from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from PIL import Image, ImageDraw
import pyqrcode
import io
import base64
import requests
import textwrap


def validate(doc,method):
	if doc.item_attribute_table:
		attribute_list = [item.attribute for item in doc.item_attribute_table]
		attribute_set = set(attribute_list)
		if len(attribute_set) != len(attribute_list):
			frappe.throw("Duplicate Attribute Not Allowed")

	warehouse_list  = []
	if doc.warehouses:
		for row in doc.warehouses:
			warehouse_list.append(row.warehouse)

	if doc.item_defaults:
		for row in doc.item_defaults:
			if row.default_warehouse not in warehouse_list:
				doc.append('warehouses',{
					'warehouse':row.default_warehouse
					})
				# frappe.throw("Please Add Default Warehouse {0} in Item Locations".format(row.default_warehouse))

def disable_old_boms(doc,method):
	if doc.auto_disable_old_active_boms:
		old_boms = frappe.db.sql("""SELECT name from `tabBOM` WHERE item='{0}' and name<(SELECT name FROM `tabBOM` WHERE item='{0}' AND is_default=1) """.format(doc.name), as_dict=1)
		for bom in old_boms:
			bom_doc = frappe.get_doc('BOM', bom)
			if bom_doc.is_active:
				any_wos = frappe.db.sql("""SELECT name FROM `tabWork Order` WHERE bom_no='{0}' AND status IN ('Submitted','Not Started', 'In Process','Draft')""".format(bom['name']))
				any_mboms = frappe.db.sql("""SELECT name FROM `tabMapped BOM Item` WHERE bom_no='{0}'""".format(bom['name']))
				if not any_wos and not any_mboms:
					bom_doc.is_active = 0
				if any_wos:
					bom_doc.to_be_disabled = 1
				bom_doc.save()
				bom_doc.submit()

def label_img(doc,method):
	url = frappe.db.get_value('URL Data',{'sourcedoctype_name':'Item'},'url')
	final_string = url + doc.name
	img = Image.new('RGB', (192,192), color='white')
	qrc = pyqrcode.create(final_string)
	inmf = io.BytesIO()
	qrc.png(inmf,scale=6)
	qrcimg = Image.open(inmf)
	qrcimg.thumbnail((72,72))
	img.paste(qrcimg,(12,12))
	d = ImageDraw.Draw(img)
	itemname = textwrap.fill(text = doc.item_name,width=20)
	d.text((90,10), itemname, fill=(0,0,0))
	d.text((12,96), doc.name, fill=(0,0,0))
	item_locations = frappe.db.get_list('Item Locations',{'parent':doc.name},pluck='warehouse')
	locs_str = ""
	for loc in item_locations:
		locs_str += loc
	locs_str = textwrap.fill(text=locs_str,width=40)
	d.text((12,110), "Item Locations: {0}".format(locs_str), fill=(0,0,0))
	barcode = requests.get('https://barcode.tec-it.com/barcode.ashx?data={0}&code=Code128&translate-esc=true'.format(doc.item_code))
	barc = Image.open(io.BytesIO(barcode.content))
	barc = barc.resize((180,20))
	img.paste(barc,(6,160))
	imgbuffer = io.BytesIO()
	img.save(imgbuffer, format='PNG')
	b64str = base64.b64encode(imgbuffer.getvalue())
	fname = frappe.db.get_value('File',{'file_name':doc.name+"-label.png"},'name')
	if fname:
		frappe.delete_doc('File',fname)
	imgfile = frappe.get_doc({'doctype':'File','file_name':doc.name+"-label.png",'attached_to_doctype':"Item",'attached_to_name':doc.name,"content":b64str,"decode":1})
	imgfile.insert()
