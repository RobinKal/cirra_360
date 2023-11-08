frappe.listview_settings['Client Event'] = {
	onload: function(listview) {
		listview.filter_area.clear();
		listview.filter_area.add([[listview.doctype, "_assign", 'like',  '%' + frappe.session.user + '%']]);
	}
}