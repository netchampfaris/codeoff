# Copyright (c) 2026, Code Off and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime


class CodeoffSubmission(Document):
	def before_insert(self):
		self.submitted_at = now_datetime()
		self.language = "python"
		self.validate_match_state()

	@frappe.whitelist()
	def judge(self):
		from codeoff.services.judge import judge_submission

		judge_submission(self.name)

	def validate_match_state(self):
		match = frappe.get_doc("Codeoff Match", self.match)

		if match.status != "Live":
			frappe.throw("Submissions are only accepted for live matches")

		if self.submitted_at > match.deadline:
			frappe.throw("Match deadline has passed")

		if self.player not in (match.player_1, match.player_2):
			frappe.throw("You are not a participant in this match")
