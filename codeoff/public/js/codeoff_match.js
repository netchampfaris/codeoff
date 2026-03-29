frappe.ui.form.on('Codeoff Match', {
	refresh(frm) {
		if (frm.doc.status === 'Review') {
			frm.add_custom_button(
				__('Create Rematch'),
				() => {
					frappe.confirm(
						__('Create a rematch for this bracket slot using a different problem?'),
						() => {
							frm.call('create_rematch').then((response) => {
								const rematchId = response.message?.rematch_match_id
								if (rematchId) {
									frappe.set_route('Form', 'Codeoff Match', rematchId)
									return
								}
								frm.reload_doc()
							})
						},
					)
				},
				__('Actions'),
			)
		}

		if (['Live', 'Review'].includes(frm.doc.status)) {
			frm.add_custom_button(
				__('Set Winner'),
				() => {
					const playerIds = [frm.doc.player_1, frm.doc.player_2].filter(Boolean)
					frappe.db
						.get_list('Codeoff Player', {
							filters: [['name', 'in', playerIds]],
							fields: ['name', 'player_name'],
						})
						.then((players) => {
							const nameToId = {}
							players.forEach((p) => {
								nameToId[p.player_name || p.name] = p.name
							})
							frappe.prompt(
								{
									label: __('Winner'),
									fieldname: 'winner',
									fieldtype: 'Select',
									options: Object.keys(nameToId).join('\n'),
									reqd: 1,
								},
								({ winner }) => {
									frm
										.call('force_finish', { winner_player: nameToId[winner] })
										.then(() => frm.reload_doc())
								},
								__('Set Match Winner'),
								__('Confirm'),
							)
						})
				},
				__('Actions'),
			)
		}

		if (frm.doc.status !== 'Draft') {
			frm.add_custom_button(
				__('Reset Match'),
				() => {
					frappe.confirm(
						__(
							'Reset this match? All submissions will be deleted and the match will return to Ready state.',
						),
						() => frm.call('reset_match').then(() => frm.reload_doc()),
					)
				},
				__('Actions'),
			)
		}
	},
})
