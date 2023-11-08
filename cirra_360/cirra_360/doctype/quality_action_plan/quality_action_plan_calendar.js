// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.views.calendar["Quality Action Plan"] = {
	field_map: {
		"start": "start_date",
		"end": "end_date",
		"id": "name",
	},
	gantt: true,
	filters: [
		{
			"fieldtype": "Link",
			"fieldname": "quality_action_plan",
			"options": "Quality Action Plan",
			"label": __("Quality Action Plan")
		}
	],
	get_events_method: "frappe.desk.calendar.get_events"
}
