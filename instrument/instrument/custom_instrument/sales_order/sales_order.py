from __future__ import unicode_literals
import frappe
from frappe.model.document import Document


def on_submit(doc, method = None):
	# reminder on submit
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
	sender = frappe.db.get_value("Email Setting",{"email_name": "Sales Order Email"},"email_id")
	recipient = doc.contact_email
	if recipient:
		frappe.sendmail(
			sender = sender,
			recipients = recipient,
			subject = "Sales Order : {0}".format(doc.name),
			message = "Sales Order: "+"https://uatrushabhinstruments.indictranstech.com/app/sales-order/{0}".format(doc.name),
			attachments = file_att,
			)