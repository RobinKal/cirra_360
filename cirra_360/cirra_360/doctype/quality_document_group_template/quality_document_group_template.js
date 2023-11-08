// Copyright (c) 2021, sujay and contributors
// For license information, please see license.txt


frappe.ui.form.on('Quality Document Group Template', {
	// refresh: function(frm) {

	// }
	setup: function (frm) {
		frm.set_query("quality_document", "quality_documents", function () {
			return {
				filters: {
					"is_template": 1
				}
			};
		});
	}
});

frappe.ui.form.on('Quality Document Template', {
	quality_document: function (frm, cdt, cdn) {
		// console.log('test1')
		// var row = locals[cdt][cdn];
		// frappe.db.get_value("Quality Document", row.quality_document, "subject", (value) => {
		// 	row.subject = value.subject;
		// 	refresh_field("quality_documents");
		// });
	}
});

