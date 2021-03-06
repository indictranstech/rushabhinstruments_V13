from __future__ import unicode_literals
import frappe
from PIL import Image, ImageDraw
import io
import base64
import pyqrcode
import re

def label_img(doc,method):
	url = frappe.db.get_value('URL Data',{'sourcedoctype_name':'Work Order Pick List'},'url')
	final_string = url + doc.name
	img = Image.new('RGB', (384,192), color='white')
	qrc = pyqrcode.create(final_string)
	inmf = io.BytesIO()
	qrc.png(inmf,scale=6)
	qrcimg = Image.open(inmf)
	work_orders = frappe.db.get_list("Pick Orders",{'parent':doc.name},pluck='work_order')
	wos_str = ""
	for order in work_orders:
		wos_str = wos_str + order + "\n"
	qrcimg.thumbnail((72,72))
	img.paste(qrcimg,(26,30))
	d = ImageDraw.Draw(img)
	d.multiline_text((120,35), "{0}\n\nWork Orders: {1}".format(doc.name,wos_str), fill=(0,0,0), spacing=1)
	d.text((35,160), "Work Order Pick List Traveler", fill=(0,0,0))
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
	imgfile = frappe.get_doc({'doctype':'File','file_name':namestr,'attached_to_doctype':"Work Order Pick List",'attached_to_name':doc.name,"content":b64str,"decode":1})
	imgfile.insert()
