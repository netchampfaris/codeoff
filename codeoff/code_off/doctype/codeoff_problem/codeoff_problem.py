# Copyright (c) 2026, Code Off and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class CodeoffProblem(Document):
	def before_save(self):
		if not self.slug:
			self.slug = frappe.scrub(self.title).replace("_", "-")
		if not self.starter_code and self.function_signature:
			self.starter_code = f"{self.function_signature}\n\tpass"
