import frappe
from frappe.tests import IntegrationTestCase

from codeoff.tests.utils import (
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

	def test_cannot_start_finished_match(self):
		"""Cannot re-start a match that is already Finished."""
		match, players, problem, _ = self._setup_match()
		match.problem = problem.name
		match.save()
		match.start_match()
		match.reload()

		# Simulate finish
		match.status = "Finished"
		match.flags.ignore_validate = True
		match.save()

		with self.assertRaises(frappe.ValidationError):
			match.start_match()

	def test_per_round_duration_used_when_configured(self):
		"""When a round duration entry exists it overrides the tournament default."""
		from datetime import timedelta

		players = create_players(2, prefix="durtest")
		problem = create_problem()
		tournament = create_tournament(players, duration=600)
		# Add a per-round duration for round 1
		tournament.append("round_durations", {"round_number": 1, "duration_seconds": 120})
		tournament.save()
		tournament.generate_bracket()

		match_name = frappe.get_value("Codeoff Match", {"tournament": tournament.name})
		match = frappe.get_doc("Codeoff Match", match_name)
		match.problem = problem.name
		match.save()
		match.start_match()
		match.reload()

		expected_deadline = match.start_time + timedelta(seconds=120)
		# Allow 2-second tolerance for test execution time
		delta = abs((match.deadline - expected_deadline).total_seconds())
		self.assertLessEqual(delta, 2)
