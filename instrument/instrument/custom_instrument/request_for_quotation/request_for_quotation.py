from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils.background_jobs import enqueue
from frappe.desk.form.load import get_attachments
from zipfile import ZipFile
import os, shutil
from frappe.utils import call_hook_method, cint, cstr, encode, get_files_path, get_hook_method, random_string, strip
from frappe.model.mapper import get_mapped_doc
import json

def after_insert(doc,method):
	pdf_data=frappe.attach_print('Request for Quotation',doc.name, print_format='Request for Quotation Print')
		
	_file = frappe.get_doc({
	"doctype": "File",
	"file_name": pdf_data.get('fname'),
	"attached_to_doctype": "Request for Quotation",
	"attached_to_name": doc.name,
	"is_private": 1,
	"content": pdf_data.get('fcontent')
	})
	_file.save()
def validate(doc,method):
	if doc.items:
		for item in doc.items:
			engineering_revision = frappe.db.get_value("Item",{'item_code':item.item_code},'engineering_revision')
			item.default_engineering_revision = engineering_revision
	if not doc.get("__islocal"):
		frappe.db.sql("""DELETE from `tabFile` where attached_to_doctype='Request for Quotation' and attached_to_name=%s""",
			(doc.name))
		pdf_data=frappe.attach_print('Request for Quotation',doc.name, print_format='Request for Quotation Print')
		
		_file = frappe.get_doc({
		"doctype": "File",
		"file_name": pdf_data.get('fname'),
		"attached_to_doctype": "Request for Quotation",
		"attached_to_name": doc.name,
		"is_private": 1,
		"content": pdf_data.get('fcontent')
		})
		_file.save()
	# attach_purchasing_docs(doc,method)
def on_submit(doc, method = None):
	prepare_zip_attachment_for_rfq(doc,method)
	file_att = []
	attachments = frappe.db.sql(""" SELECT file_name  FROM tabFile 
				WHERE attached_to_name = '{0}'""".format(doc.name),as_dict=1)
	
	if attachments:
		for row in attachments:
			_file = frappe.get_doc("File", {"file_name": row.file_name})
			content = _file.get_content()
			if not content:
				return
			attachment_list = {'fname':row.file_name,'fcontent':content}
			file_att.append(attachment_list)

	send_email_without_reference_to_supplier(doc, method, file_att)
	
def send_email_without_reference_to_supplier(doc, method, file_att):
	file_att.append(frappe.attach_print("Request for Quotation", doc.name))
	email_template = frappe.get_doc("Email Template", "Request for Quotation")
	data = {}
	for row in doc.suppliers:
		data["salutation"] = doc.salutation
		data["supplier_name"] = row.supplier_name
		data["username"] = frappe.db.get_value("User", {"name":frappe.session.user}, "full_name")
		if row.without_url_email:
			message = frappe.render_template(email_template.response_html, data)
			email_args = {
				"recipients": [row.email_id],
				"sender": frappe.db.get_value("Email Setting",{"email_name": "Purchase Order Email"},"email_id"),
				"subject": email_template.subject,
				"message": message,
				"now": True,
				"expose_recipients": "header",
				"read_receipt": 0,
				"is_notification": False,
				"attachments": file_att
			}
			enqueue(method=frappe.sendmail, queue='short', timeout=300, is_async=True, delayed=False, **email_args)
		data.clear()

@frappe.whitelist()
def get_engineering_revision(item_code):
	if item_code:
		engineering_revision = frappe.db.get_value("Item",{'name':item_code},'engineering_revision')
		return engineering_revision


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_engineering_revisions_for_filter(doctype, txt, searchfield, start, page_len, filters):
	return frappe.db.sql(""" SELECT name FROM `tabEngineering Revision` where item_code = '{0}' """.format(filters.get("item_code")))


# def attach_purchasing_docs(doc, method):
# 	for row in doc.items:
# 		if row.item_code and row.engineering_revision:
# 			purchasing_package = frappe.db.sql("""SELECT purchasing_package_name from `tabPurchasing Package Table` a join `tabEngineering Revision` b on a.parent = b.name where b.name = '{0}'""".format(row.engineering_revision),as_dict=1,debug=1)
# 			purchasing_package_list = [item.purchasing_package_name for item in purchasing_package]
# 			er_doc = frappe.get_doc("Engineering Revision",row.engineering_revision)
# 			if er_doc:
# 				for i in er_doc.other_engineering_revision:
# 					print("============", er_doc.name)
# 					if i.revision and not i.exclude_purchasing_package:
# 						er_purchasing_package = frappe.db.sql("""SELECT purchasing_package_name from `tabPurchasing Package Table` a join `tabEngineering Revision` b on a.parent = b.name where b.name = '{0}'""".format(i.revision),as_dict=1,debug=1)
# 						if er_purchasing_package:
# 							for p in er_purchasing_package:
# 								purchasing_package_list.append(p.purchasing_package_name)
# 					else:
# 						if i.purchase_package_name and not i.exclude_purchasing_package:
# 							purchasing_package_list.append(i.purchase_package_name)
# 			for col in purchasing_package_list:
# 				package_doc = frappe.get_doc("Package Document",col)
# 				"""Copy attachments from `package document`"""
# 				from frappe.desk.form.load import get_attachments
# 				attachments = get_attachments(package_doc.doctype, package_doc.name)
# 				print("============", attachments,  package_doc.doctype, package_doc.name)

# 				#loop through attachments
# 				# for attach_item in get_attachments(package_doc.doctype, package_doc.name):
# 					# save attachments to new doc
# 					# _file = frappe.get_doc({
# 					# 	"doctype": "File",
# 					# 	"file_url": attach_item.file_url,
# 					# 	"file_name": attach_item.file_name,
# 					# 	"attached_to_name": doc.name,
# 					# 	"attached_to_doctype": doc.doctype,
# 					# 	"folder": "Home"})
# 					# _file.save()
# 				# path = os.getcwd()
# 				# file = open("currentsite.txt","r")
# 				# sitename = file.read()
# 				file_path = os.path.realpath(get_files_path(is_private=1))
# 				# full_path = path+"/"+sitename+"private/files/"+row.engineering_revision+"_"+doc.name+".zip"
# 				full_path = file_path+ "/"+row.engineering_revision+"_"+doc.name+".zip"
# 				file_name = row.engineering_revision+"_"+doc.name+".zip"
# 				file_url = '/private/files/'+file_name
# 				if len(attachments) > 0 :
# 					with ZipFile(full_path,'w') as zip:
# 						for i in attachments:
# 							file_doc = frappe.get_doc("File",{'file_url':i.file_url})
# 							full_file_path = file_doc.get_full_path()
# 							zip.write(full_file_path)
# 					file_doc = frappe.new_doc("File")
# 					file_doc.file_name =file_name
# 					file_doc.folder = "Home/Attachments"
# 					file_doc.attached_to_doctype = doc.doctype
# 					file_doc.attached_to_name = doc.name
# 					file_doc.file_url = file_url
# 					file_doc.insert(ignore_permissions=True)
# 					frappe.db.commit()
# 					doc.reload()


def prepare_zip_attachment_for_rfq(doc, method):
	all_files = []
	for row in doc.items:
		if not row.engineering_revision:
			row.engineering_revision=frappe.db.get_value("Engineering Revision", {"item_code":row.item_code, "is_default":True, "is_active":True}, "name")

		if row.item_code and row.engineering_revision:
			engineering_revision_doc(row, all_files)
	if all_files:
		create_zip_file(row, all_files)
		doc.reload()

def engineering_revision_doc(row, all_files):
	purchasing_package_list = []
	purchasing_package = frappe.db.sql("""SELECT purchasing_package_name from `tabPurchasing Package Table` a join `tabEngineering Revision` b on a.parent = b.name where b.name = '{0}'""".format(row.get("engineering_revision")),as_dict=1,debug=False)
	purchasing_package_list = [item.get('purchasing_package_name') for item in purchasing_package]

	# file_path = os.path.realpath(get_files_path(is_private=1))
	file_path = get_files_path(is_private=1)
	full_path = file_path+ "/"+row.get("item_code")
	os.mkdir(full_path)
	all_files.append(full_path)

	for col in purchasing_package_list:
		package_doc = frappe.get_doc("Package Document",col)
		from frappe.desk.form.load import get_attachments
		attachments = get_attachments(package_doc.doctype, package_doc.name)
		create_folder_with_file(attachments, full_path)

	er_doc = frappe.get_doc("Engineering Revision",row.get("engineering_revision"))
	other_dict={}
	for i in er_doc.other_engineering_revision:
		if i.revision and not i.exclude_purchasing_package:
			other_dict["item_code"]=i.item_code
			other_dict["parent"]=row.get("parent")
			other_dict["engineering_revision"]=i.revision
		elif i.purchase_package_name and not i.exclude_purchasing_package:
			other_dict["item_code"]=i.item_code
			other_dict["parent"]=row.get("parent")
			other_dict["engineering_revision"]="_".join(i.purchase_package_name.split("_")[0:2])
		else:
			if not i.exclude_purchasing_package:
				other_dict["item_code"]=i.item_code
				other_dict["parent"]=row.get("parent")
				other_dict["engineering_revision"]=frappe.db.get_value("Engineering Revision", {"item_code":i.item_code, "is_default":True, "is_active":True}, "name")
		engineering_revision_doc(other_dict, all_files)


def create_folder_with_file(attachments, full_path):
	for i in attachments:
		file_doc = frappe.get_doc("File",{'file_url':i.file_url})
		with open(full_path+f"/{i.file_name}","wb") as f:
			try:
				f.write(file_doc.get_content())
			except Exception as e:
				print(e)

def create_zip_file(row, all_files):
	file_path = get_files_path(is_private=1)
	zip_full_path = file_path+ "/"+row.engineering_revision+"_"+row.parent+".zip"
	file_name = row.engineering_revision+"_"+row.parent+".zip"
	file_url = '/private/files/'+file_name

	with ZipFile(zip_full_path,'w') as zip:
		for full_path in all_files:
			for dirname, subdirs, files in os.walk(full_path):
				zip.write(dirname)
				for filename in files:
					zip.write(os.path.join(dirname, filename))
			shutil.rmtree(full_path)
	file_doc = frappe.new_doc("File")
	file_doc.file_name =file_name
	file_doc.folder = "Home/Attachments"
	file_doc.attached_to_doctype = row.parenttype
	file_doc.attached_to_name = row.parent
	file_doc.file_url = file_url
	file_doc.insert(ignore_permissions=True)
	frappe.db.commit()


@frappe.whitelist()
def set_min_order_qty(doc):
	doc = json.loads(doc)
	min_order_qty_list = []
	if doc:
		if doc.get("items"):
			for row in doc.get("items"):
				min_order_qty = frappe.db.get_value("Item",{'item_code':row.get("item_code")},'min_order_qty')
				if row.get('qty') < min_order_qty:
					row['qty'] = min_order_qty
					min_order_qty_list.append({'item_code':row.get('item_code'),'qty':min_order_qty})
		return min_order_qty_list

@frappe.whitelist()
def consolidate_qty(doc):
	doc = json.loads(doc)
	doc = frappe.get_doc("Request for Quotation",doc.get('name'))
	if doc.get('items'):
		item_data = doc.get('items')
		item_dict = {(item.item_code,item.schedule_date):item.schedule_date for item in doc.get('items')}
		final_data = []
		count = 0
		for item in item_dict:
			total = 0
			count = count + 1
			for info in doc.get('items'):
				item_date_dict = (info.get('item_code'),info.get('schedule_date'))
				if item ==  item_date_dict:
					total = total + info.get('qty')
					item_info = info
			item_info.qty = total
			item_info.idx = count
			final_data.append(item_info)
		doc.items = ''
		for i in final_data:
			doc.append("items",i)
		doc.save()
	return True