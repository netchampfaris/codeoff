from datetime import timedelta

import frappe
from frappe.tests import IntegrationTestCase
from frappe.utils import now_datetime

from codeoff.code_off.tests.utils import cleanup_test_data, create_live_match, create_players


class TestCodeoffSubmissionValidation(IntegrationTestCase):
	"""Tests for submission validation rules."""

	def setUp(self):
		cleanup_test_data()

	def tearDown(self):
		cleanup_test_data()

	def _setup_live_match_with_outsider(self):
		match, players, problem = create_live_match(player_prefix="subtest")

		email = "outsider@codeoff.test"
		if not frappe.db.exists("User", email):
			frappe.get_doc(
				{
					"doctype": "User",
					"email": email,
					"first_name": "Outsider",
					"send_welcome_email": 0,
				}
			).insert(ignore_permissions=True)
		outsider = frappe.get_doc({"doctype": "Codeoff Player", "user": email, "is_active": 1}).insert(
			ignore_permissions=True
		)

		return match, players, outsider, problem

	def test_submission_rejected_for_non_participant(self):
		"""Outsider cannot submit to a match they're not in."""
		match, players, outsider, _ = self._setup_live_match_with_outsider()

		with self.assertRaises(frappe.ValidationError):
			frappe.get_doc(
				{
					"doctype": "Codeoff Submission",
					"match": match.name,
					"player": outsider.name,
					"problem": match.problem,
					"source_code": "def add(a, b): return 0",
				}
			).insert(ignore_permissions=True)

	def test_submission_rejected_for_non_live_match(self):
		"""Submission rejected if match is not Live."""
		match, players, _, _ = self._setup_live_match_with_outsider()

		match.status = "Finished"
		match.flags.ignore_validate = True
		match.save()

		with self.assertRaises(frappe.ValidationError):
			frappe.get_doc(
				{
					"doctype": "Codeoff Submission",
					"match": match.name,
					"player": players[0].name,
					"problem": match.problem,
					"source_code": "def add(a, b): return 0",
				}
			).insert(ignore_permissions=True)

	def test_submission_rejected_after_deadline(self):
		"""Submission rejected after match deadline has passed."""
		match, players, _, _ = self._setup_live_match_with_outsider()

		match.deadline = now_datetime() - timedelta(seconds=60)
		match.flags.ignore_validate = True
		match.save()

		with self.assertRaises(frappe.ValidationError):
			frappe.get_doc(
				{
					"doctype": "Codeoff Submission",
					"match": match.name,
					"player": players[0].name,
					"problem": match.problem,
					"source_code": "def add(a, b): return 0",
				}
			).insert(ignore_permissions=True)

	def test_valid_submission_accepted(self):
		"""Valid submission from a match participant is accepted."""
		match, players, _, _ = self._setup_live_match_with_outsider()

		sub = frappe.get_doc(
			{
				"doctype": "Codeoff Submission",
				"match": match.name,
				"player": players[0].name,
				"problem": match.problem,
				"source_code": "def add(a, b): return a + b",
			}
		).insert(ignore_permissions=True)

		self.assertEqual(sub.status, "Queued")
		self.assertEqual(sub.language, "python")
		self.assertIsNotNone(sub.submitted_at)
