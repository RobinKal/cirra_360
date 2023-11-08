import frappe
from frappe import _
from frappe.model.document import Document

def on_update_employee(doc, method):
	for row in doc.customer:
		if not doc.user_id:
			if not doc.personal_email:
				frappe.throw("Personal Email is Required for User Creation.")
			create_user(doc.first_name, doc.last_name, doc.personal_email)
			doc.user_id = doc.personal_email
		customer_doc = frappe.get_doc("Customer", row.customers)
		employee_exist = False
		for user in customer_doc.user_creation_info:
			if user.email_id == doc.user_id:
				employee_exist = True
				user.first_name = doc.first_name
				user.last_name = doc.last_name
		if not employee_exist:
			customer_doc.append("user_creation_info", dict(
				first_name = doc.first_name,
				last_name = doc.last_name,
				email_id = doc.user_id
			))
		customer_doc.save()
		frappe.db.set_value(doc.doctype, doc.name,"user_id",doc.user_id)
	# for remove employee from customer
	remove_employee_from_customer(doc)

def remove_employee_from_customer(doc):
	if doc.user_id:
		customer_list = [row.customers for row in doc.customer]
		filters = [["User Creation Info","email_id","=",doc.user_id],["name","not in",customer_list]]
		customers = frappe.get_all("Customer", filters = filters, fields = ["name"])
		for customer in customers:
			customer_doc = frappe.get_doc("Customer", customer.name)
			for user in customer_doc.user_creation_info:
				if user.email_id == doc.user_id:
					customer_doc.user_creation_info.remove(user)
					customer_doc.save()

def create_user(first_name, last_name = None, personal_email = None):
	if not frappe.db.exists("User", personal_email):
		user_list_doc = frappe.new_doc('User')
		user_list_doc.first_name=first_name
		user_list_doc.last_name=last_name
		user_list_doc.email=personal_email
		user_list_doc.insert()
	else:
		user_doc = frappe.get_doc("User", personal_email)
		user_doc.first_name=first_name
		user_doc.last_name=last_name
		user_doc.save()