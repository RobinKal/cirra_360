# Copyright (c) 2021, sujay and contributors
# For license information, please see license.txt


from distutils.log import debug
import frappe
from frappe.model.document import Document
from frappe.utils import today

class QualityDocumentGroup(Document):
	def get_feed(self):
		return '{0}: {1}'.format((self.status), frappe.safe_decode(self.quality_document_group_name))
		
	def before_print(self, settings=None):
		self.onload()
	
	def validate(self):
		pass
		# if not self.is_new():
		# 	self.copy_quality_document_group_template()
		
	def on_submit(self):
		self.copy_quality_document_group_template()
	
	
	
	def copy_quality_document_group_template(self):
		'''
		Copy quality_documents from template
		'''
		if self.quality_document_group_template and not frappe.db.get_all('Quality Document', dict(quality_document_group = self.name), limit=1):

			# has a template, and no loaded quality_documents, so lets create
			if not self.expected_start_date:
				# quality_document_group starts today
				self.expected_start_date = today()

			template = frappe.get_doc('Quality Document Group Template', self.quality_document_group_template)

			if not self.quality_document_group_type:
				self.quality_document_group_type = template.quality_document_group_type

			# create quality_documents from template
			quality_document_group_quality_documents = []
			tmp_quality_document_details = []
			for quality_document in template.quality_documents:
				template_quality_document_details = frappe.get_doc("Quality Document", quality_document.quality_document)
				tmp_quality_document_details.append(template_quality_document_details)
				quality_document = self.create_quality_document_quality_document_group_type(template_quality_document_details)
				quality_document_group_quality_documents.append(quality_document)
			self.dependency_mapping(tmp_quality_document_details, quality_document_group_quality_documents) 

	def create_quality_document_quality_document_group_type(self, quality_document_details):
		return frappe.get_doc(dict(
				doctype = 'Quality Document',
				subject = quality_document_details.subject,
				quality_document_group = self.name,
				status = 'Draft',
				shortcode = quality_document_details.shortcode,
				#exp_start_date = self.calculate_start_date(quality_document_details),
				#exp_end_date = self.calculate_end_date(quality_document_details),
				# description = quality_document_details.description,
				# quality_document_weight = quality_document_details.quality_document_weight,
				# type = quality_document_details.type,
				quality_document_type_master = quality_document_details.quality_document_type_master,
				quality_document_type = quality_document_details.quality_document_type,
				# issue = quality_document_details.issue,
				is_group = quality_document_details.is_group
			)).insert()

	"""def calculate_start_date(self, quality_document_details):
		self.start_date = add_days(self.expected_start_date, quality_document_details.start)
		self.start_date = self.update_if_holiday(self.start_date)
		return self.start_date

	def calculate_end_date(self, quality_document_details):
		self.end_date = add_days(self.start_date, quality_document_details.duration)
		return self.update_if_holiday(self.end_date)

	def update_if_holiday(self, date):
		holiday_list = self.holiday_list or get_holiday_list(self.company)
		while is_holiday(holiday_list, date):
			date = add_days(date, 1)
		return date"""

	def dependency_mapping(self, template_quality_documents, quality_document_group_quality_documents):
		for template_quality_document in template_quality_documents:
			quality_document_group_quality_document = list(filter(lambda x: x.subject == template_quality_document.subject, quality_document_group_quality_documents))[0]
			quality_document_group_quality_document = frappe.get_doc("Quality Document", quality_document_group_quality_document.name)
			self.check_depends_on_value(template_quality_document, quality_document_group_quality_document, quality_document_group_quality_documents)
			self.check_for_parent_quality_documents(template_quality_document, quality_document_group_quality_document, quality_document_group_quality_documents)

	def check_depends_on_value(self, template_quality_document, quality_document_group_quality_document, quality_document_group_quality_documents):
		if template_quality_document.get("depends_on") and not quality_document_group_quality_document.get("depends_on"):
			for child_quality_document in template_quality_document.get("depends_on"):
				child_quality_document_subject = frappe.db.get_value("Quality Document", child_quality_document.quality_document, "subject")
				corresponding_quality_document_group_quality_document = list(filter(lambda x: x.subject == child_quality_document_subject, quality_document_group_quality_documents))
				if len(corresponding_quality_document_group_quality_document):
					quality_document_group_quality_document.append("depends_on",{
						"quality_document": corresponding_quality_document_group_quality_document[0].name
					})
					quality_document_group_quality_document.save()

	def check_for_parent_quality_documents(self, template_quality_document, quality_document_group_quality_document, quality_document_group_quality_documents):
		if template_quality_document.get("parent_quality_document") and not quality_document_group_quality_document.get("parent_quality_document"):
			parent_quality_document_subject = frappe.db.get_value("Quality Document", template_quality_document.get("parent_quality_document"), "subject")
			corresponding_quality_document_group_quality_document = list(filter(lambda x: x.subject == parent_quality_document_subject, quality_document_group_quality_documents))
			if len(corresponding_quality_document_group_quality_document):
				quality_document_group_quality_document.parent_quality_document = corresponding_quality_document_group_quality_document[0].name
				quality_document_group_quality_document.save()

	def is_row_updated(self, row, existing_quality_document_data, fields):
		if self.get("__islocal") or not existing_quality_document_data: return True

		d = existing_quality_document_data.get(row.quality_document_id, {})

		for field in fields:
			if row.get(field) != d.get(field):
				return True

	
	def update_percent_complete(self):
		if self.percent_complete_method == "Manual":
			if self.status == "Completed":
				self.percent_complete = 100
			return

		total = frappe.db.count('Quality Document', dict(quality_document_group=self.name))

		if not total:
			self.percent_complete = 0
		else:
			if (self.percent_complete_method == "Quality Document Completion" and total > 0) or (
				not self.percent_complete_method and total > 0):
				completed = frappe.db.sql("""select count(name) from tabQuality Document where
					quality_document_group=%s and status in ('Cancelled', 'Completed')""", self.name)[0][0]
				self.percent_complete = flt(flt(completed) / total * 100, 2)

			if (self.percent_complete_method == "Quality Document Progress" and total > 0):
				progress = frappe.db.sql("""select sum(progress) from tabQuality Document where
					quality_document_group=%s""", self.name)[0][0]
				self.percent_complete = flt(flt(progress) / total, 2)

			if (self.percent_complete_method == "Quality Document Weight" and total > 0):
				weight_sum = frappe.db.sql("""select sum(quality_document_weight) from tabQuality Document where
					quality_document_group=%s""", self.name)[0][0]
				weighted_progress = frappe.db.sql("""select progress, quality_document_weight from tabQuality Document where
					quality_document_group=%s""", self.name, as_dict=1)
				pct_complete = 0
				for row in weighted_progress:
					pct_complete += row["progress"] * frappe.utils.safe_div(row["quality_document_weight"], weight_sum)
				self.percent_complete = flt(flt(pct_complete), 2)

		# don't update status if it is cancelled
		if self.status == 'Cancelled':
			return

		if self.percent_complete == 100:
			self.status = "Completed"
	
	
	# def create_quality_document_quality_document_group_type(self, quality_document_details):
	# 	return frappe.get_doc(dict(
	# 			doctype = 'Quality Document',
	# 			subject = quality_document_details.subject,
	# 			quality_document_group = self.name,
	# 			status = 'Draft',
	# 			#exp_start_date = self.calculate_start_date(quality_document_details),
	# 			#exp_end_date = self.calculate_end_date(quality_document_details),
	# 			#description = quality_document_details.description,
	# 			#quality_document_weight = quality_document_details.quality_document_weight,
	# 			#type = quality_document_details.type,
	# 			#issue = quality_document_details.issue,
	# 			is_group = quality_document_details.is_group
	# 		)).insert()
			
	#def after_rename(self, old_name, new_name, merge=False):
	#	if old_name == self.copied_from:
	#		frappe.db.set_value('Quality Document Group', new_name, 'copied_from', new_name)
	#
@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_users_for_quality_document_group(doctype, txt, searchfield, start, page_len, filters):
	conditions = []
	return frappe.db.sql("""select name, concat_ws(' ', first_name, middle_name, last_name)
		from `tabUser`
		where enabled=1
			and name not in ("Guest", "Administrator")
			and ({key} like %(txt)s
				or full_name like %(txt)s)
			{fcond} {mcond}
		order by
			if(locate(%(_txt)s, name), locate(%(_txt)s, name), 99999),
			if(locate(%(_txt)s, full_name), locate(%(_txt)s, full_name), 99999),
			idx desc,
			name, full_name
		limit %(start)s, %(page_len)s""".format(**{
		'key': searchfield,
		'fcond': get_filters_cond(doctype, filters, conditions),
		'mcond': get_match_cond(doctype)
	}), {
							 'txt': "%%%s%%" % txt,
							 '_txt': txt.replace("%", ""),
							 'start': start,
							 'page_len': page_len
						 })




	
@frappe.whitelist()
def create_duplicate_quality_document_group(prev_doc, quality_document_group_name):
	''' Create duplicate quality_document_group based on the old quality_document_group '''
	import json
	prev_doc = json.loads(prev_doc)

	if quality_document_group_name == prev_doc.get('name'):
		frappe.throw(_("Use a name that is different from previous quality_document_group name"))

	# change the copied doc name to new quality_document_group name
	quality_document_group = frappe.copy_doc(prev_doc)
	quality_document_group.name = quality_document_group_name
	quality_document_group.quality_document_group_template = ''
	quality_document_group.quality_document_group_name = quality_document_group_name
	quality_document_group.insert()

	# fetch all the quality_document linked with the old quality_document_group
	quality_document_list = frappe.get_all("Quality Document", filters={
		'quality_document_group': prev_doc.get('name')
	}, fields=['name'])

	# Create duplicate quality_document for all the quality_document
	for quality_document in quality_document_list:
		quality_document = frappe.get_doc('Quality Document', quality_document)
		new_quality_document = frappe.copy_doc(quality_document)
		new_quality_document.quality_document_group = quality_document_group.name
		new_quality_document.insert()

	quality_document_group.db_set('quality_document_group_template', prev_doc.get('quality_document_group_template'))



@frappe.whitelist()
def create_kanban_board_if_not_exists(quality_document_group):
	from frappe.desk.doctype.kanban_board.kanban_board import quick_kanban_board

	quality_document_group = frappe.get_doc('Quality Document Group', quality_document_group)
	if not frappe.db.exists('Kanban Board', quality_document_group.quality_document_group_name):
		quick_kanban_board('Quality Document', quality_document_group.quality_document_group_name, 'status', quality_document_group.name)

	return True

@frappe.whitelist()
def set_quality_document_group_status(quality_document_group, status):
	'''
	set status for quality_document_group and all related Quality Documents
	'''
	if not status in ('Completed', 'Cancelled'):
		frappe.throw(_('Status must be Cancelled or Completed'))

	quality_document_group = frappe.get_doc('Quality Document Group', quality_document_group)
	frappe.has_permission(doc = quality_document_group, throw = True)

	for quality_document in frappe.get_all('Quality Document', dict(quality_document_group = quality_document_group.name)):
		frappe.db.set_value('Quality Document', quality_document.name, 'status', status)

	quality_document_group.status = status
	quality_document_group.save()
	
	
@frappe.whitelist()
def get_children(doctype, parent=None, quality_document_group =None, is_root=False, customer = None):
	filters = [['docstatus', '<', '2']]
	if quality_document_group:
		filters.append(['parent_quality_document_group', '=', quality_document_group])
	elif parent and not is_root:
		filters.append(['parent_quality_document_group', '=', parent])
	else:
		filters.append(['ifnull(`parent_quality_document_group`, "")', '=', ''])
	
	if customer:
		filters.append(['customer', '=', customer])

	quality_document_tree = frappe.get_list(doctype, fields=[
		'name as value',
		'is_group as expandable'
	], filters=filters, order_by='name')

	return quality_document_tree

@frappe.whitelist()
def add_node():
	from frappe.desk.treeview import make_tree_args
	args = frappe.form_dict
	args = make_tree_args(**args)

	if args.parent_quality_document_group == 'All Quality Document Groups':
		args.parent_quality_document_group = None

	frappe.get_doc(args).insert()

@frappe.whitelist()
def get_user_query(doctype, txt, searchfield, start, page_len, filters):
	if not filters.get("customer"):
		return []

	item_filters = [
		['parent', '=', filters.get("customer")]
	]

	item_users = frappe.get_all(
		"User Creation Info",
		fields=["email_id as 'name'"],
		filters=item_filters,
		limit_start=start,
		limit_page_length=page_len,
		as_list=1
	)
	return item_users


@frappe.whitelist()
def get_user_role(doctype, txt, searchfield, start, page_len, filters):
	if not filters.get("user"):
		return []

	role_filter = [
		['parent', '=', filters.get("user")]
	]

	user_roles = frappe.get_all(
		"Has Role",
		fields=["role as 'name'"],
		filters=role_filter,
		limit_start=start,
		limit_page_length=page_len,
		as_list=1
	)
	return user_roles