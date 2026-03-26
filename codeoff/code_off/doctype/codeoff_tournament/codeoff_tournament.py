# Copyright (c) 2026, Code Off and contributors
# For license information, please see license.txt

import math
import random

import frappe
from frappe.model.document import Document


class CodeoffTournament(Document):
	def validate(self):
		self.validate_player_count()

	def validate_player_count(self):
		if not self.players:
			return
		count = len(self.players)
		if count < 2:
			frappe.throw("Tournament must have at least 2 players")
		if count & (count - 1) != 0:
			frappe.throw(f"Player count must be a power of 2 (got {count})")

	@frappe.whitelist()
	def generate_bracket(self):
		self.validate_player_count()

		if frappe.db.exists("Codeoff Match", {"tournament": self.name}):
			frappe.throw("Bracket already generated. Delete existing matches first.")

		players = list(self.players)
		# Sort by seed (seeded players first, then by order added)
		players.sort(key=lambda p: (p.seed or 9999, p.idx))

		num_players = len(players)
		total_rounds = int(math.log2(num_players))

		# Create all matches for all rounds
		for round_num in range(1, total_rounds + 1):
			matches_in_round = num_players // (2**round_num)
			for pos in range(1, matches_in_round + 1):
				match_doc = frappe.new_doc("Codeoff Match")
				match_doc.tournament = self.name
				match_doc.round_number = round_num
				match_doc.bracket_position = pos

				# Only assign players to round 1
				if round_num == 1:
					idx1 = (pos - 1) * 2
					idx2 = idx1 + 1
					match_doc.player_1 = players[idx1].player
					match_doc.player_2 = players[idx2].player

				match_doc.insert()

		self.current_round = 1
		self.status = "Ready"
		self.save()

		frappe.msgprint(f"Bracket generated: {total_rounds} rounds, {num_players - 1} matches")

	@frappe.whitelist()
	def start_round(self):
		"""Start all Ready matches in the current round simultaneously."""
		matches = frappe.get_all(
			"Codeoff Match",
			filters={
				"tournament": self.name,
				"round_number": self.current_round,
				"status": "Ready",
			},
			fields=["name"],
		)
		if not matches:
			frappe.throw(f"No Ready matches found in round {self.current_round}")

		for m in matches:
			match_doc = frappe.get_doc("Codeoff Match", m.name)
			match_doc.start_match()

		frappe.msgprint(f"Round {self.current_round}: {len(matches)} match(es) started")

	@frappe.whitelist()
	def finish_round_with_random_winners(self):
		"""Test helper: randomly pick a winner for every Live/Ready match in the current round."""
		matches = frappe.get_all(
			"Codeoff Match",
			filters={
				"tournament": self.name,
				"round_number": self.current_round,
				"status": ["in", ["Draft", "Ready", "Live"]],
			},
			fields=["name", "player_1", "player_2"],
		)

		if not matches:
			frappe.throw(f"No active matches found in round {self.current_round}")

		from codeoff.services.match_engine import finalize_match

		for m in matches:
			if not m.player_1 or not m.player_2:
				frappe.throw(f"Match {m.name} does not have both players assigned yet")
			match_doc = frappe.get_doc("Codeoff Match", m.name)
			winner = random.choice([m.player_1, m.player_2])
			finalize_match(match_doc, winner, "Manual Override")

		frappe.msgprint(f"Round {self.current_round}: {len(matches)} match(es) finished with random winners")

	@frappe.whitelist()
	def reset_all_matches(self):
		"""Test helper: reset every match and submission back to initial state."""
		matches = frappe.get_all(
			"Codeoff Match",
			filters={"tournament": self.name},
			fields=["name", "round_number", "player_1", "player_2"],
		)

		if not matches:
			frappe.throw("No matches found for this tournament")

		# Delete all submissions for this tournament's matches
		match_names = [m.name for m in matches]
		submissions = frappe.get_all(
			"Codeoff Submission", filters={"match": ["in", match_names]}, pluck="name"
		)
		for sub in submissions:
			frappe.delete_doc("Codeoff Submission", sub, ignore_permissions=True)

		# Reset each match
		for m in matches:
			is_round1 = m.round_number == 1
			frappe.db.set_value(
				"Codeoff Match",
				m.name,
				{
					"status": "Ready" if is_round1 else "Draft",
					"winner": None,
					"winning_reason": None,
					"start_time": None,
					"deadline": None,
					"tie_break_metadata": None,
					"best_score_player_1": 0,
					"best_score_player_2": 0,
					"wrong_submissions_player_1": 0,
					"wrong_submissions_player_2": 0,
					"player_1_joined": 0,
					"player_2_joined": 0,
					# Clear players for rounds 2+ (they'll be filled by advance_bracket again)
					"player_1": m.player_1 if is_round1 else None,
					"player_2": m.player_2 if is_round1 else None,
				},
			)

		# Reset draft states
		draft_states = frappe.get_all(
			"Codeoff Draft State", filters={"match": ["in", match_names]}, pluck="name"
		)
		for ds in draft_states:
			frappe.delete_doc("Codeoff Draft State", ds, ignore_permissions=True)

		self.current_round = 1
		self.status = "Ready"
		self.save(ignore_permissions=True)

		frappe.msgprint(f"Reset {len(matches)} match(es) and {len(submissions)} submission(s)")
