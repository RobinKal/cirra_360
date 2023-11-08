# Copyright (c) 2021, sujay and contributors
# For license information, please see license.txt

	
import frappe
from frappe import _
from frappe.model.document import Document


class QualityDocumentGroupType(Document):
	def on_trash(self):
		if self.name == "External":
			frappe.throw(_("You cannot delete QualityDocumentGroupType 'External'"))
