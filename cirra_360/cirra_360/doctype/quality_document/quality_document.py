# Copyright (c) 2021, sujay and contributors
# For license information, please see license.txt

# import frappe
#from frappe.model.document import Document
#class QualityDocument(Document):
#	pass
	

from dataclasses import fields
import json
import frappe
from frappe import _, throw
from frappe.desk.form.assign_to import clear, close_all_assignments
from frappe.model.mapper import get_mapped_doc
from frappe.utils import add_days, cstr, date_diff, flt, get_link_to_form, getdate, today, flt, add_months
from frappe.utils.nestedset import NestedSet
from bs4 import BeautifulSoup
from whoosh.fields import ID, TEXT, Schema
from frappe.search.full_text_search import FullTextSearch
from frappe.utils import set_request, update_progress_bar,strip_html_tags
from frappe.model.naming import make_autoname
INDEX_NAME = "quality_document"

class CircularReferenceError(frappe.ValidationError): pass
class EndDateCannotBeGreaterThanQualityDocumentGroupEndDateError(frappe.ValidationError): pass

class QualityDocumentFT(FullTextSearch):
	nsm_parent_field = 'parent_quality_document'
	
	def get_schema(self):
		return Schema(
			name=ID(stored=True), content=TEXT(stored=True)
		)

	def get_fields_to_search(self):
		return ["name","content"]

	def get_id(self):
		return "name"

	def get_items_to_index(self):
		docs = []
		q_d_list = frappe.get_all("Quality Document",filters={},fields=["name","quality_document"])
		for row in q_d_list:
			docs.append(self.get_document_to_index(row.name,row.quality_document))
		return docs

	def get_document_to_index(self,q_id,q_content):
		return frappe._dict(name=q_id, content=q_content)

	def parse_result(self, result):
		title_highlights = result.highlights("title")
		content_highlights = result.highlights("content")

		return frappe._dict(
			title=result["title"],
			name=result["name"],
			title_highlights=title_highlights,
			content_highlights=content_highlights,
		)

def build_index_for_all_documents():
	search = QualityDocumentFT(INDEX_NAME)
	return search.build()

class QualityDocument(NestedSet):
	nsm_parent_field = 'parent_quality_document'

	def autoname(self):
		series = self.shortcode + '-' + self.quality_document_type + '-' + '.YYYY.-.#####'
		def quality_document_parent(series,quality_document):
			shortcode = frappe.db.get_value("Quality Document",quality_document,"shortcode")
			if shortcode:
				series = shortcode + '-' + series
			parent_quality_document = frappe.db.get_value("Quality Document",quality_document,"parent_quality_document")
			if parent_quality_document:
				series = quality_document_parent(series,parent_quality_document)
			return series
		if self.parent_quality_document:
			series = quality_document_parent(series,self.parent_quality_document)
		self.name = make_autoname(series)

	def get_feed(self):
		return '{0}: {1}'.format(_(self.status), self.subject)

	def get_customer_details(self):
		cust = frappe.db.sql("select customer_name from `tabCustomer` where name=%s", self.customer)
		if cust:
			ret = {'customer_name': cust and cust[0][0] or ''}
			return ret

	def validate(self):
		self.validate_dates()
		#self.validate_parent_expected_end_date()
		#self.validate_parent_quality_document_group_dates()
		#self.validate_progress()
		self.validate_status()
		#self.update_depends_on()
		self.validate_dependencies_for_template_quality_document()
		#self.validate_completed_on()
		self.validate_workflow_permissions()
		self.update_version()
		self.set_verifier_and_approver()
		# ws = QualityDocumentFT(INDEX_NAME)
		# return ws.update_index_by_name(self.name)

	def validate_dates(self):
		if self.exp_start_date and self.exp_end_date and getdate(self.exp_start_date) > getdate(self.exp_end_date):
			frappe.throw(_("{0} can not be greater than {1}").format(frappe.bold("Expected Start Date"), \
				frappe.bold("Expected End Date")))


	"""def validate_parent_expected_end_date(self):
		if self.parent_quality_document:
			parent_exp_end_date = frappe.db.get_value("Quality Document", self.parent_quality_document, "exp_end_date")
			if parent_exp_end_date and getdate(self.get("exp_end_date")) > getdate(parent_exp_end_date):
				frappe.throw(_("Expected End Date should be less than or equal to parent quality_document's Expected End Date {0}.").format(getdate(parent_exp_end_date)))"""

	#def validate_parent_quality_document_group_dates(self):
	#	if not self.quality_document_group or frappe.flags.in_test:
	#		return

	#	expected_end_date = frappe.db.get_value("Quality Document Group", self.quality_document_group, "expected_end_date")

	#	if expected_end_date:
	#		validate_quality_document_group_dates(getdate(expected_end_date), self, "exp_start_date", "exp_end_date", "Expected")
	#		validate_quality_document_group_dates(getdate(expected_end_date), self, "act_start_date", "act_end_date", "Actual") 

	def validate_status(self):
		if self.is_template and self.status != "Template":
			self.status = "Template"
		if self.status!=self.get_db_value("status") and self.status == "Completed":
			for d in self.depends_on:
				if frappe.db.get_value("Quality Document", d.quality_document, "status") not in ("Completed", "Cancelled"):
					frappe.throw(_("Cannot complete quality_document {0} as its dependant quality_document {1} are not ccompleted / cancelled.").format(frappe.bold(self.name), frappe.bold(d.quality_document)))

			close_all_assignments(self.doctype, self.name)

	"""def validate_progress(self):
		if flt(self.progress or 0) > 100:
			frappe.throw(_("Progress % for a quality_document cannot be more than 100."))

		if flt(self.progress) == 100:
			self.status = 'Completed'

		if self.status == 'Completed':
			self.progress = 100 """

	def validate_dependencies_for_template_quality_document(self):
		if self.is_template:
			self.validate_parent_template_quality_document()
			self.validate_depends_on_quality_documents()

	def validate_parent_template_quality_document(self):
		if self.parent_quality_document:
			if not frappe.db.get_value("Quality Document", self.parent_quality_document, "is_template"):
				parent_quality_document_format = """<a href="#Form/Quality Document/{0}">{0}</a>""".format(self.parent_quality_document)
				frappe.throw(_("Parent Quality Document {0} is not a Template Quality Document").format(parent_quality_document_format))

	def validate_depends_on_quality_documents(self):
		if self.depends_on:
			for quality_document in self.depends_on:
				if not frappe.db.get_value("Quality Document", quality_document.quality_document, "is_template"):
					dependent_quality_document_format = """<a href="#Form/Quality Document/{0}">{0}</a>""".format(quality_document.quality_document)
					frappe.throw(_("Dependent Quality Document {0} is not a Template Quality Document").format(dependent_quality_document_format))

	#def validate_completed_on(self):
	#	if self.completed_on and getdate(self.completed_on) > getdate():
	#		frappe.throw(_("Completed On cannot be greater than Today"))

	def update_depends_on(self):
		depends_on_quality_documents = self.depends_on_quality_documents or ""
		for d in self.depends_on:
			if d.quality_document and d.quality_document not in depends_on_quality_documents:
				depends_on_quality_documents += d.quality_document + ","
		self.depends_on_quality_documents = depends_on_quality_documents

	def update_nsm_model(self):
		frappe.utils.nestedset.update_nsm(self)

	def on_update(self):
		self.update_nsm_model()
		self.check_recursion()
		#self.reschedule_dependent_quality_documents()
		#self.update_quality_document_group()
		self.unassign_todo()
		self.populate_depends_on()

	def unassign_todo(self):
		if self.status == "Completed":
			close_all_assignments(self.doctype, self.name)
		if self.status == "Cancelled":
			clear(self.doctype, self.name)

	#def update_total_expense_claim(self):
	#	self.total_expense_claim = frappe.db.sql("""select sum(total_sanctioned_amount) from `tabExpense Claim`
	#		where quality_document_group = %s and quality_document = %s and docstatus=1""",(self.quality_document_group, self.name))[0][0]

	# def update_time_and_costing(self):
	#	tl = frappe.db.sql("""select min(from_time) as start_date, max(to_time) as end_date,
	#		sum(billing_amount) as total_billing_amount, sum(costing_amount) as total_costing_amount,
	#		sum(hours) as time from `tabTimesheet Detail` where quality_document = %s and docstatus=1"""
	#		,self.name, as_dict=1)[0]
	#	if self.status == "Open":
	#		self.status = "Working"
	#	self.total_costing_amount= tl.total_costing_amount
	#	self.total_billing_amount= tl.total_billing_amount
	#	self.actual_time= tl.time
	#	self.act_start_date= tl.start_date
	#	self.act_end_date= tl.end_date 

	#def update_quality_document_group(self):
	#	if self.quality_document_group and not self.flags.from_quality_document_group:
	#		frappe.get_cached_doc("Quality Document Group", self.quality_document_group).update_quality_document_group()

	def check_recursion(self):
		if self.flags.ignore_recursion_check: return
		check_list = [['quality_document', 'parent'], ['parent', 'quality_document']]
		for d in check_list:
			quality_document_list, count = [self.name], 0
			while (len(quality_document_list) > count ):
				quality_documents = frappe.db.sql(" select %s from `tabQuality Document Depends On` where %s = %s " %
					(d[0], d[1], '%s'), cstr(quality_document_list[count]))
				count = count + 1
				for b in quality_documents:
					if b[0] == self.name:
						frappe.throw(_("Circular Reference Error"), CircularReferenceError)
					if b[0]:
						quality_document_list.append(b[0])

				if count == 15:
					break

	
	def has_webform_permission(self):
		quality_document_group_user = frappe.db.get_value("Quality User", {"parent": self.Quality, "user":frappe.session.user} , "user")
		if quality_document_group_user:
			return True

	def populate_depends_on(self):
		if self.parent_quality_document:
			parent = frappe.get_doc('Quality Document', self.parent_quality_document)
			if self.name not in [row.quality_document for row in parent.depends_on]:
				parent.append("depends_on", {
					"doctype": "Quality Document Depends On",
					"quality_document": self.name,
					"subject": self.subject
				})
				parent.save()

	def on_trash(self):
		if check_if_child_exists(self.name):
			throw(_("Child Quality Document exists for this Quality Document. You can not delete this Quality Document."))

		self.update_nsm_model()

	#def after_delete(self):
	#	self.update_quality_document_group()
	
	def before_insert(self):
		self.version = 1.0
	
	def update_version(self):
		if self.workflow_state == "Being Updated" and self.version_check == False:
			self.version = cstr(round(flt(self.version) + 0.5, 1))
			self.version_check = True
		if not self.workflow_state == "Being Updated":
			self.version_check = False

	def set_verifier_and_approver(self):
		if self.workflow_state == "Verified":
			self.verifier = frappe.db.get_value("User",frappe.session.user,"username")
			self.verify_date = today()
		if self.workflow_state == "Approved":
			self.approver = frappe.db.get_value("User",frappe.session.user,"username")
			self.approver_date = today()
	
	def validate_workflow_permissions(self):
		if not frappe.session.user  == "Administrator":
			allow_role_in_group = get_role_allow_for_this_group(self.quality_document_group)
			if self.workflow_state and not self.workflow_state == "Draft":
				if allow_role_in_group:
					if not frappe.db.get_value("Workflow Transition",{"next_state":self.workflow_state,"allowed":allow_role_in_group},"name"):
						frappe.throw(_("Not Allowed To Do This Action"))
				else:
					frappe.throw(_("Insufficient Permission To Do Action"))
			
def get_role_allow_for_this_group(quality_document_group):
	quality_document_group_users = frappe.db.sql("""SELECT role
FROM `tabQuality User`
WHERE parent=%s
  AND USER=%s""",(quality_document_group,frappe.session.user),as_dict=1)
	if len(quality_document_group_users) >= 1:
		return quality_document_group_users[0].role
	else:
		return None

@frappe.whitelist()
def get_attach_quality_document(doc_name):
	quality_document = frappe.get_all("File",filters={"attached_to_doctype":"Quality Document","attached_to_name":doc_name},fields=["name"])
	quality_document_list = [row.name for row in quality_document]
	return quality_document_list


"""	def update_status(self):
		if self.status not in ('Cancelled', 'Completed') and self.exp_end_date:
			from datetime import datetime
			if self.exp_end_date < datetime.now().date():
				self.db_set('status', 'Overdue', update_modified=False)
				self.update_quality_document_group() """

@frappe.whitelist()
def check_if_child_exists(name):
	child_quality_documents = frappe.get_all("Quality Document", filters={"parent_quality_document": name})
	child_quality_documents = [get_link_to_form("Quality Document", quality_document.name) for quality_document in child_quality_documents]
	return child_quality_documents


#@frappe.whitelist()
#@frappe.validate_and_sanitize_search_inputs
#def get_quality_document_group(doctype, txt, searchfield, start, page_len, filters):
#	from erpnext.controllers.queries import get_match_cond
#	meta = frappe.get_meta(doctype)
#	searchfields = meta.get_search_fields()
#	search_columns = ", " + ", ".join(searchfields) if searchfields else ''
#	search_cond = " or " + " or ".join(field + " like %(txt)s" for field in searchfields)

	#return frappe.db.sql(""" select name {search_columns} from `tabQuality Document Group`
	#	where %(key)s like %(txt)s
	#		%(mcond)s
	#		{search_condition}
	#	order by name
	#	limit %(start)s, %(page_len)s""".format(search_columns = search_columns,
	#		search_condition=search_cond), {
	#		'key': searchfield,
	#		'txt': '%' + txt + '%',
	#		'mcond':get_match_cond(doctype),
	#		'start': start,
	#		'page_len': page_len
	#	})


@frappe.whitelist()
def set_multiple_status(names, status):
	names = json.loads(names)
	for name in names:
		quality_document = frappe.get_doc("Quality Document", name)
		quality_document.status = status
		quality_document.save()

def set_quality_documents_as_overdue():
	quality_documents = frappe.get_all("Quality Document", filters={"status": ["not in", ["Cancelled", "Completed"]]}, fields=["name", "status", "review_date"])
	for quality_document in quality_documents:
		if quality_document.status == "Pending Review":
			if getdate(quality_document.review_date) > getdate(today()):
				continue
		frappe.get_doc("Quality Document", quality_document.name).update_status()


@frappe.whitelist()
def make_timesheet(source_name, target_doc=None, ignore_permissions=False):
	def set_missing_values(source, target):
		target.append("time_logs", {
			"hours": source.actual_time,
			"completed": source.status == "Completed",
			"quality_document_group": source.quality_document_group,
			"quality_document": source.name
		})

	doclist = get_mapped_doc("Quality Document", source_name, {
			"Quality Document": {
				"doctype": "Timesheet"
			}
		}, target_doc, postprocess=set_missing_values, ignore_permissions=ignore_permissions)

	return doclist


@frappe.whitelist()
def get_children(doctype, parent, quality_document=None, quality_document_group=None, is_root=False):

	filters = [['docstatus', '<', '2']]

	if quality_document:
		filters.append(['parent_quality_document', '=', quality_document])
	elif parent and not is_root:
		# via expand child
		filters.append(['parent_quality_document', '=', parent])
	else:
		filters.append(['ifnull(`parent_quality_document`, "")', '=', ''])

	if quality_document_group:
		filters.append(['quality_document_group', '=', quality_document_group])

	quality_documents = frappe.get_list(doctype, fields=[
		'name as value',
		'subject as title',
		'is_group as expandable',
		'workflow_state as status'
	], filters=filters, order_by='name')

	# return tasks
	return quality_documents

@frappe.whitelist()
def add_node():
	from frappe.desk.treeview import make_tree_args
	args = frappe.form_dict
	args.update({
		"name_field": "subject"
	})
	args = make_tree_args(**args)

	if args.parent_quality_document == 'All Quality Documents' or args.parent_quality_document == args.quality_document_group:
		args.parent_quality_document = None

	frappe.get_doc(args).insert()

@frappe.whitelist()
def add_multiple_quality_documents(data, parent):
	data = json.loads(data)
	new_doc = {'doctype': 'Quality Document', 'parent_quality_document': parent if parent!="All Quality Documents" else ""}
	new_doc['quality_document_group'] = frappe.db.get_value('Quality Document', {"name": parent}, 'quality_document_group') or ""

	for d in data:
		if not d.get("subject"): continue
		new_doc['subject'] = d.get("subject")
		new_quality_document = frappe.get_doc(new_doc)
		new_quality_document.insert()

def on_doctype_update():
	frappe.db.add_index("Quality Document", ["lft", "rgt"])

def validate_quality_document_group_dates(quality_document_group_end_date, quality_document, quality_document_start, quality_document_end, actual_or_expected_date):
	if quality_document.get(quality_document_start) and date_diff(quality_document_group_end_date, getdate(quality_document.get(quality_document_start))) < 0:
		frappe.throw(_("Quality Documents's {0} Start Date cannot be after Quality Document Group's End Date.").format(actual_or_expected_date))

	if quality_document.get(quality_document_end) and date_diff(quality_document_group_end_date, getdate(quality_document.get(quality_document_end))) < 0:
		frappe.throw(_("Quality Document's {0} End Date cannot be after Quality Document Group's End Date.").format(actual_or_expected_date))

'''Update status outdated for approved document cron job'''
@frappe.whitelist()
def update_outdate_for_approved_quality_document():
	filters = [
		["approver_date","=",add_months(today(),-12)],
		["workflow_state","=","Approved"]
	]
	quality_documents = frappe.get_all("Quality Document",filters=filters,fields=["name"])
	for quality_document in quality_documents:
		frappe.db.set_value("Quality Document",quality_document.name,"workflow_state","Outdated")
