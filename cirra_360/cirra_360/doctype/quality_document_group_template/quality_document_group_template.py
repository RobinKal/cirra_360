# Copyright (c) 2021, sujay and contributors
# For license information, please see license.txt


import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_link_to_form


class QualityDocumentGroupTemplate(Document):

	def validate(self):
		self.validate_dependencies()

	def validate_dependencies(self):
		for quality_document in self.quality_documents:
			quality_document_details = frappe.get_doc("Quality Document", quality_document.quality_document)
			if quality_document_details.depends_on:
				for dependency_quality_document in quality_document_details.depends_on:
					if not self.check_dependent_quality_document_presence(dependency_quality_document.quality_document):
						quality_document_details_format = get_link_to_form("Quality Document",quality_document_details.name)
						dependency_quality_document_format = get_link_to_form("Quality Document", dependency_quality_document.quality_document)
						frappe.throw(_("Quality Document {0} depends on Quality Document {1}. Please add Quality Document {1} to the QualityDocuments list.").format(frappe.bold(quality_document_details_format), frappe.bold(dependency_quality_document_format)))

	
	def check_dependent_quality_document_presence(self, quality_document):
		for quality_document_details in self.quality_documents:
			if quality_document_details.quality_document == quality_document:
				return True
		return False

	@frappe.whitelist()
	def get_all_dependent_document(self,parent_document_id):
		documents = []
		_get_all_dependent_document(documents,parent_document_id)
		frappe.errprint(documents)
		for row in documents:
			self.append("quality_documents",dict(
				quality_document = row.quality_document,
				subject = frappe.db.get_value("Quality Document",row.quality_document,"subject")
			))

	@frappe.whitelist()
	def remove_all_dependent_document(self,parent_document_id):
		documents = []
		_get_all_dependent_document(documents,parent_document_id)
		frappe.errprint(documents)
		dependent_document = [row.quality_document for row in documents]
		for row in self.quality_documents:
			if row.quality_document in dependent_document:
				self.remove(row)
		

def _get_all_dependent_document(documents,parent_document_id):
	documents_list = frappe.get_all("Quality Document Depends On",filters={"parent":parent_document_id},fields=["quality_document"])
	for row in documents_list:
		documents.append(row)
		_get_all_dependent_document(documents,row.quality_document)


