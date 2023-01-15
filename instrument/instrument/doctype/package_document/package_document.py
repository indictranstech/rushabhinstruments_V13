# Copyright (c) 2021, instrument and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json

class PackageDocument(Document):

	def validate(self):
		engineering_revision = frappe.db.get_value("Engineering Revision",{'item_code':self.item_code,'revision':self.revision},'name')
		if self.package_type == 'Purchasing_Package':
			package_doc_name = frappe.db.get_value("Purchasing Package Table",{'parent':engineering_revision},'name')
			frappe.db.set_value("Purchasing Package Table",package_doc_name,'completed',self.completed)
		elif self.package_type == 'Manufacturing_Package':
			package_doc_name = frappe.db.get_value("Manufacturing Package Table",{'parent':engineering_revision},'name')
			frappe.db.set_value("Manufacturing Package Table",package_doc_name,'completed',self.completed)
		else :
			package_doc_name = frappe.db.get_value("Engineering Package Table",{'parent':engineering_revision},'name')
			frappe.db.set_value("Engineering Package Table",package_doc_name,'completed',self.completed)


@frappe.whitelist()
def copy_doc_to_other_doc(item_list,package_type,item_code,revision,docname,package_document):
	locations = 0
	item_list = json.loads(item_list)
	# other_package_documents = frappe.db.sql("""SELECT name from `tabPackage Document` where item_code = '{0}' and revision = '{1}' and name != '{2}'""".format(item_code,revision,docname),as_dict=1)
	
	# for row in other_package_documents:
	doc = frappe.get_doc("Package Document",package_document)
	if doc:
		for col in item_list:
			doc.append('attachment',{
				'attachment':col.get('attachment')
				})
			_file = frappe.get_doc({
				"doctype": "File",
				"file_url":col.get("attachment") ,
				"attached_to_doctype": "Package Document",
				"attached_to_name": package_document,
				"is_private": 1
				})
			_file.save()
		doc.save()
	
	frappe.msgprint("Documents Copied Successfully")

@frappe.whitelist()
def copy_doc_to_other_doc_for_file(item_list,package_type,item_code,revision,docname,package_document):
	item_list = json.loads(item_list)
	# other_package_documents = frappe.db.sql("""SELECT name from `tabPackage Document` where item_code = '{0}' and revision = '{1}' and name != '{2}'""".format(item_code,revision,docname),as_dict=1)

	# for row in other_package_documents:
	doc = frappe.get_doc("Package Document",package_document)
	if doc:
		for col in item_list:
			doc.append("file_locations",{
				'file_name' : col.get('file_name'),
				'location': col.get("location"),
				'note':col.get("note")

			})
		doc.save()
	frappe.msgprint("Documents Copied Successfully")