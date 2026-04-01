# Copyright (c) 2026, Code Off and contributors
# For license information, please see license.txt

import math
from datetime import timedelta

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime

_ALLOWED_REACTIONS = ["🔥", "💀", "👀", "🎉", "😬"]


def _get_current_player():
	"""Get the Codeoff Player for the currently logged-in user."""
	user = frappe.session.user
	player_name = frappe.db.get_value("Codeoff Player", {"user": user}, "name")
	if not player_name:
		frappe.throw("No player profile found for your account")
	return frappe.get_doc("Codeoff Player", player_name)


class CodeoffMatch(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		best_score_player_1: DF.Int
		best_score_player_2: DF.Int
		bracket_position: DF.Int
		deadline: DF.Datetime | None
		duration_seconds: DF.Int
		player_1: DF.Link | None
		player_1_joined: DF.Check
		player_2: DF.Link | None
		player_2_joined: DF.Check
		problem: DF.Link | None
		round_number: DF.Int
		start_time: DF.Datetime | None
		status: DF.Literal["Draft", "Ready", "Live", "Finished", "Review", "Cancelled"]
		tie_break_metadata: DF.JSON | None
		tournament: DF.Link
		votes_player_1: DF.Int
		votes_player_2: DF.Int
		winner: DF.Link | None
		winning_reason: DF.Literal["", "First Accepted", "Best Score", "Tie Review", "Manual Override"]
		wrong_submissions_player_1: DF.Int
		wrong_submissions_player_2: DF.Int
	# end: auto-generated types

	def validate(self):
		self.validate_players()
		if not self.is_new():
			self.update_status()

	def validate_players(self):
		if self.player_1 and self.player_2 and self.player_1 == self.player_2:
			frappe.throw("Player 1 and Player 2 must be different")

	def update_status(self):
		if self.status == "Draft" and self.player_1 and self.player_2 and self.problem:
			self.status = "Ready"

	@frappe.whitelist()
	def start_match(self):
		if "System Manager" not in frappe.get_roles():
			frappe.throw("Only organizers can start a match", frappe.PermissionError)
		if self.status != "Ready":
			frappe.throw("Match can only be started from Ready status")

		if not self.player_1 or not self.player_2:
			frappe.throw("Both players must be assigned")

		if not self.problem:
			frappe.throw("A problem must be assigned")

		tournament = frappe.get_doc("Codeoff Tournament", self.tournament)

		# Use per-round duration if configured, else fall back to tournament default
		round_entry = next(
			(r for r in tournament.round_durations if r.round_number == self.round_number),
			None,
		)
		# Priority: match-level > round-level > tournament default
		duration = (
			self.duration_seconds
			or (round_entry.duration_seconds if round_entry else None)
			or tournament.match_duration_seconds
		)

		now = now_datetime()
		self.start_time = now
		self.deadline = now + timedelta(seconds=duration)
		self.status = "Live"
		self.save(ignore_permissions=True)

		# Broadcast updated match state
		from codeoff.api.contest import publish_match_state
		from codeoff.services.match_engine import schedule_match_timeout

		publish_match_state(self.name)

		# Schedule timeout resolution
		schedule_match_timeout(self.name, duration)

	@frappe.whitelist()
	def force_finish(self, winner_player: str):
		"""Organizer override: force-finish a Live or Review match."""
		if "System Manager" not in frappe.get_roles():
			frappe.throw("Only organizers can force-finish a match", frappe.PermissionError)
		if self.status not in ("Live", "Review"):
			frappe.throw("Match must be Live or Review to force-finish")
		if self.status == "Review" and self._get_existing_rematch():
			frappe.throw("A rematch already exists for this review match")
		if winner_player not in (self.player_1, self.player_2):
			frappe.throw("Winner must be one of the match players")
		from codeoff.services.match_engine import finalize_match

		finalize_match(self, winner_player, "Manual Override")
		frappe.msgprint(f"Match finished — winner set to {winner_player}")

	def _get_tie_break_metadata(self):
		if not self.tie_break_metadata:
			return {}
		if isinstance(self.tie_break_metadata, dict):
			return dict(self.tie_break_metadata)
		return frappe.parse_json(self.tie_break_metadata) or {}

	def _get_existing_rematch(self):
		metadata = self._get_tie_break_metadata()
		rematch_id = metadata.get("rematch_match_id")
		if rematch_id and frappe.db.exists("Codeoff Match", rematch_id):
			return rematch_id
		return None

	def _pick_rematch_problem(self):
		used_problem_rows = frappe.get_all(
			"Codeoff Match",
			filters={
				"tournament": self.tournament,
				"round_number": self.round_number,
				"bracket_position": self.bracket_position,
				"player_1": self.player_1,
				"player_2": self.player_2,
			},
			fields=["problem"],
		)
		used_problem_ids = sorted({row.problem for row in used_problem_rows if row.problem})
		candidate_filters = {"name": ["not in", used_problem_ids]} if used_problem_ids else {}
		candidates = frappe.get_all(
			"Codeoff Problem",
			filters=candidate_filters,
			fields=["name"],
			order_by="creation asc",
		)
		if not candidates:
			frappe.throw("No alternate problem is available for a rematch")
		return candidates[0].name

	@frappe.whitelist()
	def create_rematch(self):
		"""Create a new ready match for the same slot using a different problem."""
		if "System Manager" not in frappe.get_roles():
			frappe.throw("Only organizers can create a rematch", frappe.PermissionError)
		if self.status != "Review":
			frappe.throw("Only review matches can create a rematch")
		if not self.player_1 or not self.player_2:
			frappe.throw("Both players must be assigned before creating a rematch")
		existing_rematch = self._get_existing_rematch()
		if existing_rematch:
			frappe.throw(f"Rematch already created: {existing_rematch}")

		rematch = frappe.new_doc("Codeoff Match")
		rematch.tournament = self.tournament
		rematch.round_number = self.round_number
		rematch.bracket_position = self.bracket_position
		rematch.player_1 = self.player_1
		rematch.player_2 = self.player_2
		rematch.problem = self._pick_rematch_problem()
		rematch.duration_seconds = self.duration_seconds
		rematch.status = "Ready"
		rematch.tie_break_metadata = frappe.as_json(
			{
				"rematch_of": self.name,
				"source_match_id": self.name,
				"original_problem": self.problem,
			}
		)
		rematch.insert(ignore_permissions=True)

		metadata = self._get_tie_break_metadata()
		metadata.update(
			{
				"rematch_required": True,
				"rematch_match_id": rematch.name,
				"rematch_problem": rematch.problem,
			}
		)
		self.tie_break_metadata = frappe.as_json(metadata)
		self.save(ignore_permissions=True)

		from codeoff.api.contest import publish_match_state

		frappe.db.commit()
		publish_match_state(self.name)
		publish_match_state(rematch.name)
		return {
			"rematch_match_id": rematch.name,
			"problem": rematch.problem,
			"status": rematch.status,
		}

	@frappe.whitelist()
	def reset_match(self):
		"""Reset this match to Ready/Draft state, deleting all submissions."""
		if "System Manager" not in frappe.get_roles():
			frappe.throw("Only organizers can reset a match", frappe.PermissionError)
		submissions = frappe.get_all("Codeoff Submission", filters={"match": self.name}, pluck="name")
		for sub in submissions:
			frappe.delete_doc("Codeoff Submission", sub, ignore_permissions=True)

		new_status = "Ready" if (self.player_1 and self.player_2 and self.problem) else "Draft"
		frappe.db.set_value(
			"Codeoff Match",
			self.name,
			{
				"status": new_status,
				"winner": None,
				"winning_reason": None,
				"start_time": None,
				"deadline": None,
				"best_score_player_1": 0,
				"best_score_player_2": 0,
				"wrong_submissions_player_1": 0,
				"wrong_submissions_player_2": 0,
				"player_1_joined": 0,
				"player_2_joined": 0,
				"tie_break_metadata": None,
				"votes_player_1": 0,
				"votes_player_2": 0,
			},
		)
		frappe.db.commit()
		frappe.msgprint(f"Match reset to {new_status}")

	@frappe.whitelist()
	def add_time(self, seconds: int):
		"""Extend the deadline of a Live match by N seconds."""
		if "System Manager" not in frappe.get_roles():
			frappe.throw("Only organizers can add time to a match", frappe.PermissionError)
		if self.status != "Live":
			frappe.throw("Match must be Live to add time")
		seconds = int(seconds)
		if seconds <= 0:
			frappe.throw("Seconds must be a positive integer")

		current_deadline = frappe.db.get_value("Codeoff Match", self.name, "deadline")
		new_deadline = current_deadline + timedelta(seconds=seconds)
		frappe.db.set_value("Codeoff Match", self.name, "deadline", new_deadline)
		frappe.db.commit()

		from codeoff.api.contest import publish_match_state

		publish_match_state(self.name)
		frappe.msgprint(f"{seconds}s added — new deadline: {new_deadline}")

	@frappe.whitelist()
	def resolve_now(self):
		"""Synchronously run match timeout resolution — use if the background job didn't fire."""
		if "System Manager" not in frappe.get_roles():
			frappe.throw("Only organizers can resolve a match manually", frappe.PermissionError)
		if self.status != "Live":
			frappe.throw("Match must be Live to resolve")
		from codeoff.services.match_engine import resolve_match_timeout

		resolve_match_timeout(self.name, force=True)
		frappe.msgprint("Match resolved")

	@frappe.whitelist(methods=["POST"])
	def submit_code(self, source_code: str):
		"""Submit code for official judging."""
		player = _get_current_player()

		if self.status != "Live":
			frappe.throw("Match is not live")
		if player.name not in (self.player_1, self.player_2):
			frappe.throw("You are not a participant in this match")

		submission = frappe.new_doc("Codeoff Submission")
		submission.match = self.name
		submission.player = player.name
		submission.problem = self.problem
		submission.source_code = source_code
		submission.insert(ignore_permissions=True)
		frappe.db.commit()

		from codeoff.api.contest import publish_match_state

		publish_match_state(self.name)

		sync_judging = frappe.db.get_value("Codeoff Tournament", self.tournament, "sync_judging")
		if sync_judging:
			from codeoff.services.judge import judge_submission

			judge_submission(submission.name)
			return {"submission_id": submission.name, "status": "Completed"}

		frappe.enqueue(
			"codeoff.services.judge.judge_submission",
			submission_id=submission.name,
			at_front=True,
		)
		return {"submission_id": submission.name, "status": "Queued"}

	@frappe.whitelist(methods=["POST"])
	def run_sample_tests(self, source_code: str):
		"""Run code against sample test cases only. Ephemeral — no record created."""
		player = _get_current_player()

		if self.status != "Live":
			frappe.throw("Match is not live")
		if player.name not in (self.player_1, self.player_2):
			frappe.throw("You are not a participant in this match")

		from codeoff.services.judge import run_sample_tests as _run_sample_tests

		return _run_sample_tests(source_code, self.problem)

	@frappe.whitelist(methods=["POST"])
	def update_draft(self, source_code: str, cursor_line: int = 0, cursor_column: int = 0):
		"""Update draft state in Redis and broadcast to spectators."""
		player = _get_current_player()

		draft_data = {
			"match_id": self.name,
			"player_id": player.name,
			"language": "python",
			"source_code": source_code,
			"cursor_line": int(cursor_line),
			"cursor_column": int(cursor_column),
			"updated_at": str(now_datetime()),
		}
		cache_key = f"codeoff_draft:{self.name}:{player.name}"
		frappe.cache.set_value(cache_key, frappe.as_json(draft_data))

		from codeoff.api.contest import _broadcast_match_event

		_broadcast_match_event(self.name, {"event_type": "draft_updated", **draft_data})

	@frappe.whitelist(methods=["POST"])
	def join_match(self):
		"""Player joins the match lobby. When both players join, the match starts."""
		player = _get_current_player()

		if self.status not in ("Ready", "Live"):
			frappe.throw("Match is not available to join")

		if self.player_1 == player.name:
			slot = "player_1"
		elif self.player_2 == player.name:
			slot = "player_2"
		else:
			frappe.throw("You are not a player in this match")

		if self.get(f"{slot}_joined"):
			return {"status": self.status, "already_joined": True}

		# Atomic set_value to avoid race condition where concurrent joins
		# overwrite each other's flags via full document save
		frappe.db.set_value("Codeoff Match", self.name, f"{slot}_joined", 1)
		frappe.db.commit()

		from codeoff.api.contest import publish_match_state

		publish_match_state(self.name)
		self.reload()
		return {"status": self.status}

	@frappe.whitelist()
	def make_match_ready(self):
		"""Organizer-only: force a Draft match to Ready status."""
		if "System Manager" not in frappe.get_roles():
			frappe.throw("Only organizers can make a match ready", frappe.PermissionError)
		if self.status != "Draft":
			frappe.throw("Match is not in Draft status")
		self.status = "Ready"
		self.save(ignore_permissions=True)
		return {"status": "Ready"}

	@frappe.whitelist(allow_guest=True, methods=["POST"])
	def vote_for_player(self, player_id: str):
		"""Cast a spectator crowd pick for a player while the match is Ready."""
		if self.status != "Ready":
			frappe.throw("Voting is only open while the match is in the lobby")
		if player_id not in (self.player_1, self.player_2):
			frappe.throw("Invalid player for this match")

		Match = frappe.qb.DocType("Codeoff Match")
		if player_id == self.player_1:
			frappe.qb.update(Match).set(Match.votes_player_1, Match.votes_player_1 + 1).where(
				Match.name == self.name
			).run()
		else:
			frappe.qb.update(Match).set(Match.votes_player_2, Match.votes_player_2 + 1).where(
				Match.name == self.name
			).run()

		updated = frappe.db.get_value(
			"Codeoff Match", self.name, ["votes_player_1", "votes_player_2"], as_dict=True
		)
		votes_1 = updated.votes_player_1 or 0
		votes_2 = updated.votes_player_2 or 0

		from codeoff.api.contest import _broadcast_match_event

		_broadcast_match_event(
			self.name, {"event_type": "vote_update", "votes_1": votes_1, "votes_2": votes_2}
		)
		return {"votes_1": votes_1, "votes_2": votes_2}

	@frappe.whitelist(allow_guest=True, methods=["POST"])
	def send_reaction(self, emoji: str, player_id: str | None = None, client_id: str | None = None):
		"""Broadcast an ephemeral emoji reaction to all spectators."""
		import uuid

		if emoji not in _ALLOWED_REACTIONS:
			frappe.throw("Invalid reaction")
		# Sanitize client_id — it's echoed back for dedup; reject oversized values
		if client_id and len(str(client_id)) > 128:
			client_id = None
		# Validate player_id belongs to this match if provided
		if player_id and player_id not in (self.player_1, self.player_2):
			player_id = None

		from codeoff.api.contest import _broadcast_match_event

		_broadcast_match_event(
			self.name,
			{
				"event_type": "reaction",
				"emoji": emoji,
				"player_id": player_id,
				"client_id": client_id,
				"id": str(uuid.uuid4()),
			},
		)
		return {"ok": True}

	@frappe.whitelist(allow_guest=True, methods=["GET"])
	def get_match_state(self):
		"""Get current match state for spectator or contestant. Public API."""
		from codeoff.api.contest import _build_match_state

		return _build_match_state(self.name)

	def get_next_match_position(self):
		"""Compute the next round match position for bracket advancement."""
		next_round = self.round_number + 1
		next_position = math.ceil(self.bracket_position / 2)
		# Odd bracket positions feed into player_1, even into player_2
		next_slot = "player_1" if self.bracket_position % 2 != 0 else "player_2"
		return next_round, next_position, next_slot
