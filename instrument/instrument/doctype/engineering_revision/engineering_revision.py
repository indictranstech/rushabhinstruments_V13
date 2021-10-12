# Copyright (c) 2021, instrument and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class EngineeringRevision(Document):
	def validate(self):
		self.manage_default()
		if self.get('__islocal'):
			purchasing_package = frappe.new_doc("Package Document")
			if purchasing_package:
				purchasing_package.item_code = self.item_code
				purchasing_package.revision = self.revision
				purchasing_package.package_type = 'Purchasing_Package'
				purchasing_package.save(ignore_permissions=1)
			self.append('purchasing_package',{
				'purchasing_package_name' : purchasing_package.name
				})
			manufacturing_package = frappe.new_doc("Package Document")
			if purchasing_package:
				manufacturing_package.item_code = self.item_code
				manufacturing_package.revision = self.revision
				manufacturing_package.package_type = 'Manufacturing_Package'
				manufacturing_package.save(ignore_permissions=1)
			self.append('manufacturing_package',{
				'manufacturing_package_name' : manufacturing_package.name
				})
			engineering_package = frappe.new_doc("Package Document")
			if engineering_package:
				engineering_package.item_code = self.item_code
				engineering_package.revision = self.revision
				engineering_package.package_type = 'Engineering_Package'
				engineering_package.save(ignore_permissions=1)
			self.append('engineering_package',{
				'engineering_package_name' : engineering_package.name
				})
		
	
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

	def on_trash(self):
		frappe.db.sql("""delete from `tabPackage Document` where item_code = '{0}' and revision ='{1}'""".format(self.item_code,self.revision))