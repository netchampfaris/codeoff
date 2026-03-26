frappe.listview_settings["Codeoff Problem"] = {
	onload(listview) {
		listview.page.add_button("Import from JSON", () => {
			const input = document.createElement("input");
			input.type = "file";
			input.accept = ".json";
			input.addEventListener("change", async () => {
				const file = input.files[0];
				if (!file) return;

				const json_data = await file.text();

				frappe.show_alert({ message: `Importing ${file.name}…`, indicator: "blue" });

				frappe.call({
					method: "codeoff.load_problems.import_from_json",
					args: { json_data },
					callback({ message }) {
						frappe.show_alert({
							message: `Done — ${message.created} created, ${message.skipped} skipped.`,
							indicator: "green",
						});
						listview.refresh();
					},
				});
			});
			input.click();
		});
	},
};
