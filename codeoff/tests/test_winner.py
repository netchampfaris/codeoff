import frappe
from frappe.tests import IntegrationTestCase

from codeoff.services.match_engine import (
	determine_winner_by_score,
	finalize_match,
	process_verdict,
	recompute_scores,
	resolve_match_timeout,
)
from codeoff.tests.utils import cleanup_test_data, create_live_match, create_submission


class TestCodeoffWinnerDetermination(IntegrationTestCase):
	"""Tests for scoring and winner determination logic."""

	def setUp(self):
		cleanup_test_data()

	def tearDown(self):
		cleanup_test_data()

	def test_player1_higher_score_wins(self):
		"""Player with more passed tests wins on timeout."""
		match, players, _ = create_live_match(player_prefix="wintest")

		create_submission(match, players[0], "Wrong Answer", passed_tests=2, total_tests=3)
		create_submission(match, players[1], "Wrong Answer", passed_tests=1, total_tests=3)

		recompute_scores(match)
		determine_winner_by_score(match)

		match.reload()
		self.assertEqual(match.status, "Finished")
		self.assertEqual(match.winner, players[0].name)
		self.assertEqual(match.winning_reason, "Best Score")

	def test_player2_higher_score_wins(self):
		"""Player 2 with more passed tests wins."""
		match, players, _ = create_live_match(player_prefix="wintest")

		create_submission(match, players[0], "Wrong Answer", passed_tests=1, total_tests=3)
		create_submission(match, players[1], "Wrong Answer", passed_tests=2, total_tests=3)

		recompute_scores(match)
		determine_winner_by_score(match)

		match.reload()
		self.assertEqual(match.winner, players[1].name)

	def test_equal_score_fewer_wrongs_wins(self):
		"""With equal scores, fewer wrong submissions wins."""
		match, players, _ = create_live_match(player_prefix="wintest")

		create_submission(match, players[0], "Wrong Answer", passed_tests=1, total_tests=3)
		create_submission(match, players[0], "Wrong Answer", passed_tests=0, total_tests=3)
		create_submission(match, players[1], "Wrong Answer", passed_tests=1, total_tests=3)

		recompute_scores(match)
		determine_winner_by_score(match)

		match.reload()
		self.assertEqual(match.winner, players[1].name)

	def test_full_tie_enters_review(self):
		"""Equal scores and equal wrong submissions should enter Review."""
		match, players, _ = create_live_match(player_prefix="wintest")

		create_submission(match, players[0], "Wrong Answer", passed_tests=1, total_tests=3)
		create_submission(match, players[1], "Wrong Answer", passed_tests=1, total_tests=3)

		recompute_scores(match)
		determine_winner_by_score(match)

		match.reload()
		self.assertEqual(match.status, "Review")
		self.assertFalse(match.winner)
		self.assertTrue(match.tie_break_metadata)

	def test_no_submissions_enters_review(self):
		"""No submissions from either player should enter Review."""
		match, _, _ = create_live_match(player_prefix="wintest")

		recompute_scores(match)
		determine_winner_by_score(match)

		match.reload()
		self.assertEqual(match.status, "Review")

	def test_accepted_wins_immediately(self):
		"""An Accepted verdict should finalize the match with First Accepted."""
		match, players, _ = create_live_match(player_prefix="wintest")

		sub = create_submission(match, players[0], "Accepted", passed_tests=2, total_tests=2)
		process_verdict(sub.name)

		match.reload()
		self.assertEqual(match.status, "Finished")
		self.assertEqual(match.winner, players[0].name)
		self.assertEqual(match.winning_reason, "First Accepted")

	def test_resolve_timeout_skips_finished_match(self):
		"""resolve_match_timeout should not re-process a finished match."""
		match, players, _ = create_live_match(player_prefix="wintest")

		finalize_match(match, players[0].name, "First Accepted")
		resolve_match_timeout(match.name)

		match.reload()
		self.assertEqual(match.status, "Finished")
		self.assertEqual(match.winner, players[0].name)

	def test_both_accepted_earlier_submitted_at_wins(self):
		"""When both players have Accepted, the one with the earlier submitted_at wins."""
		from datetime import timedelta

		from frappe.utils import now_datetime

		match, players, _ = create_live_match(player_prefix="wintest")

		# Player 2 submitted first (earlier time)
		earlier = now_datetime() - timedelta(seconds=10)
		later = now_datetime() - timedelta(seconds=5)

		sub2 = create_submission(match, players[1], "Accepted", passed_tests=2, total_tests=2)
		frappe.db.set_value("Codeoff Submission", sub2.name, "submitted_at", earlier)

		sub1 = create_submission(match, players[0], "Accepted", passed_tests=2, total_tests=2)
		frappe.db.set_value("Codeoff Submission", sub1.name, "submitted_at", later)

		# Process player 1's verdict (which arrived after player 2's)
		sub1.reload()
		process_verdict(sub1.name)

		match.reload()
		self.assertEqual(match.status, "Finished")
		# Player 2 submitted earlier so should win
		self.assertEqual(match.winner, players[1].name)
		self.assertEqual(match.winning_reason, "First Accepted")

	def test_process_verdict_skips_non_live_match(self):
		"""process_verdict on a Finished match should be a no-op."""
		match, players, _ = create_live_match(player_prefix="wintest")

		# Create submission while still Live, then finish the match
		sub = create_submission(match, players[1], "Accepted", passed_tests=2, total_tests=2)
		finalize_match(match, players[0].name, "First Accepted")

		# Now processing the second player's verdict should not change the winner
		process_verdict(sub.name)

		match.reload()
		self.assertEqual(match.winner, players[0].name)
