from __future__ import unicode_literals
import frappe
from PIL import Image, ImageDraw
import io
import base64
import pyqrcode
import re

def label_img(doc,method):
	url = frappe.db.get_value('URL Data',{'sourcedoctype_name':'Pick List'},'url')
	final_string = url + doc.name
	img = Image.new('RGB', (384,192), color='white')
	qrc = pyqrcode.create(final_string)
	inmf = io.BytesIO()
	qrc.png(inmf,scale=6)
	qrcimg = Image.open(inmf)
	qrcimg.thumbnail((72,72))
	img.paste(qrcimg,(26,30))
	d = ImageDraw.Draw(img)
	d.multiline_text((120,35), "{0}\n\nWork Order: {1}\nQty of Finished Goods Items: {2}".format(doc.name,doc.work_order,doc.for_qty), fill=(0,0,0), spacing=2)
	d.text((35,160), "Pick List Traveler", fill=(0,0,0))
	imgbuffer = io.BytesIO()
	img.save(imgbuffer, format='PNG')
	b64str = base64.b64encode(imgbuffer.getvalue())
	fname = frappe.db.get_list('File',filters={'attached_to_name':doc.name},fields=['name','file_name'])
	count=0
	if fname:
		for filedoc in fname:
			if "label" in filedoc.file_name:
				lnum = re.search("label(.*).png",filedoc.file_name)
				count = int(lnum.group(1))+1
				frappe.delete_doc('File',filedoc.name)
	namestr = doc.name + "-label{0}".format(count) + ".png"
	imgfile = frappe.get_doc({'doctype':'File','file_name':namestr,'attached_to_doctype':"Pick List",'attached_to_name':doc.name,"content":b64str,"decode":1})
	imgfile.insert()
def after_insert(doc,method):
	start_string = doc.name 
	end_string = '.png'
	label_files = frappe.db.sql("""SELECT file_name from `tabFile` where attached_to_name = '{0}' and attached_to_doctype = 'Pick List' and file_name like '{1}%{2}'""".format(doc.name,start_string,end_string),as_dict=1)
	if label_files:
		frappe.db.sql("""DELETE from `tabFile` where attached_to_doctype='Pick List' and attached_to_name=%s and file_name != %s""",
		(doc.name,label_files[0].file_name))
	else:
		frappe.db.sql("""DELETE from `tabFile` where attached_to_doctype='Pick List' and attached_to_name=%s""",
	(doc.name))
	# file_url = '/private/files/' + doc.name + '.pdf'
	# frappe.db.sql("""delete from `tabFile` where attached_to_doctype='Pick List' and attached_to_name=%s and file_url = %s""",
	# (doc.name,file_url))
	pdf_data=frappe.attach_print('Pick List',doc.name, print_format='Pick List Print With QR')
	
	_file = frappe.get_doc({
	"doctype": "File",
	"file_name": pdf_data.get('fname'),
	"attached_to_doctype": "Pick List",
	"attached_to_name": doc.name,
	"is_private": 1,
	"content": pdf_data.get('fcontent')
	})
	_file.save()

def validate(doc,method):
	if not doc.get("__islocal"):
		start_string = doc.name 
		end_string = '.png'
		label_files = frappe.db.sql("""SELECT file_name from `tabFile` where attached_to_name = '{0}' and attached_to_doctype = 'Pick List' and file_name like '{1}%{2}'""".format(doc.name,start_string,end_string),as_dict=1)
		if label_files:
			frappe.db.sql("""DELETE from `tabFile` where attached_to_doctype='Pick List' and attached_to_name=%s and file_name != %s""",
			(doc.name,label_files[0].file_name))
		else:
			frappe.db.sql("""DELETE from `tabFile` where attached_to_doctype='Pick List' and attached_to_name=%s""",
		(doc.name))
		# file_url = '/private/files/' + doc.name + '.pdf'
		# frappe.db.sql("""delete from `tabFile` where attached_to_doctype='Pick List' and attached_to_name=%s and file_url = %s""",
		# (doc.name,file_url))
		pdf_data=frappe.attach_print('Pick List',doc.name, print_format='Pick List Print With QR')
		
		_file = frappe.get_doc({
		"doctype": "File",
		"file_name": pdf_data.get('fname'),
		"attached_to_doctype": "Pick List",
		"attached_to_name": doc.name,
		"is_private": 1,
		"content": pdf_data.get('fcontent')
		})
		_file.save()
