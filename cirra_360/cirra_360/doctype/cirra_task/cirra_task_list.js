frappe.listview_settings['Cirra Task'] = {
	add_fields: ["status"],
    has_indicator_for_draft: 1,
	get_indicator: function(doc) {
		return [__(doc.status), {
			"Transmitted to ASN": "green",
			"Processing Report": "orange",
			"In Progress": "orange",
			"Done": "green",
            "Overdue": "red"
		}[doc.status]];
	},
	onload: function(listview) {
		console.log(listview)
		listview.filter_area.clear();
		listview.filter_area.add([[listview.doctype, "_assign", 'like',  '%' + frappe.session.user + '%']]);
	}
};