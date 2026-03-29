import frappe
from frappe.tests import IntegrationTestCase

from codeoff.services.match_engine import finalize_match
from codeoff.tests.utils import (
	cleanup_test_data,
	create_players,
	create_problem,
	create_submission,
	create_tournament,
)


class TestCodeoffBracket(IntegrationTestCase):
	"""Tests for bracket generation and advancement."""

	def setUp(self):
		cleanup_test_data()

	def tearDown(self):
		cleanup_test_data()

	def test_bracket_4_players(self):
		"""4 players should produce 3 matches: 2 in round 1, 1 in round 2."""
		players = create_players(4)
		tournament = create_tournament(players)
		tournament.generate_bracket()

		matches = frappe.get_all(
			"Codeoff Match",
			filters={"tournament": tournament.name},
			fields=["round_number", "bracket_position", "player_1", "player_2"],
			order_by="round_number, bracket_position",
		)

		self.assertEqual(len(matches), 3)

		r1 = [m for m in matches if m.round_number == 1]
		self.assertEqual(len(r1), 2)
		self.assertTrue(all(m.player_1 and m.player_2 for m in r1))

		r2 = [m for m in matches if m.round_number == 2]
		self.assertEqual(len(r2), 1)
		self.assertFalse(r2[0].player_1)
		self.assertFalse(r2[0].player_2)

	def test_bracket_8_players(self):
		"""8 players should produce 7 matches across 3 rounds."""
		players = create_players(8)
		tournament = create_tournament(players)
		tournament.generate_bracket()

		matches = frappe.get_all(
			"Codeoff Match",
			filters={"tournament": tournament.name},
			fields=["round_number", "bracket_position"],
		)

		self.assertEqual(len(matches), 7)

		by_round = {}
		for m in matches:
			by_round.setdefault(m.round_number, []).append(m)

		self.assertEqual(len(by_round[1]), 4)
		self.assertEqual(len(by_round[2]), 2)
		self.assertEqual(len(by_round[3]), 1)

	def test_bracket_2_players(self):
		"""2 players = 1 match (the final)."""
		players = create_players(2)
		tournament = create_tournament(players)
		tournament.generate_bracket()

		matches = frappe.get_all("Codeoff Match", filters={"tournament": tournament.name})
		self.assertEqual(len(matches), 1)

	def test_non_power_of_2_rejected(self):
		"""3 players should fail validation at insert time."""
		players = create_players(4)
		with self.assertRaises(frappe.ValidationError):
			create_tournament(players[:3])

	def test_seeding_order(self):
		"""Players should be arranged by seed in round 1."""
		players = create_players(4)
		tournament = frappe.get_doc(
			{
				"doctype": "Codeoff Tournament",
				"tournament_name": f"Seeded Tournament {frappe.generate_hash(length=6)}",
				"match_duration_seconds": 600,
				"format": "Single Elimination",
				"players": [
					{"player": players[0].name, "seed": 4},
					{"player": players[1].name, "seed": 3},
					{"player": players[2].name, "seed": 2},
					{"player": players[3].name, "seed": 1},
				],
			}
		)
		tournament.insert(ignore_permissions=True)
		tournament.generate_bracket()

		r1_matches = frappe.get_all(
			"Codeoff Match",
			filters={"tournament": tournament.name, "round_number": 1},
			fields=["bracket_position", "player_1", "player_2"],
			order_by="bracket_position",
		)

		self.assertEqual(r1_matches[0].player_1, players[3].name)
		self.assertEqual(r1_matches[0].player_2, players[2].name)

	def test_duplicate_bracket_rejected(self):
		"""Cannot generate bracket twice."""
		players = create_players(4)
		tournament = create_tournament(players)
		tournament.generate_bracket()

		with self.assertRaises(frappe.ValidationError):
			tournament.generate_bracket()

	def test_bracket_advancement(self):
		"""Winner of round 1 should be placed into round 2."""
		players = create_players(4)
		tournament = create_tournament(players)
		problem = create_problem(
			title=f"Bracket Problem {frappe.generate_hash(length=6)}",
			function_name="add_two",
			function_signature="def add_two(a, b):",
			statement="Return the sum of two numbers.",
			test_cases=[
				{
					"case_name": "Sample 1",
					"visibility": "Sample",
					"input_data": "[1, 2]",
					"expected_output": "3",
					"weight": 1,
					"is_active": 1,
				},
			],
		)
		tournament.generate_bracket()

		r1_matches = frappe.get_all(
			"Codeoff Match",
			filters={"tournament": tournament.name, "round_number": 1},
			fields=["name", "bracket_position"],
			order_by="bracket_position",
		)

		match1 = frappe.get_doc("Codeoff Match", r1_matches[0].name)
		match1.problem = problem.name
		match1.save()
		match1.start_match()
		match1.reload()
		finalize_match(match1, match1.player_1, "First Accepted")

		r2_match = frappe.get_all(
			"Codeoff Match",
			filters={"tournament": tournament.name, "round_number": 2},
			fields=["name", "player_1", "player_2"],
		)[0]

		self.assertEqual(r2_match.player_1, match1.player_1)

	def test_tournament_completes_after_final(self):
		"""Tournament should be marked Completed when the final match finishes."""
		players = create_players(2)
		tournament = create_tournament(players)
		problem = create_problem()
		tournament.generate_bracket()

		match = frappe.get_all(
			"Codeoff Match",
			filters={"tournament": tournament.name},
			fields=["name"],
		)[0]
		match_doc = frappe.get_doc("Codeoff Match", match.name)
		match_doc.problem = problem.name
		match_doc.save()
		match_doc.start_match()
		match_doc.reload()
		finalize_match(match_doc, match_doc.player_1, "First Accepted")

		tournament.reload()
		self.assertEqual(tournament.status, "Completed")
		self.assertIsNotNone(tournament.completed_on)

	def test_clear_tournament_data_deletes_runtime_records(self):
		"""Clearing tournament data should remove matches and dependent records but keep the tournament."""
		players = create_players(4)
		problem = create_problem()
		tournament = create_tournament(players)
		tournament.generate_bracket()

		match_name = frappe.get_value(
			"Codeoff Match",
			{"tournament": tournament.name, "round_number": 1, "bracket_position": 1},
		)
		match = frappe.get_doc("Codeoff Match", match_name)
		match.problem = problem.name
		match.save()
		match.start_match()
		match.reload()

		create_submission(match, players[0])
		frappe.get_doc(
			{
				"doctype": "Codeoff Draft State",
				"match": match.name,
				"player": players[0].name,
				"language": "python",
				"source_code": "def add(a, b):\n    return a + b",
				"cursor_line": 1,
				"cursor_column": 0,
			}
		).insert(ignore_permissions=True)
		frappe.cache.set_value(f"codeoff_draft:{match.name}:{players[0].name}", {"source_code": "draft"})

		tournament.players[0].status = "Winner"
		tournament.status = "Completed"
		tournament.current_round = 2
		tournament.save(ignore_permissions=True)

		summary = tournament.clear_tournament_data()
		tournament.reload()

		self.assertEqual(summary["matches_deleted"], 3)
		self.assertEqual(summary["submissions_deleted"], 1)
		self.assertEqual(summary["draft_states_deleted"], 1)
		self.assertEqual(tournament.status, "Draft")
		self.assertFalse(tournament.current_round)
		self.assertIsNone(tournament.completed_on)
		self.assertTrue(all(row.status == "Registered" for row in tournament.players))
		self.assertFalse(frappe.db.exists("Codeoff Match", {"tournament": tournament.name}))
		self.assertFalse(frappe.db.exists("Codeoff Submission", {"match": match.name}))
		self.assertFalse(frappe.db.exists("Codeoff Draft State", {"match": match.name}))
		self.assertIsNone(frappe.cache.get_value(f"codeoff_draft:{match.name}:{players[0].name}"))
