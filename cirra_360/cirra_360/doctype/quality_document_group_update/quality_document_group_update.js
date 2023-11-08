// Copyright (c) 2021, sujay and contributors
// For license information, please see license.txt


frappe.ui.form.on('Quality Document Group Update', {
	refresh: function() {

	},

	onload: function (frm) {
		frm.set_value("naming_series", "UPDATE-.quality_document_group.-.YY.MM.DD.-.####");
	},

	validate: function (frm) {
		frm.set_value("time", frappe.datetime.now_time());
		frm.set_value("date", frappe.datetime.nowdate());
	}
});
