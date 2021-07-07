from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils.background_jobs import enqueue



def on_submit(doc, method = None):
	# file_att = []
	# file_att = [frappe.attach_print(doc.doctype, doc.name, file_name=doc.name)]
	# attachments = frappe.db.sql(""" SELECT file_name  FROM tabFile 
	# 			WHERE attached_to_name = '{0}'""".format(doc.name),as_dict=1)
	
	# if attachments:
	# 	for row in attachments:
	# 		_file = frappe.get_doc("File", {"file_name": row.file_name})
	# 		content = _file.get_content()
	# 		if not content:
	# 			return
	# 		attachment_list = {'fname':row.file_name,'fcontent':content}
	# 		file_att.append(attachment_list)

	# sender = frappe.db.get_value("Email Setting",{"email_name": "Purchase Order Email"},"email_id")
	# if doc.suppliers:
	# 	recipient = suppliers.contact_email
	# if recipient:
	# 	frappe.sendmail(
	# 		sender = sender,
	# 		recipients = recipient,
	# 		subject = "Request For Quotation : {0}".format(doc.name),
	# 		message = "Request For Quotation : " + "https://uatrushabhinstruments.indictranstech.com/app/request-for-quotation/{0}".format(doc.name),
	# 		attachments = file_att,
	# 		)
	send_email_without_reference_to_supplier(doc, method)

def send_email_without_reference_to_supplier(doc, method):
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
				"attachments": [frappe.attach_print("Request for Quotation", doc.name)]
			}
			enqueue(method=frappe.sendmail, queue='short', timeout=300, is_async=True, delayed=False, **email_args)
		data.clear()