# Copyright (c) 2022, sujay and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class QualityActionPlan(Document):
	@frappe.whitelist()
	def set_status(self,status):
		self.status = status
		if status == "Completed":
			self.update_event_status()
		self.save()
	
	def update_event_status(self):
		events = frappe.get_all("Client Event",filters={"quality_action_plan":self.name},fields=["name"])
		for row in events:
			event_doc = frappe.get_doc("Client Event",row.name)
			event_doc.status = "Completed"
			event_doc.save()
	

	def validate_dates(self):
			if self.start_date and self.end_date and getdate(self.start_date) > getdate(self.end_date):
				frappe.throw(_("{0} can not be greater than {1}").format(frappe.bold("Start Date"), \
					frappe.bold("End Date")))
