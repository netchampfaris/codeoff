# Copyright (c) 2026, Code Off and contributors
# For license information, please see license.txt

"""
API methods for contestant and spectator interactions.
"""

import json
import uuid

import frappe
from frappe.utils import now_datetime

ALLOWED_REACTIONS = ["🔥", "💀", "👀", "🎉", "😬"]
AUDIENCE_CHANNEL = "codeoff_audience"
AUDIENCE_KEY_PREFIX = "codeoff_presence:global:"
AUDIENCE_TTL_SECONDS = 45
AUDIENCE_LAST_COUNT_KEY = "codeoff_audience:last_count"


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

	# Broadcast updated match state
	publish_match_state(match_id)

	# Enqueue or run synchronously based on tournament setting
	tournament = frappe.db.get_value("Codeoff Match", match_id, "tournament")
	sync_judging = frappe.db.get_value("Codeoff Tournament", tournament, "sync_judging")

	if sync_judging:
		from codeoff.services.judge import judge_submission

		judge_submission(submission.name)
		return {"submission_id": submission.name, "status": "Completed"}

	# enqueue_after_commit ensures the submission row is visible to the worker
	frappe.enqueue(
		"codeoff.services.judge.judge_submission",
		submission_id=submission.name,
		at_front=True,
		enqueue_after_commit=True,
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

	# Validate player belongs to this match
	match_players = frappe.db.get_value("Codeoff Match", match_id, ["player_1", "player_2"], as_dict=True)
	if not match_players or player.name not in (match_players.player_1, match_players.player_2):
		frappe.throw("You are not a participant in this match")

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

	_broadcast_match_event(match_id, {"event_type": "draft_updated", **draft_data})


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

	# Broadcast updated match state
	publish_match_state(match_id)

	# Return fresh status
	match.reload()
	return {"status": match.status}


@frappe.whitelist()
def start_match_now(match_id: str):
	"""Organizer-only: start a Ready match manually."""
	match = _get_organizer_match(match_id)
	if match.status != "Ready":
		frappe.throw("Match is not in Ready status")
	match.start_match()
	return {"status": "Live"}


@frappe.whitelist()
def make_match_ready(match_id: str):
	"""Organizer-only: force a Draft match to Ready status."""
	match = _get_organizer_match(match_id)
	if match.status != "Draft":
		frappe.throw("Match is not in Draft status")
	frappe.db.set_value("Codeoff Match", match_id, "status", "Ready")
	frappe.db.commit()
	return {"status": "Ready"}


@frappe.whitelist()
def organizer_add_match_time(match_id: str, seconds: int):
	"""Organizer-only: extend a live match deadline."""
	match = _get_organizer_match(match_id)
	match.add_time(seconds)
	match.reload()
	return {"status": match.status, "deadline": match.deadline}


@frappe.whitelist()
def organizer_resolve_match(match_id: str):
	"""Organizer-only: resolve a live match immediately."""
	match = _get_organizer_match(match_id)
	match.resolve_now()
	match.reload()
	return {"status": match.status, "winner": match.winner, "winning_reason": match.winning_reason}


@frappe.whitelist()
def organizer_force_finish_match(match_id: str, winner_player: str):
	"""Organizer-only: manually set the winner of a live/review match."""
	match = _get_organizer_match(match_id)
	match.force_finish(winner_player)
	match.reload()
	return {"status": match.status, "winner": match.winner, "winning_reason": match.winning_reason}


@frappe.whitelist()
def organizer_reset_match(match_id: str):
	"""Organizer-only: reset a match and clear submissions."""
	match = _get_organizer_match(match_id)
	match.reset_match()
	match.reload()
	return {"status": match.status}


@frappe.whitelist()
def organizer_create_rematch(match_id: str):
	"""Organizer-only: create a rematch for a review match."""
	match = _get_organizer_match(match_id)
	result = match.create_rematch()
	return result


@frappe.whitelist(allow_guest=True)
def heartbeat_audience(viewer_token: str):
	"""Register or refresh a spectator presence heartbeat and return the latest count."""
	viewer_token = _normalize_viewer_token(viewer_token)
	if not viewer_token:
		frappe.throw("Invalid viewer token")

	cache_key = _audience_presence_key(viewer_token)
	frappe.cache.set_value(
		cache_key,
		{
			"viewer_token": viewer_token,
			"updated_at": str(now_datetime()),
		},
		expires_in_sec=AUDIENCE_TTL_SECONDS,
	)

	audience_total = _get_audience_total()
	_publish_audience_count(audience_total)
	return {
		"audience_total": audience_total,
		"updated_at": str(now_datetime()),
	}


@frappe.whitelist(allow_guest=True)
def leave_audience(viewer_token: str):
	"""Remove a spectator presence entry when leaving eligible Codeoff pages."""
	viewer_token = _normalize_viewer_token(viewer_token)
	if not viewer_token:
		return {"audience_total": _get_audience_total(), "updated_at": str(now_datetime())}

	frappe.cache.delete_value(_audience_presence_key(viewer_token))
	audience_total = _get_audience_total()
	_publish_audience_count(audience_total, force=True)
	return {
		"audience_total": audience_total,
		"updated_at": str(now_datetime()),
	}


@frappe.whitelist(allow_guest=True)
def get_audience_count():
	"""Return the latest global Codeoff audience count."""
	return {
		"audience_total": _get_audience_total(),
		"updated_at": str(now_datetime()),
	}


@frappe.whitelist(allow_guest=True)
def vote_for_player(match_id: str, player_id: str):
	"""Cast a spectator crowd pick for a player while the match is Ready."""
	match = frappe.db.get_value(
		"Codeoff Match",
		match_id,
		["status", "player_1", "player_2", "votes_player_1", "votes_player_2"],
		as_dict=True,
	)
	if not match:
		frappe.throw("Match not found")
	if match.status != "Ready":
		frappe.throw("Voting is only open while the match is in the lobby")
	if player_id not in (match.player_1, match.player_2):
		frappe.throw("Invalid player for this match")

	if player_id == match.player_1:
		frappe.db.sql(
			"UPDATE `tabCodeoff Match` SET `votes_player_1` = COALESCE(`votes_player_1`, 0) + 1 WHERE name = %s",
			(match_id,),
		)
	else:
		frappe.db.sql(
			"UPDATE `tabCodeoff Match` SET `votes_player_2` = COALESCE(`votes_player_2`, 0) + 1 WHERE name = %s",
			(match_id,),
		)

	updated = frappe.db.get_value(
		"Codeoff Match", match_id, ["votes_player_1", "votes_player_2"], as_dict=True
	)
	votes_1 = updated.votes_player_1 or 0
	votes_2 = updated.votes_player_2 or 0
	_broadcast_match_event(
		match_id,
		{
			"event_type": "vote_update",
			"votes_1": votes_1,
			"votes_2": votes_2,
		},
	)
	return {"votes_1": votes_1, "votes_2": votes_2}


@frappe.whitelist(allow_guest=True)
def send_reaction(match_id: str, emoji: str, player_id: str | None = None, client_id: str | None = None):
	"""Broadcast an ephemeral emoji reaction to all spectators."""
	if emoji not in ALLOWED_REACTIONS:
		frappe.throw("Invalid reaction")
	# Sanitize client_id — it's echoed back for dedup; reject oversized values
	if client_id and len(str(client_id)) > 128:
		client_id = None
	# Validate player_id belongs to this match if provided
	if player_id:
		players = frappe.db.get_value("Codeoff Match", match_id, ["player_1", "player_2"], as_dict=True)
		if not players or player_id not in (players.player_1, players.player_2):
			player_id = None
	_broadcast_match_event(
		match_id,
		{
			"event_type": "reaction",
			"emoji": emoji,
			"player_id": player_id,
			"client_id": client_id,
			"id": str(uuid.uuid4()),
		},
	)
	return {"ok": True}


@frappe.whitelist(allow_guest=True)
def get_match_state(match_id: str):
	"""Get current match state for spectator or contestant. Public API."""
	return _build_match_state(match_id)


def publish_match_state(match_id: str):
	"""Build full match state and broadcast it via realtime."""
	state = _build_match_state(match_id)
	state["event_type"] = "match_state"
	_broadcast_match_event(match_id, state)


def _broadcast_match_event(match_id: str, message: dict):
	"""Broadcast to room 'all' (spectators/organizer) + each player's user room (Website Users)."""
	event = f"codeoff_match_{match_id}"
	frappe.publish_realtime(event, message)
	players = frappe.db.get_value("Codeoff Match", match_id, ["player_1", "player_2"], as_dict=True)
	for player_field in ("player_1", "player_2"):
		player_id = players.get(player_field)
		if player_id:
			user = frappe.db.get_value("Codeoff Player", player_id, "user")
			if user:
				frappe.publish_realtime(event, message, user=user)


def _audience_presence_key(viewer_token: str) -> str:
	return f"{AUDIENCE_KEY_PREFIX}{viewer_token}"


def _normalize_viewer_token(viewer_token: str | None) -> str:
	viewer_token = (viewer_token or "").strip()
	if not viewer_token or len(viewer_token) > 128:
		return ""
	allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_")
	return viewer_token if all(char in allowed for char in viewer_token) else ""


def _get_audience_total() -> int:
	return len(frappe.cache.get_keys(AUDIENCE_KEY_PREFIX))


def _publish_audience_count(audience_total: int, force: bool = False):
	previous_total = frappe.cache.get_value(AUDIENCE_LAST_COUNT_KEY)
	if not force and previous_total == audience_total:
		return

	frappe.cache.set_value(AUDIENCE_LAST_COUNT_KEY, audience_total, expires_in_sec=AUDIENCE_TTL_SECONDS)
	frappe.publish_realtime(
		AUDIENCE_CHANNEL,
		{
			"event_type": "audience_count_updated",
			"audience_total": audience_total,
			"updated_at": str(now_datetime()),
		},
	)


def _build_match_state(match_id: str):
	"""Internal: build the full match state dict."""
	match = frappe.get_doc("Codeoff Match", match_id)
	match = _refresh_expired_match(match)

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
		active_cases = [tc for tc in problem.test_cases if tc.is_active]
		sample_cases = [
			{"input": tc.input_data, "expected_output": tc.expected_output}
			for tc in active_cases
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
			"total_test_cases": len(active_cases),
		}

	votes_1 = match.votes_player_1 or 0
	votes_2 = match.votes_player_2 or 0

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

	is_organizer = "System Manager" in frappe.get_roles()

	# Expose dev-login flag so the spectate UI can show the player-switcher
	enable_dev_login = False
	if match.tournament:
		enable_dev_login = bool(
			frappe.db.get_value("Codeoff Tournament", match.tournament, "enable_dev_login")
		)

	return {
		"match_id": match.name,
		"status": match.status,
		"is_organizer": is_organizer,
		"enable_dev_login": enable_dev_login,
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
		"round_number": match.round_number,
		"bracket_position": match.bracket_position,
		"drafts": drafts,
		"problem": problem_data,
		"submissions": submissions,
		"votes_1": votes_1,
		"votes_2": votes_2,
	}


def _get_organizer_match(match_id: str):
	"""Ensure the caller is an organizer before mutating match state."""
	if "System Manager" not in frappe.get_roles():
		frappe.throw("Only organizers can manage matches", frappe.PermissionError)
	return frappe.get_doc("Codeoff Match", match_id)


def _refresh_expired_match(match):
	"""Resolve overdue live matches during state reads if the queue hasn't caught up yet."""
	if match.status != "Live" or not match.deadline or match.winner:
		return match

	if match.deadline > now_datetime():
		return match

	from codeoff.services.match_engine import resolve_match_timeout

	resolve_match_timeout(match.name)
	match.reload()
	return match


@frappe.whitelist(allow_guest=True)
def get_my_match():
	"""Get the current player's active match (for lobby/redirect)."""
	user = frappe.session.user
	if user == "Guest":
		return {"match_id": None, "status": "not_a_player"}

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


@frappe.whitelist(allow_guest=True)
def get_live_matches():
	"""Return Live and Ready matches for the spectate lobby. Public API."""
	is_organizer = "System Manager" in frappe.get_roles()
	matches = frappe.get_all(
		"Codeoff Match",
		filters={"status": ("in", ["Ready", "Live"])},
		fields=[
			"name",
			"status",
			"tournament",
			"player_1",
			"player_2",
			"problem",
			"round_number",
			"bracket_position",
			"votes_player_1",
			"votes_player_2",
		],
		order_by="round_number asc, bracket_position asc",
	)
	# Batch-fetch player names and problem titles to avoid N+1 queries
	player_ids = {m[f] for m in matches for f in ("player_1", "player_2") if m.get(f)}
	problem_ids = {m["problem"] for m in matches if m.get("problem")}
	player_name_map = (
		{
			p.name: p.player_name
			for p in frappe.get_all(
				"Codeoff Player",
				filters={"name": ["in", list(player_ids)]},
				fields=["name", "player_name"],
			)
		}
		if player_ids
		else {}
	)
	problem_title_map = (
		{
			p.name: p.title
			for p in frappe.get_all(
				"Codeoff Problem",
				filters={"name": ["in", list(problem_ids)]},
				fields=["name", "title"],
			)
		}
		if problem_ids
		else {}
	)
	for m in matches:
		for field in ("player_1", "player_2"):
			if m[field]:
				m[f"{field}_name"] = player_name_map.get(m[field])
		if m["problem"]:
			m["problem_title"] = problem_title_map.get(m["problem"])
		m["votes_1"] = m.get("votes_player_1") or 0
		m["votes_2"] = m.get("votes_player_2") or 0
		m["is_organizer"] = is_organizer
	return matches


@frappe.whitelist()
def get_active_matches():
	"""Get all active (Live/Ready) matches. For organizer dashboard."""
	matches = frappe.get_all(
		"Codeoff Match",
		filters={"status": ("in", ["Ready", "Live"])},
		fields=["name", "status", "tournament", "player_1", "player_2", "problem", "start_time", "deadline"],
		order_by="creation asc",
	)
	player_ids = {m[f] for m in matches for f in ("player_1", "player_2") if m.get(f)}
	player_name_map = (
		{
			p.name: p.player_name
			for p in frappe.get_all(
				"Codeoff Player",
				filters={"name": ["in", list(player_ids)]},
				fields=["name", "player_name"],
			)
		}
		if player_ids
		else {}
	)
	for m in matches:
		for field in ("player_1", "player_2"):
			if m[field]:
				m[f"{field}_name"] = player_name_map.get(m[field])
	return matches


@frappe.whitelist(allow_guest=True)
def get_tournament_bracket():
	"""Get tournament bracket data for display."""
	tournament = frappe.get_all(
		"Codeoff Tournament",
		fields=["name", "tournament_name", "status", "current_round", "enable_dev_login"],
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
			"deadline",
			"best_score_player_1",
			"best_score_player_2",
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

	is_organizer = "System Manager" in frappe.get_roles()

	return {
		"tournament_name": t.tournament_name,
		"tournament_id": t.name,
		"status": t.status,
		"current_round": t.current_round,
		"enable_dev_login": bool(t.enable_dev_login),
		"is_organizer": is_organizer,
		"total_rounds": total_rounds,
		"rounds": rounds,
	}


@frappe.whitelist(allow_guest=True)
def get_all_players():
	"""Return all Codeoff Players (for dev login-as dropdown). Only available in
	developer mode — used by the player-switcher shown when enable_dev_login is set."""
	if not frappe.conf.developer_mode:
		frappe.throw("This API is only available in developer mode", frappe.PermissionError)
	return frappe.get_all(
		"Codeoff Player",
		fields=["name", "player_name", "user"],
		order_by="player_name asc",
	)


def _get_current_player():
	"""Get the Codeoff Player for the currently logged-in user."""
	user = frappe.session.user
	player_name = frappe.db.get_value("Codeoff Player", {"user": user}, "name")
	if not player_name:
		frappe.throw("No player profile found for your account")
	return frappe.get_doc("Codeoff Player", player_name)
