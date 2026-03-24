# Copyright (c) 2026, Code Off and contributors
# For license information, please see license.txt

import math

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
