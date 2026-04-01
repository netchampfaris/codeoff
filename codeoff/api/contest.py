# Copyright (c) 2026, Code Off and contributors
# For license information, please see license.txt

"""
Non-DocType API endpoints: audience presence, live match listings, and tournament bracket.
Doc-scoped match actions (submit_code, join_match, vote_for_player, etc.) live as
@frappe.whitelist() methods on the Codeoff Match controller.
"""

import json

import frappe
from frappe.utils import now_datetime

AUDIENCE_CHANNEL = "codeoff_audience"
AUDIENCE_KEY_PREFIX = "codeoff_presence:global:"
AUDIENCE_TTL_SECONDS = 45
AUDIENCE_LAST_COUNT_KEY = "codeoff_audience:last_count"


@frappe.whitelist(allow_guest=True, methods=["POST"])
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


@frappe.whitelist(allow_guest=True, methods=["POST"])
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


@frappe.whitelist(allow_guest=True, methods=["GET"])
def get_audience_count():
	"""Return the latest global Codeoff audience count."""
	return {
		"audience_total": _get_audience_total(),
		"updated_at": str(now_datetime()),
	}


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


@frappe.whitelist(allow_guest=True, methods=["GET"])
def get_my_match():
	"""Get the current player's active match (for lobby/redirect)."""
	user = frappe.session.user
	if user == "Guest":
		return {"match_id": None, "status": "not_a_player"}

	player_name = frappe.db.get_value("Codeoff Player", {"user": user}, "name")
	if not player_name:
		return {"match_id": None, "status": "not_a_player"}

	# Find a live or ready match for this player with a single OR query
	CMatch = frappe.qb.DocType("Codeoff Match")
	rows = (
		frappe.qb.from_(CMatch)
		.select(CMatch.name)
		.where(CMatch.status.isin(["Ready", "Live"]))
		.where((CMatch.player_1 == player_name) | (CMatch.player_2 == player_name))
		.limit(1)
	).run(as_dict=True)
	match_name = rows[0].name if rows else None

	if not match_name:
		return {"match_id": None, "status": "no_active_match"}

	match = frappe.get_doc("Codeoff Match", match_name)
	return {
		"match_id": match.name,
		"status": match.status,
		"tournament": match.tournament,
	}


@frappe.whitelist(allow_guest=True, methods=["GET"])
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


@frappe.whitelist(methods=["GET"])
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


@frappe.whitelist(allow_guest=True, methods=["GET"])
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

	# Resolve player names in a single batch query
	all_player_ids = {m.get(f) for m in matches for f in ("player_1", "player_2", "winner") if m.get(f)}
	player_name_map = (
		{
			p.name: p.player_name
			for p in frappe.get_all(
				"Codeoff Player",
				filters={"name": ["in", list(all_player_ids)]},
				fields=["name", "player_name"],
			)
		}
		if all_player_ids
		else {}
	)
	for m in matches:
		for field in ("player_1", "player_2", "winner"):
			pid = m.get(field)
			m[f"{field}_name"] = player_name_map.get(pid) if pid else None

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


@frappe.whitelist(allow_guest=True, methods=["GET"])
def get_all_players():
	"""Return all Codeoff Players (for dev login-as dropdown). Guest-accessible
	because spectators are guests; only shown when enable_dev_login is set."""
	fields = ["name", "player_name"]
	t = frappe.get_all("Codeoff Tournament", fields=["enable_dev_login"], limit=1, ignore_permissions=True)
	if t and t[0].enable_dev_login:
		fields.append("user")
	return frappe.get_all("Codeoff Player", fields=fields, order_by="player_name asc")
