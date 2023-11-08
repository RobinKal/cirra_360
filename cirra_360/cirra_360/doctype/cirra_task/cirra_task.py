# Copyright (c) 2022, sujay and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import cint,cstr,today
from frappe.utils.file_manager import download_file
from frappe import _
from frappe.model.naming import make_autoname


class CirraTask(Document):
	def autoname(self):
		name = 'TACHE'
		if self.task_type == "Event":
			if self.task_type_custom in ["ASN Submission","CRES ASN"]:
				name += "-ESR"
			if self.task_type_custom in ["EIGS1","EIGS2"]:
				name += "-EIG"
		name += '-.YYYY.-.#####'
		self.name = make_autoname(name)

	def validate(self):
		if self.get("__islocal") and self.get('task_type') == "Corrective action":
			self.status == "Not Started"

	@frappe.whitelist()
	def set_status(self,status):
		self.status = status
		self.save()
		self.notify_update()

	@frappe.whitelist()
	def download_file_data(self):
		task_type_field_map  = {"ASN Submission":"esr_decalre","CRES ASN":"cres_report","EIGS2":"egis_step2","EIGS1":"egis_step1"}
		if task_type_field_map.get(self.task_type_custom):
			file_name = frappe.db.get_value("File",{"attached_to_name":"Cirra Setting","attached_to_field":task_type_field_map.get(self.task_type_custom)},"file_url")
			return file_name

	@frappe.whitelist()
	def submit_to(self):
		task_category_field_map = {"Serious adverse event (EIG)":"eig_link","Significant Radiation Protection Event (ESR)":"esr_link"}
		if task_category_field_map.get(self.event_category):
			url = frappe.db.get_value("Cirra Setting","Cirra Setting",task_category_field_map.get(self.event_category))
			return url
		frappe.throw(_("Set Link In Cirra Setting First"))

'''update cirra task 48 hours cron job and send email if there is no any activiy'''
def update_action_hours_cron():
	cirra_tasks = frappe.get_all("Cirra Task", filters={
								  "status": "To Be Analysed","action_taken":"Hour"}, fields=["*"])
	for row in cirra_tasks:
		if int(row.get('action_taken_in_hours')) > 0:
			hours_passed = cint(row.get('hour_passed')) or 0
			hours_passed += 1
			frappe.db.set_value("Cirra Task", row.name,
								"hour_passed", cstr(hours_passed))
			if row.get('action_taken_in_hours') == hours_passed:
				task_doc = frappe.get_doc("Cirra Task", row.name)
				task_doc.status = "Overdue"
				task_doc.save()

def update_action_daily_cron():
	cirra_tasks = frappe.get_all("Cirra Task", filters={
								  "status": "To Be Analysed","action_taken":"Month","action_taken_before_date":today()}, fields=["*"])
	for row in cirra_tasks:
		task_doc = frappe.get_doc("Cirra Task", row.name)
		task_doc.status = "Overdue"
		task_doc.save()
