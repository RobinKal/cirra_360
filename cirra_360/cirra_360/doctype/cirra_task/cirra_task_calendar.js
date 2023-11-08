frappe.views.calendar["Cirra Task"] = {
	field_map: {
		"start": "start_date",
		"end": "end_date",
		"id": "name",
		"title": "task_name",
		"allDay": "allDay"
	},
	gantt: true,
	get_events_method: "frappe.desk.calendar.get_events",
}