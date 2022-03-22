from __future__ import unicode_literals
import frappe
import json
import requests
from PIL import Image, ImageDraw
import io
import base64
import pyqrcode



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
	d.text((150,50), doc.name, fill=(0,0,0))
	d.multiline_text((150,70), "Production Item: {0}\nQty to Manufacture: {1}".format(doc.production_item,doc.for_quantity) , fill=(0,0,0), spacing=2)
	d.multiline_text((150,90), "Operation: {0}\nWorkstation: {1}\nWork Order: {2}\nItem Name: {3}".format(doc.operation,doc.workstation,doc.work_order,doc.item_name) , fill=(0,0,0), spacing=2)
	d.text((40,160), "Job Card Traveler", fill=(0,0,0))
	barcode = requests.get('https://barcode.tec-it.com/barcode.ashx?data={0}&code=Code128&translate-esc=true'.format(doc.production_item))
	barc = Image.open(io.BytesIO(barcode.content))
	barc = barc.resize((220,15))
	img.paste(barc,(140,160))
	imgbuffer = io.BytesIO()
	img.save(imgbuffer, format='PNG')
	b64str = base64.b64encode(imgbuffer.getvalue())
	fname = frappe.db.get_value('File',{'file_name':doc.name+"-label.png"},'name')
	if fname:
		frappe.delete_doc('File',fname)
	imgfile = frappe.get_doc({'doctype':'File','file_name':doc.name+"-label.png",'attached_to_doctype':"Job Card",'attached_to_name':doc.name,"content":b64str,"decode":1})
	imgfile.insert()
	
