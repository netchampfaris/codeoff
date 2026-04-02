# Copyright (c) 2026, Code Off and contributors
# For license information, please see license.txt

import json
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

	def _ensure_no_existing_matches(self):
		if frappe.db.exists("Codeoff Match", {"tournament": self.name}):
			frappe.throw("Bracket already generated. Delete existing matches first.")

	def _get_ordered_players_for_bracket(self):
		seeded = sorted([p for p in self.players if p.seed], key=lambda p: p.seed)
		unseeded = [p for p in self.players if not p.seed]
		random.shuffle(unseeded)
		return seeded + unseeded

	def _get_round_config_map(self):
		return {int(row.round_number): row for row in self.round_durations if row.round_number}

	def _get_match_status(self, player_1=None, player_2=None, problem=None):
		return "Ready" if player_1 and player_2 and problem else "Draft"

	def _assign_random_problems_by_round(self, total_rounds: int, num_players: int):
		round_config = self._get_round_config_map()
		problem_map = {}

		for round_num in range(1, total_rounds + 1):
			config = round_config.get(round_num)
			if not config or not config.difficulty:
				frappe.throw(f"Round {round_num} must have a difficulty configured before planning")

			matches_in_round = num_players // (2**round_num)
			candidates = frappe.get_all(
				"Codeoff Problem",
				filters={"difficulty": config.difficulty, "is_active": 1},
				fields=["name"],
			)
			if len(candidates) < matches_in_round:
				frappe.throw(
					f"Round {round_num} needs {matches_in_round} {config.difficulty} problem(s), "
					f"but only {len(candidates)} active problem(s) are available"
				)

			problem_map[round_num] = random.sample(
				[candidate.name for candidate in candidates], matches_in_round
			)

		return problem_map

	def _create_match(
		self,
		round_number: int,
		bracket_position: int,
		player_1=None,
		player_2=None,
		problem=None,
		duration_seconds=None,
	):
		match_doc = frappe.new_doc("Codeoff Match")
		match_doc.tournament = self.name
		match_doc.round_number = round_number
		match_doc.bracket_position = bracket_position
		match_doc.player_1 = player_1
		match_doc.player_2 = player_2
		match_doc.problem = problem
		if duration_seconds:
			match_doc.duration_seconds = int(duration_seconds)
		match_doc.status = self._get_match_status(player_1, player_2, problem)
		match_doc.insert()
		return match_doc

	@frappe.whitelist()
	def generate_bracket(self):
		self.validate_player_count()
		self._ensure_no_existing_matches()

		players = list(self.players)
		# Sort by seed (seeded players first, then by order added)
		players.sort(key=lambda p: (p.seed or 9999, p.idx))

		num_players = len(players)
		total_rounds = int(math.log2(num_players))

		# Create all matches for all rounds
		for round_num in range(1, total_rounds + 1):
			matches_in_round = num_players // (2**round_num)
			for pos in range(1, matches_in_round + 1):
				player_1 = None
				player_2 = None

				# Only assign players to round 1
				if round_num == 1:
					idx1 = (pos - 1) * 2
					idx2 = idx1 + 1
					player_1 = players[idx1].player
					player_2 = players[idx2].player

				# Assign problem from round config if available
				round_entry = next(
					(r for r in self.round_durations if r.round_number == round_num),
					None,
				)
				problem = round_entry.problem if round_entry and round_entry.problem else None
				duration_seconds = round_entry.duration_seconds if round_entry else None

				self._create_match(
					round_number=round_num,
					bracket_position=pos,
					player_1=player_1,
					player_2=player_2,
					problem=problem,
					duration_seconds=duration_seconds,
				)

		self.current_round = 1
		self.status = "Ready"
		self.save()

		frappe.msgprint(f"Bracket generated: {total_rounds} rounds, {num_players - 1} matches")

	@frappe.whitelist()
	def get_bracket_preview(self):
		"""Return shuffled bracket matchups without saving to DB."""
		self.validate_player_count()
		self._ensure_no_existing_matches()

		ordered = self._get_ordered_players_for_bracket()

		num_players = len(ordered)
		total_rounds = int(math.log2(num_players))

		player_id_list = [p.player for p in ordered]
		player_name_rows = frappe.get_all(
			"Codeoff Player",
			filters={"name": ["in", player_id_list]},
			fields=["name", "player_name"],
		)
		player_names = {row.name: row.player_name or row.name for row in player_name_rows}
		# Fallback for any player not returned
		for pid in player_id_list:
			player_names.setdefault(pid, pid)

		preview = []
		for round_num in range(1, total_rounds + 1):
			matches_in_round = num_players // (2**round_num)
			for pos in range(1, matches_in_round + 1):
				m = {
					"round_number": round_num,
					"bracket_position": pos,
					"player_1": None,
					"player_1_name": None,
					"player_2": None,
					"player_2_name": None,
				}
				if round_num == 1:
					idx1 = (pos - 1) * 2
					idx2 = idx1 + 1
					p1_id = ordered[idx1].player
					p2_id = ordered[idx2].player
					m["player_1"] = p1_id
					m["player_1_name"] = player_names[p1_id]
					m["player_2"] = p2_id
					m["player_2_name"] = player_names[p2_id]
				preview.append(m)
		return preview

	@frappe.whitelist()
	def plan_tournament(self):
		self.validate_player_count()
		self._ensure_no_existing_matches()

		ordered = self._get_ordered_players_for_bracket()
		num_players = len(ordered)
		total_rounds = int(math.log2(num_players))
		round_config = self._get_round_config_map()
		problems_by_round = self._assign_random_problems_by_round(total_rounds, num_players)

		created = 0
		for round_num in range(1, total_rounds + 1):
			matches_in_round = num_players // (2**round_num)
			config = round_config.get(round_num)
			for pos in range(1, matches_in_round + 1):
				player_1 = None
				player_2 = None
				if round_num == 1:
					idx1 = (pos - 1) * 2
					idx2 = idx1 + 1
					player_1 = ordered[idx1].player
					player_2 = ordered[idx2].player

				self._create_match(
					round_number=round_num,
					bracket_position=pos,
					player_1=player_1,
					player_2=player_2,
					problem=problems_by_round[round_num][pos - 1],
					duration_seconds=(config.duration_seconds if config else None),
				)
				created += 1

		self.current_round = 1
		self.status = "Ready"
		self.save()

		frappe.msgprint(f"Tournament planned: {created} matches created across {total_rounds} rounds.")
		return {"created": created, "rounds": total_rounds}

	@frappe.whitelist()
	def create_bracket_from_plan(self, plan: str | list[dict]):
		"""Create all bracket matches from planner data in one transaction."""
		self._ensure_no_existing_matches()

		matches_data = json.loads(plan) if isinstance(plan, str) else plan

		for m in matches_data:
			duration_seconds = None
			if m.get("duration_seconds"):
				try:
					duration_seconds = int(m["duration_seconds"])
				except (ValueError, TypeError):
					frappe.throw(f"Invalid duration_seconds value: {m['duration_seconds']!r}")

			self._create_match(
				round_number=int(m["round_number"]),
				bracket_position=int(m["bracket_position"]),
				player_1=m.get("player_1"),
				player_2=m.get("player_2"),
				problem=m.get("problem"),
				duration_seconds=duration_seconds,
			)

		self.current_round = 1
		self.status = "Ready"
		self.save()

		created = len(matches_data)
		frappe.msgprint(f"Tournament planned: {created} matches created.")
		return {"created": created}

	@frappe.whitelist()
	def assign_problems_randomly(self):
		"""Pick a distinct random problem for each round and assign to all its Draft/Ready matches."""
		# Find all rounds that have unassigned (Draft/Ready) matches
		matches = frappe.get_all(
			"Codeoff Match",
			filters={"tournament": self.name, "status": ["in", ["Draft", "Ready"]]},
			fields=["name", "round_number", "player_1", "player_2", "status"],
		)
		if not matches:
			frappe.throw("No Draft/Ready matches found")

		rounds = sorted({m.round_number for m in matches})

		all_problems = frappe.get_all("Codeoff Problem", fields=["name", "title"])
		if len(all_problems) < len(rounds):
			frappe.throw(
				f"Not enough problems ({len(all_problems)}) to assign one per round ({len(rounds)} rounds)"
			)

		selected = random.sample(all_problems, len(rounds))
		round_problem_map = {r: p.name for r, p in zip(rounds, selected, strict=False)}

		for m in matches:
			problem = round_problem_map[m.round_number]
			frappe.db.set_value("Codeoff Match", m.name, "problem", problem)
			if m.status == "Draft" and m.player_1 and m.player_2:
				frappe.db.set_value("Codeoff Match", m.name, "status", "Ready")

		summary = ", ".join(f"Round {r} → {round_problem_map[r]}" for r in rounds)
		frappe.msgprint(f"Problems assigned:<br>{summary.replace(', ', '<br>')}")
		return round_problem_map

	@frappe.whitelist()
	def assign_problem_to_round(self, round_number: int, problem: str):
		"""Assign a problem to all Draft/Ready matches in a given round."""
		matches = frappe.get_all(
			"Codeoff Match",
			filters={
				"tournament": self.name,
				"round_number": int(round_number),
				"status": ["in", ["Draft", "Ready"]],
			},
			fields=["name"],
		)
		if not matches:
			frappe.throw(f"No Draft/Ready matches found in Round {round_number}")

		for m in matches:
			frappe.db.set_value("Codeoff Match", m.name, "problem", problem)
			# Re-run status transition: Draft → Ready if players are also set
			match_doc = frappe.get_doc("Codeoff Match", m.name)
			if match_doc.status == "Draft" and match_doc.player_1 and match_doc.player_2:
				match_doc.status = "Ready"
				match_doc.save(ignore_permissions=True)

		frappe.msgprint(f"Problem '{problem}' assigned to {len(matches)} match(es) in Round {round_number}")

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
					"status": "Draft",
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

	@frappe.whitelist()
	def clear_tournament_data(self):
		"""Delete all runtime data for this tournament while keeping tournament configuration."""
		matches = frappe.get_all(
			"Codeoff Match",
			filters={"tournament": self.name},
			fields=["name"],
			order_by="round_number desc, bracket_position desc",
		)
		match_names = [m.name for m in matches]

		submissions_deleted = 0
		draft_states_deleted = 0
		matches_deleted = 0

		if match_names:
			submissions = frappe.get_all(
				"Codeoff Submission", filters={"match": ["in", match_names]}, pluck="name"
			)
			for sub in submissions:
				frappe.delete_doc("Codeoff Submission", sub, ignore_permissions=True)
			submissions_deleted = len(submissions)

			draft_states = frappe.get_all(
				"Codeoff Draft State", filters={"match": ["in", match_names]}, pluck="name"
			)
			for draft_state in draft_states:
				frappe.delete_doc("Codeoff Draft State", draft_state, ignore_permissions=True)
			draft_states_deleted = len(draft_states)

			for match_name in match_names:
				frappe.cache.delete_keys(f"codeoff_draft:{match_name}:")
				frappe.delete_doc("Codeoff Match", match_name, ignore_permissions=True)
			matches_deleted = len(match_names)

		for player in self.players:
			player.status = "Registered"

		self.current_round = None
		self.started_on = None
		self.completed_on = None
		self.status = "Draft"
		self.save(ignore_permissions=True)
		frappe.db.commit()

		frappe.msgprint(
			f"Cleared {matches_deleted} match(es), {submissions_deleted} submission(s), "
			f"and {draft_states_deleted} draft state record(s) for tournament {self.name}."
		)
		return {
			"matches_deleted": matches_deleted,
			"submissions_deleted": submissions_deleted,
			"draft_states_deleted": draft_states_deleted,
		}
