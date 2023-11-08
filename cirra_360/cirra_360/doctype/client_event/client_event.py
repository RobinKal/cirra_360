# Copyright (c) 2022, sujay and contributors
# For license information, please see license.txt

from genericpath import exists
import frappe
from frappe.model.document import Document
from frappe.utils import cint, cstr,today,add_days,add_months


class ClientEvent(Document):
	def validate(self):
		self.create_task()
		self.update_status()

	def after_insert(self):
		self.create_task()

	def create_task(self):
		if not self.get("__islocal") \
			and not frappe.db.exists("Cirra Task",{"client_event":self.name}) \
			and self.type_of_event == "Significant" \
			and self.event_category == "Significant Radiation Protection Event (ESR)":
			_create_task(self, "ASN Submission","Hour")
			_create_task(self, "CRES ASN","Month")
		if not self.get("__islocal") \
			and not frappe.db.exists("Cirra Task",{"client_event":self.name}) \
			and self.type_of_event == "Significant" \
			and self.event_category == "Serious adverse event (EIG)":
			_create_task(self, "EIGS1","Hour")
			_create_task(self, "EIGS2","Month")

	def update_status(self):
		# if self.type_of_event == "Non Significant":
		# 	if self.analysis_required:
		# 		self.status = "Kept For Analysis"
		# 	else:
		# 		self.status = "Analysis Not Required"
		# if self.type_of_event == "Significant" and not self.status in ["Processing Report","Transmitted to ASN"]:
		# 	if self.event_category == "Serious adverse event":
		# 		self.status = "Kept For Meeting"
		# 	if self.event_category == "Significant Radiation Protection Event":
		# 		self.status = "To Be Analysed"
		# 		self.action_should_taken_in_hours = 48
		if not self.status == "Completed":
			if self.type_of_event == "Significant" or self.crex_meeting == "Yes":
				self.status = "Retained for Meeting"
				self.crex_meeting = "Yes"
			if self.crex_meeting == "No":
				self.status = "No Analysis Required"
		self.notify_update()

	@frappe.whitelist()
	def set_status(self, status):
		self.status = status
		self.save()
		self.notify_update()


'''update client event 48 hours cron job and send email if there is no any activiy'''
def update_action_hours_cron():
	client_event = frappe.get_all("Client Event", filters={
								  "status": "To Be Analysed"}, fields=["*"])
	for row in client_event:
		print(row.name)
		if int(row.get('action_should_taken_in_hours')) > 0:
			hours_passed = cint(row.get('hours_passed')) or 0
			hours_passed += 1
			frappe.db.set_value("Client Event", row.name,
								"hours_passed", cstr(hours_passed))
			if row.get('action_should_taken_in_hours') == hours_passed:
				event_doc = frappe.get_doc("Client Event", row.name)
				event_doc.no_action_taken = 1
				event_doc.save()
				event_doc.notify_update()


'''create task from event'''
def _create_task(doc, task_name,action_type):
	task_doc = frappe.new_doc("Cirra Task")
	task_doc.status = "To be Analysed"
	task_doc.task_name = task_name + "-" + doc.event_name
	task_doc.task_type_custom = task_name
	task_doc.start_date = today()
	task_doc.action_taken = action_type
	if action_type == "Hour":
		task_doc.end_date = add_days(today(),2)
		task_doc.action_taken_in_hours = 48
		task_doc.hour_passed = 0
	if action_type == "Month":
		if task_name == "EIGS2":
			task_doc.end_date = add_months(today(),3)
		else:
			task_doc.end_date = add_months(today(),2)
		task_doc.action_taken_before_date = task_doc.end_date
	task_doc.task_type = "Event"
	task_doc.type_of_event = doc.type_of_event
	task_doc.event_category = doc.event_category
	task_doc.client_event = doc.name
	task_doc.insert(ignore_permissions=True)
