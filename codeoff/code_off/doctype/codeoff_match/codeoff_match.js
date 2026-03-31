// Copyright (c) 2026, Frappe and contributors
// For license information, please see license.txt

frappe.ui.form.on("Codeoff Match", {
	refresh(frm) {
		if (frm.doc.status === "Live") {
			frm.add_custom_button("Add Time", () => {
				frappe.prompt(
					{
						label: "Seconds to add",
						fieldname: "seconds",
						fieldtype: "Int",
						default: 60,
						reqd: 1,
					},
					({ seconds }) => {
						frm.call("add_time", { seconds }).then(() => frm.reload_doc());
					},
					"Add Time to Match",
					"Add"
				);
			});

			frm.add_custom_button("Judge Now", () => {
				frappe.confirm(
					"Run match resolution synchronously? Use this if the background job didn't fire.",
					() => frm.call("resolve_now").then(() => frm.reload_doc())
				);
			});
		}
	},
});
