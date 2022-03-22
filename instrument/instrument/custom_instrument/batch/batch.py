import frappe
from frappe.model.naming import make_autoname
from frappe.utils import nowdate, cstr, flt, cint, now, getdate,get_datetime,time_diff_in_seconds,add_to_date,time_diff_in_seconds,add_days,today
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import io
import base64
import pyqrcode
import requests

def autoname(doc, method):
	if doc.item:
		now = datetime.now()
		currentMonth = datetime.now().month
		currentMonth = '{:02d}'.format(currentMonth)
		currentYear = datetime.now().year
		
		engineering_revision = frappe.db.get_value("Item",{'item_code':doc.item},'engineering_revision')
		if doc.reference_doctype == 'Purchase Receipt':
			if doc.reference_name:
				pr_doc = frappe.get_doc("Purchase Receipt",doc.reference_name)
				for item in pr_doc.items:
					if item.item_code == doc.item:
						doc.name = make_autoname('BN-' + str(item.engineering_revision) + '-'+str(currentYear) +'-'+str(currentMonth) + '-' + '.#####')
						doc.batch_id = doc.name
						return doc.name
		elif doc.reference_doctype == 'Stock Entry':
			if doc.reference_name:
				se_doc = frappe.get_doc("Stock Entry",doc.reference_name)
				for item in se_doc.items:
					if item.item_code == doc.item:
						doc.name = make_autoname('BN-' + str(item.engineering_revision) + '-'+str(currentYear) +'-'+str(currentMonth) + '-' + '.#####')
						doc.batch_id = doc.name
						return doc.name
		elif engineering_revision:
			doc.name = make_autoname('BN-' + str(item.engineering_revision) + '-'+str(currentYear) +'-'+str(currentMonth) + '-' + '.#####')
			doc.batch_id = doc.name
			return doc.name
		else:
			doc.name = make_autoname('BN-' + '-'+str(currentYear) +'-'+str(currentMonth) + '-' + '.#####')
			doc.batch_id = doc.name
			return doc.name

def label_img(doc, method):
	url = frappe.db.get_value('URL Data',{'sourcedoctype_name':'Batch'},'url')
	final_string = url +  doc.name
	warehouse = frappe.db.get_value('Stock Ledger Entry',{'batch_no':doc.name,'item_code':doc.item,'posting_date':doc.manufacturing_date},'warehouse')
	if not warehouse:
		warehouse = ""
	img = Image.new('RGB', (384,192), color='white')
	qrc = pyqrcode.create(final_string)
	inmf = io.BytesIO()
	qrc.png(inmf,scale=6)
	qrcimg = Image.open(inmf)
	qrcimg.thumbnail((72,72))
	img.paste(qrcimg,(26,30))
	d = ImageDraw.Draw(img)
	d.multiline_text((120,35), "{0}\n\n{1}\n\nTotal Qty: {2}\nBatch: {3}\nBatch Name: {4}\nLocation: {5}".format(doc.item,doc.item_name,doc.batch_qty,doc.batch_id,doc.name,warehouse), fill=(0,0,0), spacing=1)
	d.text((30,160), "Batch Traveler", fill=(0,0,0))
	barcode = requests.get('https://barcode.tec-it.com/barcode.ashx?data={0}&code=Code128&translate-esc=true'.format(doc.item))
	barc = Image.open(io.BytesIO(barcode.content))
	barc = barc.resize((220,15))
	img.paste(barc,(140,160))
	imgbuffer = io.BytesIO()
	img.save(imgbuffer, format='PNG')
	b64str = base64.b64encode(imgbuffer.getvalue())
	fname = frappe.db.get_value('File',{'file_name':doc.name+"-label.png"},'name')
	if fname:
		frappe.delete_doc('File',fname)
	imgfile = frappe.get_doc({'doctype':'File','file_name':doc.name+"-label.png",'attached_to_doctype':"Batch",'attached_to_name':doc.name,"content":b64str,"decode":1})
	imgfile.insert()
