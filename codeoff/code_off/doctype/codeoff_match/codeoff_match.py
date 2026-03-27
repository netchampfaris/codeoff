# Copyright (c) 2026, Code Off and contributors
# For license information, please see license.txt

import math
from datetime import timedelta

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime


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

		publish_match_state(self.name)

		# Schedule timeout resolution
		frappe.enqueue(
			"codeoff.services.match_engine.resolve_match_timeout",
			match_id=self.name,
			enqueue_after_commit=True,
			at_front=False,
			job_id=f"match_timeout_{self.name}",
			execute_after=duration,
		)

	@frappe.whitelist()
	def force_finish(self, winner_player: str):
		"""Organizer override: force-finish a Live or Review match."""
		if self.status not in ("Live", "Review"):
			frappe.throw("Match must be Live or Review to force-finish")
		if winner_player not in (self.player_1, self.player_2):
			frappe.throw("Winner must be one of the match players")
		from codeoff.services.match_engine import finalize_match

		finalize_match(self, winner_player, "Manual Override")
		frappe.msgprint(f"Match finished — winner set to {winner_player}")

	@frappe.whitelist()
	def reset_match(self):
		"""Reset this match to Ready/Draft state, deleting all submissions."""
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
		if self.status != "Live":
			frappe.throw("Match must be Live to resolve")
		from codeoff.services.match_engine import resolve_match_timeout

		resolve_match_timeout(self.name)
		frappe.msgprint("Match resolved")

	def get_next_match_position(self):
		"""Compute the next round match position for bracket advancement."""
		next_round = self.round_number + 1
		next_position = math.ceil(self.bracket_position / 2)
		# Odd bracket positions feed into player_1, even into player_2
		next_slot = "player_1" if self.bracket_position % 2 != 0 else "player_2"
		return next_round, next_position, next_slot
