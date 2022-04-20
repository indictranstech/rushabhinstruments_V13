from __future__ import unicode_literals
import frappe
import json
import requests
from PIL import Image, ImageDraw
import io
import base64
import pyqrcode
import re


def validate(doc,method):
	if not doc.get("__islocal"):
		file_name = doc.name + '.pdf'
		frappe.db.sql("""DELETE from `tabFile` where attached_to_doctype='Job Card' and attached_to_name=%s and file_name = %s""",
			(doc.name,file_name))
		pdf_data=frappe.attach_print('Job Card',doc.name, print_format='Job Card Print With QR')
		
		_file = frappe.get_doc({
		"doctype": "File",
		"file_name": pdf_data.get('fname'),
		"attached_to_doctype": "Job Card",
		"attached_to_name": doc.name,
		"is_private": 1,
		"content": pdf_data.get('fcontent')
		})
		_file.save()
@frappe.whitelist()
def get_engineering_revision(item_code,work_order):
	if item_code:
		engineering_revision = frappe.db.get_value("Item",{'name':item_code},'engineering_revision')
		er_from_wo = frappe.db.get_value("Work Order Item",{'parent':work_order,'item_code':item_code},'engineering_revision')
		if er_from_wo:
			return er_from_wo
		else:
			return engineering_revision
			
def label_img(doc,method):
	url = frappe.db.get_value('URL Data',{'sourcedoctype_name':'Job Card'},'url')
	final_string = url + doc.name
	img = Image.new('RGB', (384,192), color='white')
	qrc = pyqrcode.create(final_string)
	inmf = io.BytesIO()
	qrc.png(inmf,scale=6)
	qrcimg = Image.open(inmf)
	qrcimg.thumbnail((72,72))
	img.paste(qrcimg,(26,30))
	d = ImageDraw.Draw(img)
	d.multiline_text((120,35), "{0}\n\nProduction Item: {1}\nQty to Manufacture: {2}\n\nOperation: {3}\nWorkstation: {4}\nWork Order: {5}\nItem Name: {6}".format(doc.name,doc.production_item,doc.for_quantity,doc.operation,doc.workstation,doc.work_order,doc.item_name), fill=(0,0,0), spacing=1)
	d.text((30,160), "Job Card Traveler", fill=(0,0,0))
	barcode = requests.get('https://barcode.tec-it.com/barcode.ashx?data={0}&code=Code128&translate-esc=true'.format(doc.production_item))
	barc = Image.open(io.BytesIO(barcode.content))
	barc = barc.resize((220,15))
	img.paste(barc,(140,160))
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
	imgfile = frappe.get_doc({'doctype':'File','file_name':namestr,'attached_to_doctype':"Job Card",'attached_to_name':doc.name,"content":b64str,"decode":1})
	imgfile.insert()

