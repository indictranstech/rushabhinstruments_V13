# Copyright (c) 2021, instrument and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
# from frappe.model.document import Document
from frappe.utils.background_jobs import enqueue
from frappe.desk.form.load import get_attachments
from zipfile import ZipFile
import os
from frappe.utils import call_hook_method, cint, cstr, encode, get_files_path, get_hook_method, random_string, strip
from frappe.model.mapper import get_mapped_doc

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
		frappe.db.sql("""DELETE from `tabFile` where attached_to_doctype='Engineering Revision' and attached_to_name=%s""",
			(self.name))
		self.other_revisions()
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

	def other_revisions(self):
		if self.other_engineering_revision:
			for row in self.other_engineering_revision:
				if row.use_specific_engineering_revision:
					er = frappe.get_doc("Engineering Revision",row.revision)
				else:
					er_name = frappe.db.get_value("Engineering Revision",{'item_code':row.item_code,'is_default':1},'name')
					if er_name:
						er = frappe.get_doc("Engineering Revision",er_name)
				if er:
					if not row.exclude_purchasing_package:
						purchasing_package = frappe.db.sql("""SELECT purchasing_package_name from `tabPurchasing Package Table` a join `tabEngineering Revision` b on a.parent = b.name where b.name = '{0}'""".format(er.name),as_dict=1)
						purchasing_package_list = [item.purchasing_package_name for item in purchasing_package]
						for col in purchasing_package_list:
							package_doc = frappe.get_doc("Package Document",col)
							"""Copy attachments from `package document`"""
							from frappe.desk.form.load import get_attachments
							attachments = get_attachments(package_doc.doctype, package_doc.name)
							file_path = os.path.realpath(get_files_path(is_private=1))
							# full_path = path+"/"+sitename+"private/files/"+row.engineering_revision+"_"+doc.name+".zip"
							full_path = file_path+ "/"+er.name+"_"+"purchasing_package"+self.name+".zip"
							file_name = er.name+"_"+"purchasing_package"+self.name+".zip"
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
								file_doc.attached_to_doctype = self.doctype
								file_doc.attached_to_name = self.name
								file_doc.file_url = file_url
								file_doc.insert(ignore_permissions=True)
								frappe.db.commit()
								# doc.reload()
					if not row.exclude_manufacturing_package:
						manufacturing_package = frappe.db.sql("""SELECT manufacturing_package_name from `tabManufacturing Package Table` a join `tabEngineering Revision` b on a.parent = b.name where b.name = '{0}'""".format(er.name),as_dict=1)
						manufacturing_package_list = [item.manufacturing_package_name for item in manufacturing_package]
						for col in manufacturing_package_list:
							package_doc = frappe.get_doc("Package Document",col)
							"""Copy attachments from `package document`"""
							from frappe.desk.form.load import get_attachments
							attachments = get_attachments(package_doc.doctype, package_doc.name)
							file_path = os.path.realpath(get_files_path(is_private=1))
							# full_path = path+"/"+sitename+"private/files/"+row.engineering_revision+"_"+doc.name+".zip"
							full_path = file_path+ "/"+er.name+"_"+"manufacturing_package"+self.name+".zip"
							file_name = er.name+"_"+"manufacturing_package"+self.name+".zip"
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
								file_doc.attached_to_doctype = self.doctype
								file_doc.attached_to_name = self.name
								file_doc.file_url = file_url
								file_doc.insert(ignore_permissions=True)
								frappe.db.commit()
					if not row.exclude_engineering_package:
						engineering_package = frappe.db.sql("""SELECT engineering_package_name from `tabEngineering Package Table` a join `tabEngineering Revision` b on a.parent = b.name where b.name = '{0}'""".format(er.name),as_dict=1)
						engineering_package_list = [item.engineering_package_name for item in engineering_package]
						for col in engineering_package_list:
							package_doc = frappe.get_doc("Package Document",col)
							"""Copy attachments from `package document`"""
							from frappe.desk.form.load import get_attachments
							attachments = get_attachments(package_doc.doctype, package_doc.name)
							file_path = os.path.realpath(get_files_path(is_private=1))
							# full_path = path+"/"+sitename+"private/files/"+row.engineering_revision+"_"+doc.name+".zip"
							full_path = file_path+ "/"+er.name+"_"+"engineering_package"+self.name+".zip"
							file_name = er.name+"_"+"engineering_package"+self.name+".zip"
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
								file_doc.attached_to_doctype = self.doctype
								file_doc.attached_to_name = self.name
								file_doc.file_url = file_url
								file_doc.insert(ignore_permissions=True)
								frappe.db.commit()	
	def on_trash(self):
		frappe.db.sql("""delete from `tabPackage Document` where item_code = '{0}' and revision ='{1}'""".format(self.item_code,self.revision))