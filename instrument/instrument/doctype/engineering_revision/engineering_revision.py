# Copyright (c) 2021, instrument and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class EngineeringRevision(Document):
	def validate(self):
		self.manage_default()
	
	def manage_default(self):
		""" Uncheck others if current one is selected as default or
			check the current one as default if it the only doc for the selected item
		"""
		if self.is_default and self.is_active:
			frappe.db.sql("""UPDATE `tabEngineering Revision`
				set is_default=0
				where name != %s""",
				(self.name))
		elif not frappe.db.exists(dict(doctype='Engineering Revision',item_code=self.item_code,is_default=1)) \
			and self.is_active:
			frappe.db.set(self, "is_default", 1)
		else:
			frappe.db.set(self, "is_default", 0)