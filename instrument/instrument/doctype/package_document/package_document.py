# Copyright (c) 2021, instrument and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json
from frappe.utils.background_jobs import enqueue
from frappe.desk.form.load import get_attachments
from zipfile import ZipFile
import os
from frappe.utils import call_hook_method, cint, cstr, encode, get_files_path, get_hook_method, random_string, strip
from frappe.model.mapper import get_mapped_doc

class PackageDocument(Document):
	@frappe.whitelist()
	def copy_attachments(self):
		documents = frappe.db.sql("""SELECT file_url from `tabFile` where attached_to_doctype = 'Package Document' and attached_to_name = '{0}'""".format(self.name),as_dict=1)
		if documents:
			for i in documents:
				self.append("attachment",{
					'attachment':i.get('file_url')

					})
		self.save()
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
@frappe.whitelist()
def get_attachments_as_zip(doc):
	"""Copy attachments from `package document`"""
	from frappe.desk.form.load import get_attachments
	doc = json.loads(doc)
	package_doc = frappe.get_doc("Package Document",doc.get('name'))
	attachments = get_attachments(package_doc.doctype, package_doc.name)
	file_path = os.path.realpath(get_files_path(is_private=1))
	# full_path = path+"/"+sitename+"private/files/"+row.engineering_revision+"_"+doc.name+".zip"
	full_path = file_path+ "/"+package_doc.name+".zip"
	file_name = package_doc.name+".zip"
	file_url = '/private/files/'+file_name
	if len(attachments) > 0 :
		with ZipFile(full_path,'w') as zip:
			for i in attachments:
				file_doc = frappe.get_doc("File",{'file_url':i.file_url})
				full_file_path = file_doc.get_full_path()
				zip.write(full_file_path)
		file_doc = frappe.new_doc("File")
		file_doc.file_name =file_name
		file_doc.folder = "Home/Attachments"
		file_doc.attached_to_doctype = package_doc.doctype
		file_doc.attached_to_name = package_doc.name
		file_doc.file_url = file_url
		file_doc.insert(ignore_permissions=True)
		frappe.db.commit()
		package_doc.reload()


@frappe.whitelist()
def download_attachments(doc):
	# doc = json.loads(doc)
	# import openpyxl
	from io import BytesIO
	# file_path = frappe.utils.get_site_path("public")
	# # now = datetime.now()
	# fname = 
	# wb = openpyxl.load_workbook(filename=file_path+fname)
	xlsx_file = BytesIO()
	# wb.save(xlsx_file)


	req = urllib.request.Request(url, headers=headers_1)

	# open it in a file and write it to save it in local
	with urllib.request.urlopen(req) as response, open(output_path, 'wb') as f:
	    shutil.copyfileobj(response, f)
	frappe.local.response.filecontent=xlsx_file.getvalue()

	frappe.local.response.type = "download"
	
	frappe.local.response.filename = doc + ".zip"
