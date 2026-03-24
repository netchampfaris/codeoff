import frappe
from frappe.tests import IntegrationTestCase

from codeoff.code_off.tests.utils import (
	cleanup_test_data,
	create_live_match,
	create_players,
	create_problem,
	create_tournament,
)


class TestCodeoffMatchLifecycle(IntegrationTestCase):
	"""Tests for match state transitions and validation."""

	def setUp(self):
		cleanup_test_data()

	def tearDown(self):
		cleanup_test_data()

	def _setup_match(self):
		"""Create a ready match with 2 players and a problem."""
		players = create_players(2, prefix="matchtest")
		problem = create_problem()
		tournament = create_tournament(players)
		tournament.generate_bracket()

		match_name = frappe.get_value("Codeoff Match", {"tournament": tournament.name})
		match = frappe.get_doc("Codeoff Match", match_name)
		return match, players, problem, tournament

	def test_auto_ready_status(self):
		"""Match with 2 players and a problem should auto-transition to Ready."""
		match, players, problem, _ = self._setup_match()
		match.problem = problem.name
		match.save()
		self.assertEqual(match.status, "Ready")

	def test_start_match_sets_times(self):
		"""Starting a match should set start_time, deadline, and status=Live."""
		match, players, problem, _ = self._setup_match()
		match.problem = problem.name
		match.save()
		match.start_match()

		match.reload()
		self.assertEqual(match.status, "Live")
		self.assertIsNotNone(match.start_time)
		self.assertIsNotNone(match.deadline)
		self.assertTrue(match.deadline > match.start_time)

	def test_cannot_start_draft_match(self):
		"""Cannot start a match that isn't Ready."""
		match, players, problem, _ = self._setup_match()
		match.status = "Draft"
		match.flags.ignore_validate = True
		match.save()

		with self.assertRaises(frappe.ValidationError):
			match.start_match()

	def test_same_player_rejected(self):
		"""Match cannot have the same player as both player_1 and player_2."""
		match, players, problem, _ = self._setup_match()
		match.player_2 = match.player_1
		with self.assertRaises(frappe.ValidationError):
			match.save()
