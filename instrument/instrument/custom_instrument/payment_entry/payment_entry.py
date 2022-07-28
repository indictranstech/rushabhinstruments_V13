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
def after_insert(doc,method):
	create_pdf_for_check_and_attached(doc)
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



def create_pdf_for_check_and_attached(doc):
	import pdfkit
	from PyPDF2 import PdfFileReader, PdfFileWriter
	import io
	from frappe.utils import get_files_path

	data = {}
	child_data = []
	options={}
	options["margin-right"] = "2mm"
	options["margin-left"] = "2mm"
	options["margin-top"] = "25mm"
	data["posting_date"] = doc.posting_date
	data["party_name"] = doc.party_name
	data["paid_amount"] = doc.paid_amount
	data["total_allocated_amount"] = doc.total_allocated_amount
	for row in doc.references:
		child_data.append({
			"reference_name":row.reference_name, 
			"date":row.due_date,
			"original_amount":row.total_amount,
			"balance_amount":row.outstanding_amount,
			"payment":row.allocated_amount 
		})
	data["references"] = child_data

	path = "instrument/instrument/custom_instrument/payment_entry/payment_entry.html"
	html = frappe.render_template(path,{'data':data})
	filedata = pdfkit.from_string(html, False, options=options)
	file_path = get_files_path(is_private=1)
	file_name = "Cheque-Print-"+doc.name+".pdf"
	full_path = file_path+ "/"+file_name
	file_url = '/private/files/'+file_name
	with open(full_path,"wb") as f:
		f.write(filedata)

	file_doc = frappe.new_doc("File")
	file_doc.file_name =file_name
	file_doc.folder = "Home/Attachments"
	file_doc.attached_to_doctype = doc.doctype
	file_doc.attached_to_name = doc.name
	file_doc.file_url = file_url
	file_doc.insert(ignore_permissions=True)
	frappe.db.commit()


