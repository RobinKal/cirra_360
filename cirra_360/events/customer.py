import frappe
from frappe.model.document import Document

def on_customer_on_save(doc, method):
	if doc.user_creation_info:
		for row in doc.user_creation_info:
			create_user(row)

def create_user(row):
	if not frappe.db.exists("User", row.email_id):
		user_list_doc = frappe.new_doc('User')
		user_list_doc.first_name=row.first_name
		user_list_doc.last_name=row.last_name
		user_list_doc.email=row.email_id
		user_list_doc.role=row.role
		user_list_doc.insert()
	else:
		user_doc = frappe.get_doc("User", row.email_id)
		user_doc.first_name=row.first_name
		user_doc.last_name=row.last_name
		user_doc.save()