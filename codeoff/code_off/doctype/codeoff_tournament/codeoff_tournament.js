// Copyright (c) 2026, Code Off and contributors
// For license information, please see license.txt

frappe.ui.form.on("Codeoff Tournament", {
	refresh(frm) {
		if (!frm.is_new()) {
			frm.add_custom_button(__("Finish Round (Random Winners)"), () => {
				frappe.confirm(
					`Randomly pick winners for all active matches in round ${frm.doc.current_round}?`,
					() => {
						frm.call("finish_round_with_random_winners").then(() => frm.reload_doc());
					}
				);
			}, __("Testing"));

			frm.add_custom_button(__("Reset All Matches"), () => {
				frappe.confirm(
					"This will delete all submissions and reset every match to its initial state. Continue?",
					() => {
						frm.call("reset_all_matches").then(() => frm.reload_doc());
					}
				);
			}, __("Testing"));
		}
	},
});
