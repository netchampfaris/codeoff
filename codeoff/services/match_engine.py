# Copyright (c) 2026, Code Off and contributors
# For license information, please see license.txt

"""
Match engine: handles match lifecycle, scoring, winner determination, and bracket advancement.
"""

import frappe
from frappe.utils import now_datetime


def resolve_match_timeout(match_id):
	"""Called by background job when match deadline is reached."""
	match = frappe.get_doc("Codeoff Match", match_id)

	if match.status != "Live":
		return

	# Check if someone already won (accepted submission during match)
	if match.winner:
		return

	recompute_scores(match)
	determine_winner_by_score(match)


def recompute_scores(match):
	"""Recompute best scores and wrong submission counts from all submissions."""
	submissions = frappe.get_all(
		"Codeoff Submission",
		filters={"match": match.name, "status": "Completed"},
		fields=["player", "verdict", "passed_tests", "submitted_at"],
	)

	best_score = {match.player_1: 0, match.player_2: 0}
	wrong_count = {match.player_1: 0, match.player_2: 0}

	for sub in submissions:
		player = sub.player
		if player not in best_score:
			continue

		if sub.verdict != "Accepted" and sub.verdict:
			wrong_count[player] += 1

		if (sub.passed_tests or 0) > best_score[player]:
			best_score[player] = sub.passed_tests or 0

	match.best_score_player_1 = best_score.get(match.player_1, 0)
	match.best_score_player_2 = best_score.get(match.player_2, 0)
	match.wrong_submissions_player_1 = wrong_count.get(match.player_1, 0)
	match.wrong_submissions_player_2 = wrong_count.get(match.player_2, 0)


def determine_winner_by_score(match):
	"""Apply tie-break rules when no accepted submission exists."""
	s1 = match.best_score_player_1 or 0
	s2 = match.best_score_player_2 or 0
	w1 = match.wrong_submissions_player_1 or 0
	w2 = match.wrong_submissions_player_2 or 0

	# Nobody scored anything — it's a draw
	if s1 == 0 and s2 == 0:
		draw_match(match)
		return

	if s1 > s2:
		finalize_match(match, match.player_1, "Best Score")
	elif s2 > s1:
		finalize_match(match, match.player_2, "Best Score")
	elif w1 < w2:
		finalize_match(match, match.player_1, "Best Score")
	elif w2 < w1:
		finalize_match(match, match.player_2, "Best Score")
	else:
		# Both had partial progress but equal — require organizer follow-up.
		_mark_match_for_review(match, "Equal best score and equal wrong submission count")


def draw_match(match):
	"""Neither player solved the problem — require a rematch or organizer decision."""
	_mark_match_for_review(match, "No submissions from either player")


def _mark_match_for_review(match, reason):
	"""Persist a review state for outcomes that need manual follow-up or a rematch."""
	match.status = "Review"
	match.winner = None
	match.winning_reason = "Tie Review"
	match.tie_break_metadata = frappe.as_json(
		{
			"reason": reason,
			"best_score_player_1": match.best_score_player_1 or 0,
			"best_score_player_2": match.best_score_player_2 or 0,
			"wrong_submissions_player_1": match.wrong_submissions_player_1 or 0,
			"wrong_submissions_player_2": match.wrong_submissions_player_2 or 0,
			"rematch_required": True,
		}
	)
	match.save(ignore_permissions=True)

	from codeoff.api.contest import _broadcast_match_event, publish_match_state

	frappe.db.commit()
	publish_match_state(match.name)
	_broadcast_match_event(
		match.name,
		{
			"event_type": "match_review_required",
			"match_id": match.name,
			"status": "Review",
			"reason": reason,
			"rematch_required": True,
		},
	)


def finalize_match(match, winner, reason):
	"""Mark match as finished and advance the bracket."""
	match.winner = winner
	match.winning_reason = reason
	match.status = "Finished"
	match.save(ignore_permissions=True)
	advance_bracket(match, winner)

	from codeoff.api.contest import publish_match_state

	frappe.db.commit()
	publish_match_state(match.name)


def advance_bracket(match, winner):
	"""Place the winner into the next round's match slot."""
	next_round, next_position, next_slot = match.get_next_match_position()

	next_match = frappe.db.get_value(
		"Codeoff Match",
		{"tournament": match.tournament, "round_number": next_round, "bracket_position": next_position},
		"name",
	)

	if not next_match:
		# This was the final — tournament is complete
		tournament = frappe.get_doc("Codeoff Tournament", match.tournament)
		tournament.status = "Completed"
		tournament.completed_on = now_datetime()
		tournament.save(ignore_permissions=True)

		# Mark winner in tournament player table
		for tp in tournament.players:
			if tp.player == winner:
				tp.status = "Winner"
				tp.save(ignore_permissions=True)

		return

	frappe.db.set_value("Codeoff Match", next_match, next_slot, winner)

	# Check if next match now has both players — reload to pick up the set_value above
	next_match_doc = frappe.get_doc("Codeoff Match", next_match)
	next_match_doc.reload()
	if next_match_doc.player_1 and next_match_doc.player_2:
		if next_match_doc.status == "Draft":
			# Inherit problem from the current match if none assigned yet
			if not next_match_doc.problem and match.problem:
				next_match_doc.problem = match.problem
			next_match_doc.status = "Ready"
			next_match_doc.save(ignore_permissions=True)


def process_verdict(submission_id):
	"""Called after judge returns a verdict. Updates match state and checks for winner."""
	submission = frappe.get_doc("Codeoff Submission", submission_id)
	match = frappe.get_doc("Codeoff Match", submission.match)

	# Lock the match row to prevent race conditions
	frappe.db.sql("SELECT name FROM `tabCodeoff Match` WHERE name=%s FOR UPDATE", match.name)

	# Reload after lock to get latest state
	match.reload()

	if match.status != "Live":
		return

	# Check for immediate win
	if submission.verdict == "Accepted":
		# Check if another accepted submission already exists
		existing_accepted = frappe.db.exists(
			"Codeoff Submission",
			{
				"match": match.name,
				"verdict": "Accepted",
				"name": ("!=", submission.name),
			},
		)

		if existing_accepted:
			# Both accepted — earlier submitted_at wins
			other = frappe.get_doc("Codeoff Submission", existing_accepted)
			if submission.submitted_at <= other.submitted_at:
				winner = submission.player
			else:
				winner = other.player
		else:
			winner = submission.player

		recompute_scores(match)
		finalize_match(match, winner, "First Accepted")
	else:
		# Update scores but don't finalize
		recompute_scores(match)
		match.save(ignore_permissions=True)

		from codeoff.api.contest import publish_match_state

		frappe.db.commit()
		publish_match_state(match.name)
