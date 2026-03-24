# Copyright (c) 2026, Code Off and contributors
# For license information, please see license.txt

"""
API methods for contestant and spectator interactions.
"""

import json

import frappe
from frappe.utils import now_datetime


@frappe.whitelist()
def submit_code(match_id, source_code):
	"""Submit code for official judging."""
	player = _get_current_player()
	match = frappe.get_doc("Codeoff Match", match_id)

	submission = frappe.new_doc("Codeoff Submission")
	submission.match = match_id
	submission.player = player.name
	submission.problem = match.problem
	submission.source_code = source_code
	submission.insert()
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
		"codeoff.code_off.services.judge.judge_submission",
		submission_id=submission.name,
		enqueue_after_commit=True,
	)

	return {"submission_id": submission.name, "status": "Queued"}


@frappe.whitelist()
def run_sample_tests(match_id, source_code):
	"""Run code against sample test cases only. Ephemeral — no record created."""
	player = _get_current_player()
	match = frappe.get_doc("Codeoff Match", match_id)

	if match.status != "Live":
		frappe.throw("Match is not live")

	if player.name not in (match.player_1, match.player_2):
		frappe.throw("You are not a participant in this match")

	from codeoff.code_off.services.judge import run_sample_tests as _run_sample_tests

	results = _run_sample_tests(source_code, match.problem)
	return results


@frappe.whitelist()
def update_draft(match_id, source_code, cursor_line=0, cursor_column=0):
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


@frappe.whitelist(allow_guest=True)
def get_match_state(match_id):
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

	player_1_name = (
		frappe.db.get_value("Codeoff Player", match.player_1, "player_name") if match.player_1 else None
	)
	player_2_name = (
		frappe.db.get_value("Codeoff Player", match.player_2, "player_name") if match.player_2 else None
	)

	return {
		"match_id": match.name,
		"status": match.status,
		"start_time": str(match.start_time) if match.start_time else None,
		"deadline": str(match.deadline) if match.deadline else None,
		"player_1": {"id": match.player_1, "name": player_1_name},
		"player_2": {"id": match.player_2, "name": player_2_name},
		"winner": match.winner,
		"winning_reason": match.winning_reason,
		"drafts": drafts,
	}


@frappe.whitelist()
def get_my_match():
	"""Get the current player's active match (for lobby/redirect)."""
	player = _get_current_player()

	# Find a live or ready match for this player
	match_name = frappe.db.get_value(
		"Codeoff Match",
		{
			"status": ("in", ["Ready", "Live"]),
			"player_1": player.name,
		},
		"name",
	) or frappe.db.get_value(
		"Codeoff Match",
		{
			"status": ("in", ["Ready", "Live"]),
			"player_2": player.name,
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


def _get_current_player():
	"""Get the Codeoff Player for the currently logged-in user."""
	user = frappe.session.user
	player_name = frappe.db.get_value("Codeoff Player", {"user": user}, "name")
	if not player_name:
		frappe.throw("No player profile found for your account")
	return frappe.get_doc("Codeoff Player", player_name)
