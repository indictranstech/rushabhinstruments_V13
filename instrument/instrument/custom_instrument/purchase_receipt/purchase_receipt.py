from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

def validate(doc,method):
	for item in doc.items:
		if item.engineering_revision:
			purchasing_package = frappe.db.get_value("Purchasing Package Table",{'parent':item.engineering_revision},'purchasing_package_name')
			item.purchasing_package = purchasing_package

# class Purchase_Receipt(Document):
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
			subject = "Purchase Receipt : {0}".format(doc.name),
			message = "Purchase Receipt: "+"https://uatrushabhinstruments.indictranstech.com/app/purchase-receipt/{0}".format(doc.name),
			attachments = file_att,
			)

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_warehouse_for_query(doctype, txt, searchfield, start, page_len, filters):
	item_doc = frappe.get_cached_doc('Item', filters.get('parent'))
	return frappe.db.sql(""" SELECT warehouse FROM `tabItem Locations` where parent = '{0}' """.format(filters.get("parent")))

@frappe.whitelist()
def get_engineering_revision(item_code,purchase_order_item):
	if item_code and purchase_order_item:
		engineering_revision = frappe.db.get_value("Purchase Order Item",{'name':purchase_order_item,item_code:item_code},'engineering_revision')
		purchasing_package = frappe.db.get_value("Purchasing Package Table",{'parent':engineering_revision},'purchasing_package_name')
		final_data = []
		final_data.append(engineering_revision)
		final_data.append(purchasing_package)
		return final_data

@frappe.whitelist()
def get_purchasing_package(engineering_revision):
	purchasing_package = frappe.db.get_value("Purchasing Package Table",{'parent':engineering_revision},'purchasing_package_name')
	return purchasing_package
