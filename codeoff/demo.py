"""
Demo data setup script for Codeoff.

Usage:
    bench --site codeoff.localhost execute codeoff.demo.setup
    bench --site codeoff.localhost execute codeoff.demo.teardown
"""

import frappe

DEMO_ORGANIZER = {"email": "organizer@codeoff.demo", "first_name": "Organizer", "last_name": ""}

DEMO_PLAYERS = [
	{"email": "alice@codeoff.demo", "first_name": "Alice", "last_name": "Chen"},
	{"email": "bob@codeoff.demo", "first_name": "Bob", "last_name": "Kumar"},
	{"email": "carol@codeoff.demo", "first_name": "Carol", "last_name": "Zhang"},
	{"email": "dave@codeoff.demo", "first_name": "Dave", "last_name": "Patel"},
	{"email": "eve@codeoff.demo", "first_name": "Eve", "last_name": "Singh"},
	{"email": "frank@codeoff.demo", "first_name": "Frank", "last_name": "Li"},
	{"email": "grace@codeoff.demo", "first_name": "Grace", "last_name": "Nakamura"},
	{"email": "hank@codeoff.demo", "first_name": "Hank", "last_name": "Russo"},
]

DEMO_PROBLEMS = [
	{
		"title": "Two Sum",
		"function_name": "two_sum",
		"function_signature": "def two_sum(nums, target):",
		"difficulty": "Easy",
		"statement": (
			"Given an array of integers `nums` and an integer `target`, "
			"return the indices of the two numbers that add up to `target`.\n\n"
			"You may assume that each input has exactly one solution, "
			"and you may not use the same element twice.\n\n"
			"Return the answer as a list of two indices in any order.\n\n"
			"**Example:**\n"
			"```\ntwo_sum([2, 7, 11, 15], 9) → [0, 1]\n```"
		),
		"constraints_text": "2 <= len(nums) <= 100\n-1000 <= nums[i] <= 1000\nExactly one valid answer exists.",
		"test_cases": [
			{
				"case_name": "Basic pair",
				"visibility": "Sample",
				"input_data": "[[2, 7, 11, 15], 9]",
				"expected_output": "[0, 1]",
				"weight": 1,
				"is_active": 1,
			},
			{
				"case_name": "Middle elements",
				"visibility": "Sample",
				"input_data": "[[3, 2, 4], 6]",
				"expected_output": "[1, 2]",
				"weight": 1,
				"is_active": 1,
			},
			{
				"case_name": "Same number",
				"visibility": "Hidden",
				"input_data": "[[3, 3], 6]",
				"expected_output": "[0, 1]",
				"weight": 1,
				"is_active": 1,
			},
			{
				"case_name": "Negative numbers",
				"visibility": "Hidden",
				"input_data": "[[-1, -2, -3, -4, -5], -8]",
				"expected_output": "[2, 4]",
				"weight": 1,
				"is_active": 1,
			},
			{
				"case_name": "Large array",
				"visibility": "Hidden",
				"input_data": "[[1, 5, 3, 7, 8, 2, 4, 6, 9, 10], 19]",
				"expected_output": "[7, 8]",
				"weight": 1,
				"is_active": 1,
			},
		],
	},
	{
		"title": "Fizz Buzz",
		"function_name": "fizz_buzz",
		"function_signature": "def fizz_buzz(n):",
		"difficulty": "Easy",
		"statement": (
			"Given an integer `n`, return a list of strings where:\n\n"
			'- `"FizzBuzz"` if the number is divisible by both 3 and 5\n'
			'- `"Fizz"` if the number is divisible by 3\n'
			'- `"Buzz"` if the number is divisible by 5\n'
			"- The number as a string otherwise\n\n"
			"**Example:**\n"
			'```\nfizz_buzz(5) → ["1", "2", "Fizz", "4", "Buzz"]\n```'
		),
		"constraints_text": "1 <= n <= 10000",
		"test_cases": [
			{
				"case_name": "Small input",
				"visibility": "Sample",
				"input_data": "[5]",
				"expected_output": '["1", "2", "Fizz", "4", "Buzz"]',
				"weight": 1,
				"is_active": 1,
			},
			{
				"case_name": "FizzBuzz at 15",
				"visibility": "Sample",
				"input_data": "[15]",
				"expected_output": '["1", "2", "Fizz", "4", "Buzz", "Fizz", "7", "8", "Fizz", "Buzz", "11", "Fizz", "13", "14", "FizzBuzz"]',
				"weight": 1,
				"is_active": 1,
			},
			{
				"case_name": "Single",
				"visibility": "Hidden",
				"input_data": "[1]",
				"expected_output": '["1"]',
				"weight": 1,
				"is_active": 1,
			},
			{
				"case_name": "Thirty",
				"visibility": "Hidden",
				"input_data": "[30]",
				"expected_output": '["1", "2", "Fizz", "4", "Buzz", "Fizz", "7", "8", "Fizz", "Buzz", "11", "Fizz", "13", "14", "FizzBuzz", "16", "17", "Fizz", "19", "Buzz", "Fizz", "22", "23", "Fizz", "Buzz", "26", "Fizz", "28", "29", "FizzBuzz"]',
				"weight": 1,
				"is_active": 1,
			},
		],
	},
	{
		"title": "Reverse Linked List",
		"function_name": "reverse_list",
		"function_signature": "def reverse_list(nums):",
		"difficulty": "Easy",
		"statement": (
			"Given a list of integers, return the list in reverse order.\n\n"
			"**Example:**\n"
			"```\nreverse_list([1, 2, 3, 4, 5]) → [5, 4, 3, 2, 1]\n```"
		),
		"constraints_text": "0 <= len(nums) <= 1000",
		"test_cases": [
			{
				"case_name": "Basic",
				"visibility": "Sample",
				"input_data": "[[1, 2, 3, 4, 5]]",
				"expected_output": "[5, 4, 3, 2, 1]",
				"weight": 1,
				"is_active": 1,
			},
			{
				"case_name": "Empty",
				"visibility": "Hidden",
				"input_data": "[[]]",
				"expected_output": "[]",
				"weight": 1,
				"is_active": 1,
			},
			{
				"case_name": "Single",
				"visibility": "Hidden",
				"input_data": "[[42]]",
				"expected_output": "[42]",
				"weight": 1,
				"is_active": 1,
			},
		],
	},
	{
		"title": "Palindrome Check",
		"function_name": "is_palindrome",
		"function_signature": "def is_palindrome(s):",
		"difficulty": "Easy",
		"statement": (
			"Given a string `s`, return `True` if it is a palindrome "
			"(reads the same forwards and backwards), ignoring case and "
			"non-alphanumeric characters. Return `False` otherwise.\n\n"
			"**Example:**\n"
			'```\nis_palindrome("racecar") → True\n'
			'is_palindrome("hello") → False\n```'
		),
		"constraints_text": "0 <= len(s) <= 10000\nString may contain letters, digits, spaces and punctuation.",
		"test_cases": [
			{
				"case_name": "Simple palindrome",
				"visibility": "Sample",
				"input_data": '["racecar"]',
				"expected_output": "true",
				"weight": 1,
				"is_active": 1,
			},
			{
				"case_name": "Not a palindrome",
				"visibility": "Sample",
				"input_data": '["hello"]',
				"expected_output": "false",
				"weight": 1,
				"is_active": 1,
			},
			{
				"case_name": "Mixed case",
				"visibility": "Hidden",
				"input_data": '["RaceCar"]',
				"expected_output": "true",
				"weight": 1,
				"is_active": 1,
			},
			{
				"case_name": "With spaces and punctuation",
				"visibility": "Hidden",
				"input_data": '["A man, a plan, a canal: Panama"]',
				"expected_output": "true",
				"weight": 1,
				"is_active": 1,
			},
			{
				"case_name": "Empty string",
				"visibility": "Hidden",
				"input_data": '[""]',
				"expected_output": "true",
				"weight": 1,
				"is_active": 1,
			},
		],
	},
]


def setup():
	"""Create demo data: 8 players, 4 problems, 1 tournament with bracket, first round matches ready."""
	# Clean up codeoff data only (not users)
	_clean_codeoff_data()

	# Create organizer user with System Manager role
	print("Creating organizer...")
	org = DEMO_ORGANIZER
	if not frappe.db.exists("User", org["email"]):
		user = frappe.get_doc(
			{
				"doctype": "User",
				"email": org["email"],
				"first_name": org["first_name"],
				"send_welcome_email": 0,
				"new_password": "123",
				"roles": [{"role": "System Manager"}],
			}
		)
		user.flags.ignore_password_policy = True
		user.insert(ignore_permissions=True)
		print(f"  Created organizer: {org['email']} — password: 123")
	else:
		print(f"  Organizer already exists: {org['email']}")

	print("\nCreating demo players...")
	players = []
	for p in DEMO_PLAYERS:
		if not frappe.db.exists("User", p["email"]):
			user = frappe.get_doc(
				{
					"doctype": "User",
					"email": p["email"],
					"first_name": p["first_name"],
					"last_name": p.get("last_name", ""),
					"send_welcome_email": 0,
					"new_password": "123",
				}
			)
			user.flags.ignore_password_policy = True
			user.insert(ignore_permissions=True)
			print(f"  Created user: {p['email']} — password: 123")
		else:
			print(f"  User already exists: {p['email']}")

		if frappe.db.exists("Codeoff Player", {"user": p["email"]}):
			player = frappe.get_doc("Codeoff Player", {"user": p["email"]})
		else:
			player = frappe.get_doc(
				{
					"doctype": "Codeoff Player",
					"user": p["email"],
					"player_name": f"{p['first_name']} {p.get('last_name', '')}".strip(),
					"is_active": 1,
				}
			)
			player.insert(ignore_permissions=True)
		players.append(player)
		print(f"  Player: {player.player_name} ({p['email']})")

	print("\nCreating demo problems...")
	problems = []
	for prob_data in DEMO_PROBLEMS:
		problem = frappe.get_doc({"doctype": "Codeoff Problem", **prob_data})
		problem.insert(ignore_permissions=True)
		problems.append(problem)
		print(f"  Created problem: {problem.title}")

	print("\nCreating tournament with 8 players...")
	tournament = frappe.get_doc(
		{
			"doctype": "Codeoff Tournament",
			"tournament_name": "Demo Tournament",
			"match_duration_seconds": 1200,
			"format": "Single Elimination",
			"players": [{"player": p.name, "seed": i + 1} for i, p in enumerate(players)],
		}
	)
	tournament.insert(ignore_permissions=True)
	tournament.generate_bracket()
	print(f"  Tournament: {tournament.name} — bracket generated")

	# Assign problems to matches
	matches = frappe.get_all(
		"Codeoff Match",
		filters={"tournament": tournament.name, "round_number": 1},
		order_by="bracket_position asc",
	)
	for i, m in enumerate(matches):
		match = frappe.get_doc("Codeoff Match", m.name)
		match.problem = problems[i].name
		match.save(ignore_permissions=True)
		print(f"  Match {match.name}: {match.player_1} vs {match.player_2} — Problem: {problems[i].title}")

	frappe.db.commit()

	first_match = frappe.get_doc("Codeoff Match", matches[0].name)

	print("\n✓ Demo data created successfully!")
	print(f"\nLogin credentials (password for all: 123):")
	print(f"  {DEMO_ORGANIZER['email']} (organizer — Desk access)")
	for p in DEMO_PLAYERS:
		print(f"  {p['email']} (contestant)")
	print(f"\nFirst match: {first_match.name} (status: {first_match.status})")
	print(f"  Match starts when both players join at: /codeoff/match/{first_match.name}")
	print(f"  Spectator URL: /codeoff/spectate/{first_match.name}")


def _clean_codeoff_data():
	"""Remove all codeoff document data (preserves users and sessions)."""
	for dt in (
		"Codeoff Submission",
		"Codeoff Draft State",
		"Codeoff Match",
		"Codeoff Tournament Player",
		"Codeoff Tournament",
		"Codeoff Test Case",
		"Codeoff Problem",
		"Codeoff Player",
	):
		frappe.db.delete(dt)
	frappe.db.commit()


def teardown():
	"""Remove all demo data including users."""
	_clean_codeoff_data()

	for p in DEMO_PLAYERS:
		if frappe.db.exists("User", p["email"]):
			frappe.delete_doc("User", p["email"], ignore_permissions=True)

	if frappe.db.exists("User", DEMO_ORGANIZER["email"]):
		frappe.delete_doc("User", DEMO_ORGANIZER["email"], ignore_permissions=True)

	frappe.db.commit()
	print("Demo data cleaned up (including users).")
