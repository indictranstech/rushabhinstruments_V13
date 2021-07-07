from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils.background_jobs import enqueue



def on_submit(doc, method = None):
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