frappe.ui.form.on('Codeoff Tournament', {
	refresh(frm) {
		if (
			frm.doc.current_round &&
			!['Completed', 'Cancelled', 'Draft'].includes(frm.doc.status)
		) {
			frm.add_custom_button(
				__('Start Round {0}', [frm.doc.current_round]),
				() => {
					frappe.confirm(
						__('Start all Ready matches in Round {0}?', [frm.doc.current_round]),
						() => frm.call('start_round').then(() => frm.reload_doc()),
					)
				},
				__('Actions'),
			)
		}
	},
})
