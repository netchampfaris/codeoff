frappe.ui.form.on("Codeoff Tournament", {
	refresh(frm) {
		// Plan Tournament — creates brackets, matches, and per-match problems from round settings.
		if (frm.doc.players?.length >= 2 && frm.doc.status === "Draft") {
			frm.add_custom_button(
				__("Plan Tournament"),
				() => {
					frappe.confirm(
						__(
							"This will create the tournament bracket, create matches, and assign random problems using each round's configured difficulty. Continue?"
						),
						() => frm.call("plan_tournament").then(() => frm.reload_doc())
					);
				},
				__("Actions")
			);
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
