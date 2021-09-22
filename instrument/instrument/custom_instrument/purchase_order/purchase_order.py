from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.desk.form.load import get_attachments

def on_submit(doc, method = None):
	file_att = []
	file_att = [frappe.attach_print(doc.doctype, doc.name, file_name=doc.name)]
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

	sender = frappe.db.get_value("Email Setting",{"email_name": "Purchase Order Email"},"email_id")
	recipient = doc.contact_email
	if recipient:
		frappe.sendmail(
			sender = sender,
			recipients = recipient,
			subject = "Purchase Order : {0}".format(doc.name),
			message = "Purchase Order : " + "https://uatrushabhinstruments.indictranstech.com/app/purchase-order/{0}".format(doc.name),
			attachments = file_att,
			)
	attach_purchasing_docs(doc,method)

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_engineering_revisions_for_filter(doctype, txt, searchfield, start, page_len, filters):
	return frappe.db.sql(""" SELECT name FROM `tabEngineering Revision` where item_code = '{0}' """.format(filters.get("item_code")))

def validate(doc,method):
	if doc.items:
		for item in doc.items:
			engineering_revision = frappe.db.get_value("Item",{'item_code':item.item_code},'engineering_revision')
			item.default_engineering_revision = engineering_revision
	frappe.db.sql("""delete from `tabFile` where attached_to_doctype='Purchase Order' and attached_to_name=%s""",
		(doc.name),debug=1)

def attach_purchasing_docs(doc, method):
	for row in doc.items:
		if row.item_code and row.engineering_revision:
			purchasing_package = frappe.db.sql("""SELECT purchasing_package_name from `tabPurchasing Package Table` a join `tabEngineering Revision` b on a.parent = b.name where b.name = '{0}'""".format(row.engineering_revision),as_dict=1,debug=1)
			purchasing_package_list = [item.purchasing_package_name for item in purchasing_package]
			for row in purchasing_package_list:
				package_doc = frappe.get_doc("Package Document",row)
				"""Copy attachments from `package doc`"""
				from frappe.desk.form.load import get_attachments

				#loop through attachments
				for attach_item in get_attachments(package_doc.doctype, package_doc.name):

					#save attachments to new doc
					_file = frappe.get_doc({
						"doctype": "File",
						"file_url": attach_item.file_url,
						"file_name": attach_item.file_name,
						"attached_to_name": doc.name,
						"attached_to_doctype": doc.doctype,
						"folder": "Home/Attachments"})
					_file.save()