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
		"title": "Add Two Numbers",
		"function_name": "add",
		"function_signature": "def add(a, b):",
		"difficulty": "Easy",
		"statement": (
			"Given two integers `a` and `b`, return their sum.\n\n**Example:**\n```\nadd(3, 5) → 8\n```"
		),
		"constraints_text": "-10^6 <= a, b <= 10^6",
		"starter_code": "def add(a, b):\n    pass\n",
		"test_cases": [
			{
				"case_name": "Basic",
				"visibility": "Sample",
				"input_data": "[3, 5]",
				"expected_output": "8",
				"weight": 1,
				"is_active": 1,
			},
			{
				"case_name": "Negatives",
				"visibility": "Sample",
				"input_data": "[-1, -2]",
				"expected_output": "-3",
				"weight": 1,
				"is_active": 1,
			},
			{
				"case_name": "Zero",
				"visibility": "Hidden",
				"input_data": "[0, 0]",
				"expected_output": "0",
				"weight": 1,
				"is_active": 1,
			},
			{
				"case_name": "Mixed",
				"visibility": "Hidden",
				"input_data": "[-10, 7]",
				"expected_output": "-3",
				"weight": 1,
				"is_active": 1,
			},
			{
				"case_name": "Large",
				"visibility": "Hidden",
				"input_data": "[1000000, 1]",
				"expected_output": "1000001",
				"weight": 1,
				"is_active": 1,
			},
		],
	},
	{
		"title": "Maximum of Three",
		"function_name": "max_of_three",
		"function_signature": "def max_of_three(a, b, c):",
		"difficulty": "Easy",
		"statement": (
			"Given three integers `a`, `b`, and `c`, return the largest one.\n\n"
			"**Example:**\n"
			"```\nmax_of_three(1, 5, 3) → 5\n```"
		),
		"constraints_text": "-10^6 <= a, b, c <= 10^6",
		"starter_code": "def max_of_three(a, b, c):\n    pass\n",
		"test_cases": [
			{
				"case_name": "Basic",
				"visibility": "Sample",
				"input_data": "[1, 5, 3]",
				"expected_output": "5",
				"weight": 1,
				"is_active": 1,
			},
			{
				"case_name": "First is largest",
				"visibility": "Sample",
				"input_data": "[9, 2, 4]",
				"expected_output": "9",
				"weight": 1,
				"is_active": 1,
			},
			{
				"case_name": "All equal",
				"visibility": "Hidden",
				"input_data": "[7, 7, 7]",
				"expected_output": "7",
				"weight": 1,
				"is_active": 1,
			},
			{
				"case_name": "Negatives",
				"visibility": "Hidden",
				"input_data": "[-3, -1, -2]",
				"expected_output": "-1",
				"weight": 1,
				"is_active": 1,
			},
			{
				"case_name": "Last is largest",
				"visibility": "Hidden",
				"input_data": "[2, 4, 8]",
				"expected_output": "8",
				"weight": 1,
				"is_active": 1,
			},
		],
	},
	{
		"title": "Count Vowels",
		"function_name": "count_vowels",
		"function_signature": "def count_vowels(s):",
		"difficulty": "Easy",
		"statement": (
			"Given a string `s`, return the number of vowels (a, e, i, o, u) it contains. "
			"Both uppercase and lowercase vowels count.\n\n"
			"**Example:**\n"
			"```\ncount_vowels('hello') → 2\n```"
		),
		"constraints_text": "0 <= len(s) <= 10000",
		"starter_code": "def count_vowels(s):\n    pass\n",
		"test_cases": [
			{
				"case_name": "Basic",
				"visibility": "Sample",
				"input_data": '["hello"]',
				"expected_output": "2",
				"weight": 1,
				"is_active": 1,
			},
			{
				"case_name": "All vowels",
				"visibility": "Sample",
				"input_data": '["aeiou"]',
				"expected_output": "5",
				"weight": 1,
				"is_active": 1,
			},
			{
				"case_name": "Mixed case",
				"visibility": "Hidden",
				"input_data": '["Hello World"]',
				"expected_output": "3",
				"weight": 1,
				"is_active": 1,
			},
			{
				"case_name": "No vowels",
				"visibility": "Hidden",
				"input_data": '["rhythm"]',
				"expected_output": "0",
				"weight": 1,
				"is_active": 1,
			},
			{
				"case_name": "Empty",
				"visibility": "Hidden",
				"input_data": '[""]',
				"expected_output": "0",
				"weight": 1,
				"is_active": 1,
			},
		],
	},
	{
		"title": "List Sum",
		"function_name": "list_sum",
		"function_signature": "def list_sum(nums):",
		"difficulty": "Easy",
		"statement": (
			"Given a list of integers `nums`, return the sum of all elements.\n\n"
			"**Example:**\n"
			"```\nlist_sum([1, 2, 3, 4]) → 10\n```"
		),
		"constraints_text": "0 <= len(nums) <= 1000\n-1000 <= nums[i] <= 1000",
		"starter_code": "def list_sum(nums):\n    pass\n",
		"test_cases": [
			{
				"case_name": "Basic",
				"visibility": "Sample",
				"input_data": "[[1, 2, 3, 4]]",
				"expected_output": "10",
				"weight": 1,
				"is_active": 1,
			},
			{
				"case_name": "Negatives",
				"visibility": "Sample",
				"input_data": "[[-1, -2, 3]]",
				"expected_output": "0",
				"weight": 1,
				"is_active": 1,
			},
			{
				"case_name": "Empty",
				"visibility": "Hidden",
				"input_data": "[[]]",
				"expected_output": "0",
				"weight": 1,
				"is_active": 1,
			},
			{
				"case_name": "Single element",
				"visibility": "Hidden",
				"input_data": "[[42]]",
				"expected_output": "42",
				"weight": 1,
				"is_active": 1,
			},
			{
				"case_name": "All zeros",
				"visibility": "Hidden",
				"input_data": "[[0, 0, 0]]",
				"expected_output": "0",
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

	# Assign problems to all matches (cycle through available problems)
	matches = frappe.get_all(
		"Codeoff Match",
		filters={"tournament": tournament.name},
		fields=["name", "round_number", "bracket_position"],
		order_by="round_number asc, bracket_position asc",
	)
	for i, m in enumerate(matches):
		problem = problems[i % len(problems)]
		frappe.db.set_value("Codeoff Match", m.name, "problem", problem.name)
		print(f"  Match {m.name} (R{m.round_number}P{m.bracket_position}): Problem: {problem.title}")

	frappe.db.commit()

	round1_matches = [m for m in matches if m.round_number == 1]
	first_match = frappe.get_doc("Codeoff Match", round1_matches[0].name)

	print("\n✓ Demo data created successfully!")
	print("\nLogin credentials (password for all: 123):")
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
