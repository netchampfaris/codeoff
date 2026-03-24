import frappe


CLEANUP_DOCTYPES = (
	"Codeoff Submission",
	"Codeoff Draft State",
	"Codeoff Match",
	"Codeoff Tournament",
	"Codeoff Problem",
	"Codeoff Player",
)


def cleanup_test_data():
	for dt in CLEANUP_DOCTYPES:
		frappe.db.delete(dt)
	frappe.db.commit()


def create_players(count, prefix="player"):
	players = []
	for i in range(count):
		email = f"{prefix}{i + 1}@codeoff.test"
		if not frappe.db.exists("User", email):
			frappe.get_doc(
				{
					"doctype": "User",
					"email": email,
					"first_name": f"Player {i + 1}",
					"send_welcome_email": 0,
				}
			).insert(ignore_permissions=True)
		player = frappe.get_doc({"doctype": "Codeoff Player", "user": email, "is_active": 1}).insert(
			ignore_permissions=True
		)
		players.append(player)
	return players


def create_tournament(players, duration=600):
	tournament = frappe.get_doc(
		{
			"doctype": "Codeoff Tournament",
			"tournament_name": f"Test Tournament {frappe.generate_hash(length=6)}",
			"match_duration_seconds": duration,
			"format": "Single Elimination",
			"players": [{"player": p.name, "seed": i + 1} for i, p in enumerate(players)],
		}
	)
	tournament.insert(ignore_permissions=True)
	return tournament


def create_problem(**kwargs):
	defaults = {
		"doctype": "Codeoff Problem",
		"title": f"Test Problem {frappe.generate_hash(length=6)}",
		"function_name": "add",
		"function_signature": "def add(a, b):",
		"statement": "Add two numbers.",
		"test_cases": [
			{
				"case_name": "Test 1",
				"visibility": "Hidden",
				"input_data": "[1, 2]",
				"expected_output": "3",
				"weight": 1,
				"is_active": 1,
			},
		],
	}
	defaults.update(kwargs)
	problem = frappe.get_doc(defaults)
	problem.insert(ignore_permissions=True)
	return problem


def create_live_match(player_prefix="test", extra_test_cases=None):
	"""Create a tournament with 2 players, generate bracket, set problem, start match.

	Returns (match, players, problem).
	"""
	players = create_players(2, prefix=player_prefix)

	test_cases = [
		{
			"case_name": "Test 1",
			"visibility": "Hidden",
			"input_data": "[1, 2]",
			"expected_output": "3",
			"weight": 1,
			"is_active": 1,
		},
		{
			"case_name": "Test 2",
			"visibility": "Hidden",
			"input_data": "[5, 5]",
			"expected_output": "10",
			"weight": 1,
			"is_active": 1,
		},
	]
	if extra_test_cases:
		test_cases = extra_test_cases

	problem = create_problem(test_cases=test_cases)
	tournament = create_tournament(players)
	tournament.generate_bracket()

	match_name = frappe.get_value("Codeoff Match", {"tournament": tournament.name})
	match = frappe.get_doc("Codeoff Match", match_name)
	match.problem = problem.name
	match.save()
	match.start_match()
	match.reload()

	return match, players, problem


def create_submission(match, player, verdict="Wrong Answer", passed_tests=0, total_tests=2):
	"""Create a completed submission."""
	sub = frappe.get_doc(
		{
			"doctype": "Codeoff Submission",
			"match": match.name,
			"player": player.name,
			"problem": match.problem,
			"source_code": "def add(a, b): return a + b",
			"status": "Completed",
			"verdict": verdict,
			"passed_tests": passed_tests,
			"total_tests": total_tests,
			"score": passed_tests,
		}
	)
	sub.insert(ignore_permissions=True)
	return sub


class MockTestCase:
	"""Lightweight stand-in for Codeoff Test Case child table rows."""

	def __init__(self, input_data, expected_output, visibility="Hidden", is_active=True):
		self.input_data = input_data
		self.expected_output = expected_output
		self.visibility = visibility
		self.is_active = is_active
		self.case_name = "test"
		self.weight = 1


def make_test_cases(cases):
	"""Build a list of MockTestCase from dicts with 'input' and 'expected' keys."""
	return [MockTestCase(c["input"], c["expected"]) for c in cases]
