# Copyright (c) 2026, Code Off and contributors
# For license information, please see license.txt

"""
API methods for contestant and spectator interactions.
"""

import json

import frappe
from frappe.utils import now_datetime


@frappe.whitelist()
def submit_code(match_id: str, source_code: str):
	"""Submit code for official judging."""
	player = _get_current_player()
	match = frappe.get_doc("Codeoff Match", match_id)

	submission = frappe.new_doc("Codeoff Submission")
	submission.match = match_id
	submission.player = player.name
	submission.problem = match.problem
	submission.source_code = source_code
	submission.insert(ignore_permissions=True)
	frappe.db.commit()

	# Publish submission received event
	frappe.publish_realtime(
		f"codeoff_match_{match_id}",
		{
			"event_type": "submission_received",
			"match_id": match_id,
			"submission_id": submission.name,
			"player_id": player.name,
			"submitted_at": str(submission.submitted_at),
			"status": "Queued",
		},
	)

	# Enqueue judging
	frappe.enqueue(
		"codeoff.services.judge.judge_submission",
		submission_id=submission.name,
		at_front=True,
	)

	return {"submission_id": submission.name, "status": "Queued"}


@frappe.whitelist()
def run_sample_tests(match_id: str, source_code: str):
	"""Run code against sample test cases only. Ephemeral — no record created."""
	player = _get_current_player()
	match = frappe.get_doc("Codeoff Match", match_id)

	if match.status != "Live":
		frappe.throw("Match is not live")

	if player.name not in (match.player_1, match.player_2):
		frappe.throw("You are not a participant in this match")

	from codeoff.services.judge import run_sample_tests as _run_sample_tests

	results = _run_sample_tests(source_code, match.problem)
	return results


@frappe.whitelist()
def update_draft(match_id: str, source_code: str, cursor_line: int = 0, cursor_column: int = 0):
	"""Update draft state in Redis and broadcast to spectators."""
	player = _get_current_player()

	# Store in Redis
	draft_data = {
		"match_id": match_id,
		"player_id": player.name,
		"language": "python",
		"source_code": source_code,
		"cursor_line": int(cursor_line),
		"cursor_column": int(cursor_column),
		"updated_at": str(now_datetime()),
	}
	cache_key = f"codeoff_draft:{match_id}:{player.name}"
	frappe.cache.set_value(cache_key, frappe.as_json(draft_data))

	# Broadcast to spectators
	frappe.publish_realtime(
		f"codeoff_match_{match_id}",
		{
			"event_type": "draft_updated",
			**draft_data,
		},
	)


@frappe.whitelist()
def join_match(match_id: str):
	"""Player joins the match lobby. When both players join, the match starts."""
	player = _get_current_player()
	match = frappe.get_doc("Codeoff Match", match_id)

	if match.status not in ("Ready", "Live"):
		frappe.throw("Match is not available to join")

	# Determine which slot this player is in
	if match.player_1 == player.name:
		slot = "player_1"
	elif match.player_2 == player.name:
		slot = "player_2"
	else:
		frappe.throw("You are not a player in this match")

	# Already joined?
	if match.get(f"{slot}_joined"):
		return {"status": match.status, "already_joined": True}

	# Use atomic set_value to avoid race condition where concurrent joins
	# overwrite each other's flags via full document save
	frappe.db.set_value("Codeoff Match", match_id, f"{slot}_joined", 1)
	frappe.db.commit()

	# Notify spectators & the other player
	frappe.publish_realtime(
		f"codeoff_match_{match_id}",
		{
			"event_type": "player_joined",
			"match_id": match_id,
			"player_id": player.name,
			"slot": slot,
		},
	)

	# If both players have joined, start the match
	match.reload()
	if match.player_1_joined and match.player_2_joined and match.status == "Ready":
		match.start_match()
		frappe.db.commit()

	# Return fresh status after potential start
	return {"status": match.status}


@frappe.whitelist(allow_guest=True)
def get_match_state(match_id: str):
	"""Get current match state for spectator or contestant. Public API."""
	match = frappe.get_doc("Codeoff Match", match_id)

	# Get draft states from Redis
	drafts = {}
	for player_field in ("player_1", "player_2"):
		player_id = getattr(match, player_field)
		if player_id:
			cache_key = f"codeoff_draft:{match_id}:{player_id}"
			draft_json = frappe.cache.get_value(cache_key)
			if draft_json:
				drafts[player_id] = json.loads(draft_json) if isinstance(draft_json, str) else draft_json

	player_1_name = None
	player_1_user = None
	if match.player_1:
		p1 = frappe.db.get_value("Codeoff Player", match.player_1, ["player_name", "user"], as_dict=True)
		if p1:
			player_1_name = p1.player_name
			player_1_user = p1.user

	player_2_name = None
	player_2_user = None
	if match.player_2:
		p2 = frappe.db.get_value("Codeoff Player", match.player_2, ["player_name", "user"], as_dict=True)
		if p2:
			player_2_name = p2.player_name
			player_2_user = p2.user

	# Get problem details
	problem_data = None
	if match.problem:
		problem = frappe.get_doc("Codeoff Problem", match.problem)
		sample_cases = [
			{"input": tc.input_data, "expected_output": tc.expected_output}
			for tc in problem.test_cases
			if tc.visibility == "Sample"
		]
		problem_data = {
			"name": problem.name,
			"title": problem.title,
			"statement": problem.statement,
			"constraints_text": problem.constraints_text,
			"function_name": problem.function_name,
			"function_signature": problem.function_signature,
			"starter_code": problem.starter_code,
			"sample_test_cases": sample_cases,
		}

	# Get submissions
	submissions = frappe.get_all(
		"Codeoff Submission",
		filters={"match": match_id},
		fields=[
			"name",
			"player",
			"status",
			"verdict",
			"passed_tests",
			"total_tests",
			"score",
			"submitted_at",
		],
		order_by="submitted_at asc",
		ignore_permissions=True,
	)

	return {
		"match_id": match.name,
		"status": match.status,
		"start_time": str(match.start_time) if match.start_time else None,
		"deadline": str(match.deadline) if match.deadline else None,
		"player_1": {
			"id": match.player_1,
			"name": player_1_name,
			"user": player_1_user,
			"joined": bool(match.player_1_joined),
		},
		"player_2": {
			"id": match.player_2,
			"name": player_2_name,
			"user": player_2_user,
			"joined": bool(match.player_2_joined),
		},
		"winner": match.winner,
		"winning_reason": match.winning_reason,
		"drafts": drafts,
		"problem": problem_data,
		"submissions": submissions,
	}


@frappe.whitelist()
def get_my_match():
	"""Get the current player's active match (for lobby/redirect)."""
	user = frappe.session.user
	player_name = frappe.db.get_value("Codeoff Player", {"user": user}, "name")
	if not player_name:
		return {"match_id": None, "status": "not_a_player"}

	# Find a live or ready match for this player
	match_name = frappe.db.get_value(
		"Codeoff Match",
		{
			"status": ("in", ["Ready", "Live"]),
			"player_1": player_name,
		},
		"name",
	) or frappe.db.get_value(
		"Codeoff Match",
		{
			"status": ("in", ["Ready", "Live"]),
			"player_2": player_name,
		},
		"name",
	)

	if not match_name:
		return {"match_id": None, "status": "no_active_match"}

	match = frappe.get_doc("Codeoff Match", match_name)
	return {
		"match_id": match.name,
		"status": match.status,
		"tournament": match.tournament,
	}


@frappe.whitelist()
def get_active_matches():
	"""Get all active (Live/Ready) matches. For organizer dashboard."""
	matches = frappe.get_all(
		"Codeoff Match",
		filters={"status": ("in", ["Ready", "Live"])},
		fields=["name", "status", "tournament", "player_1", "player_2", "problem", "start_time", "deadline"],
		order_by="creation asc",
	)
	for m in matches:
		for field in ("player_1", "player_2"):
			if m[field]:
				m[f"{field}_name"] = frappe.db.get_value("Codeoff Player", m[field], "player_name")
	return matches


@frappe.whitelist()
def get_tournament_bracket():
	"""Get tournament bracket data for display."""
	tournament = frappe.get_all(
		"Codeoff Tournament",
		fields=["name", "tournament_name", "status", "current_round"],
		order_by="creation desc",
		limit=1,
		ignore_permissions=True,
	)
	if not tournament:
		return None

	t = tournament[0]
	matches = frappe.get_all(
		"Codeoff Match",
		filters={"tournament": t.name},
		fields=[
			"name",
			"round_number",
			"bracket_position",
			"status",
			"player_1",
			"player_2",
			"winner",
		],
		order_by="round_number asc, bracket_position asc",
		ignore_permissions=True,
	)

	# Resolve player names
	player_cache = {}
	for m in matches:
		for field in ("player_1", "player_2", "winner"):
			pid = m.get(field)
			if pid and pid not in player_cache:
				player_cache[pid] = frappe.db.get_value("Codeoff Player", pid, "player_name") or pid
			m[f"{field}_name"] = player_cache.get(pid) if pid else None

	# Group by round
	rounds = {}
	for m in matches:
		r = m["round_number"]
		rounds.setdefault(r, []).append(m)

	total_rounds = max(rounds.keys()) if rounds else 0

	return {
		"tournament_name": t.tournament_name,
		"tournament_id": t.name,
		"status": t.status,
		"current_round": t.current_round,
		"total_rounds": total_rounds,
		"rounds": rounds,
	}


def _get_current_player():
	"""Get the Codeoff Player for the currently logged-in user."""
	user = frappe.session.user
	player_name = frappe.db.get_value("Codeoff Player", {"user": user}, "name")
	if not player_name:
		frappe.throw("No player profile found for your account")
	return frappe.get_doc("Codeoff Player", player_name)
