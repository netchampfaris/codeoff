# Copyright (c) 2026, Code Off and contributors
# For license information, please see license.txt

import math
from datetime import timedelta

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime


class CodeoffMatch(Document):
	def validate(self):
		self.validate_players()
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
		duration = tournament.match_duration_seconds

		now = now_datetime()
		self.start_time = now
		self.deadline = now + timedelta(seconds=duration)
		self.status = "Live"
		self.save(ignore_permissions=True)

		frappe.publish_realtime(
			f"codeoff_match_{self.name}",
			{
				"event_type": "match_started",
				"match_id": self.name,
				"status": "Live",
				"start_time": str(self.start_time),
				"deadline": str(self.deadline),
				"duration_seconds": duration,
				"problem_id": self.problem,
			},
		)

		# Schedule timeout resolution
		frappe.enqueue(
			"codeoff.services.match_engine.resolve_match_timeout",
			match_id=self.name,
			enqueue_after_commit=True,
			at_front=False,
			job_id=f"match_timeout_{self.name}",
			execute_after=duration,
		)

	def get_next_match_position(self):
		"""Compute the next round match position for bracket advancement."""
		next_round = self.round_number + 1
		next_position = math.ceil(self.bracket_position / 2)
		next_slot = "player_1" if self.bracket_position % 2 == 1 else "player_2"
		return next_round, next_position, next_slot
