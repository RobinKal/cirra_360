frappe.listview_settings['Quality Document Group'] = {
	add_fields: ["status", "priority", "is_active", "percent_complete", "expected_end_date", "quality_document_group_name"],
	filters:[["status","=", "Open"]],
	has_indicator_for_draft: 1,
	get_indicator: function(doc) {
		return [__(doc.status), {
			"Draft": "yellow",
			"Open": "green",
			"Completed": "gray",
            "Cancelled": "red"
		}[doc.status]];
	},
};
