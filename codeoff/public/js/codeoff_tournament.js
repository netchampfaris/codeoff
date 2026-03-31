frappe.ui.form.on("Codeoff Tournament", {
	refresh(frm) {
		// Plan Tournament — opens the planner dialog (before bracket is created)
		if (frm.doc.players?.length >= 2 && frm.doc.status === "Draft") {
			frm.add_custom_button(__("Plan Tournament"), () => openPlanner(frm), __("Actions"));
		}

		// Assign Problem to Round — after bracket exists
		if (!["Draft", "Completed", "Cancelled"].includes(frm.doc.status)) {
			frm.add_custom_button(
				__("Assign Problem to Round"),
				() => {
					frappe.prompt(
						[
							{
								fieldname: "round_number",
								fieldtype: "Int",
								label: __("Round Number"),
								default: frm.doc.current_round || 1,
								reqd: 1,
							},
							{
								fieldname: "problem",
								fieldtype: "Link",
								label: __("Problem"),
								options: "Codeoff Problem",
								reqd: 1,
							},
						],
						(values) => {
							frm.call("assign_problem_to_round", {
								round_number: values.round_number,
								problem: values.problem,
							}).then(() => frm.reload_doc());
						},
						__("Assign Problem to Round")
					);
				},
				__("Actions")
			);
		}

		if (
			frm.doc.current_round &&
			!["Completed", "Cancelled", "Draft"].includes(frm.doc.status)
		) {
			frm.add_custom_button(
				__("Start Round {0}", [frm.doc.current_round]),
				() => {
					frappe.confirm(
						__("Start all Ready matches in Round {0}?", [frm.doc.current_round]),
						() => frm.call("start_round").then(() => frm.reload_doc())
					);
				},
				__("Actions")
			);
		}

		if (!frm.is_new()) {
			frm.add_custom_button(
				__("Clear Tournament Data"),
				() => {
					frappe.confirm(
						__(
							"This will permanently delete all matches, submissions, and draft states for this tournament and reset it to Draft. Player entries and round settings will be kept. Continue?"
						),
						() => frm.call("clear_tournament_data").then(() => frm.reload_doc())
					);
				},
				__("Actions")
			);
		}
	},
});

async function openPlanner(frm) {
	// frappe.show_progress(__('Building bracket...'), 0, 100)
	let r;
	try {
		r = await frm.call("get_bracket_preview");
	} finally {
		// frappe.hide_progress()
	}
	if (!r?.message?.length) return;
	showPlannerDialog(frm, r.message);
}

function showPlannerDialog(frm, matches) {
	const defaultDuration = frm.doc.match_duration_seconds || 1800;

	// Group matches by round
	const byRound = {};
	for (const m of matches) {
		(byRound[m.round_number] = byRound[m.round_number] || []).push(m);
	}

	// Dynamically build frappe dialog fields: 2 matches per row via column breaks
	const fields = [];
	for (const roundNum of Object.keys(byRound)
		.map(Number)
		.sort((a, b) => a - b)) {
		const roundMatches = byRound[roundNum];

		for (let i = 0; i < roundMatches.length; i++) {
			const m = roundMatches[i];

			if (i === 0) {
				// Start a labelled section for this round
				fields.push({
					fieldtype: "Section Break",
					label: `Round ${roundNum}`,
					fieldname: `section_r${roundNum}_row0`,
				});
			} else if (i % 2 === 1) {
				// Odd index within round → right column of current row
				fields.push({ fieldtype: "Column Break" });
			} else {
				// Even index > 0 → start a new unlabelled row within the round
				fields.push({
					fieldtype: "Section Break",
					label: "",
					fieldname: `section_r${roundNum}_row${i}`,
				});
			}

			// Player display
			let playersHtml;
			if (m.player_1_name) {
				playersHtml = `<b>${m.player_1_name}</b> <span class="text-muted">vs</span> <b>${m.player_2_name}</b>`;
			} else {
				const f1 = (m.bracket_position - 1) * 2 + 1;
				const f2 = (m.bracket_position - 1) * 2 + 2;
				playersHtml = `<span class="text-muted">Winner M${f1} vs Winner M${f2}</span>`;
			}
			fields.push({
				fieldtype: "HTML",
				fieldname: `players_r${roundNum}_p${m.bracket_position}`,
				options: `<div class="mb-1 small">Match ${m.bracket_position} &nbsp;·&nbsp; ${playersHtml}</div>`,
			});
			fields.push({
				fieldtype: "Link",
				fieldname: `problem_r${roundNum}_p${m.bracket_position}`,
				label: __("Problem"),
				options: "Codeoff Problem",
			});
			fields.push({
				fieldtype: "Int",
				fieldname: `duration_r${roundNum}_p${m.bracket_position}`,
				label: __("Duration (s)"),
			});
		}
	}

	const d = new frappe.ui.Dialog({
		title: __("Tournament Planner"),
		size: "large",
		fields,
		primary_action_label: __("Create Matches"),
		primary_action(values) {
			const plan = matches.map((m) => ({
				round_number: m.round_number,
				bracket_position: m.bracket_position,
				player_1: m.player_1 || null,
				player_2: m.player_2 || null,
				problem: values[`problem_r${m.round_number}_p${m.bracket_position}`] || null,
				duration_seconds:
					values[`duration_r${m.round_number}_p${m.bracket_position}`] ||
					defaultDuration,
			}));
			frm.call("create_bracket_from_plan", { plan: JSON.stringify(plan) }).then(() => {
				d.hide();
				frm.reload_doc();
			});
		},
		secondary_action_label: __("Re-shuffle"),
		secondary_action() {
			d.hide();
			openPlanner(frm);
		},
	});

	// Set default durations after dialog is created
	matches.forEach((m) => {
		d.set_value(`duration_r${m.round_number}_p${m.bracket_position}`, defaultDuration);
	});

	d.show();
}
