frappe.ui.form.on("Codeoff Submission", {
	refresh(frm) {
		if (!frm.is_new()) {
			frm.add_custom_button(__("Judge"), () => {
				frm.call("judge").then(() => frm.reload_doc());
			});
		}
	},
});
