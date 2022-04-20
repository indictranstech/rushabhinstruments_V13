from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

def validate(doc,method):
	if not doc.get("__islocal"):
		frappe.db.sql("""DELETE from `tabFile` where attached_to_doctype='Payment Entry' and attached_to_name=%s""",
			(doc.name))
		pdf_data=frappe.attach_print('Payment Entry',doc.name, print_format='Cheque Template v1')
		
		_file = frappe.get_doc({
		"doctype": "File",
		"file_name": pdf_data.get('fname'),
		"attached_to_doctype": "Payment Entry",
		"attached_to_name": doc.name,
		"is_private": 1,
		"content": pdf_data.get('fcontent')
		})
		_file.save()