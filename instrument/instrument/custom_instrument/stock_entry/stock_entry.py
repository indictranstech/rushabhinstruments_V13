from __future__ import unicode_literals
import frappe
from PIL import Image, ImageDraw
import requests
import io
import base64
import pyqrcode
import re


def validate(doc,method):
	if doc.work_order:
		if doc.items:
			for item in doc.items:
				if item.s_warehouse:
					engineering_revision = frappe.db.get_value("Work Order Item",{'item_code':item.item_code,'parent':doc.work_order},'engineering_revision')
					manufacturing_package = frappe.db.get_value("Work Order Item",{'item_code':item.item_code,'parent':doc.work_order},'manufacturing_package')
					item.engineering_revision = engineering_revision
					item.manufacturing_package = manufacturing_package
				if item.t_warehouse:
					engineering_revision = frappe.db.get_value("Work Order",{'production_item':item.item_code,'name':doc.work_order},'engineering_revision')
					manufacturing_package = frappe.db.get_value("Work Order",{'production_item':item.item_code,'name':doc.work_order},'manufacturing_package_name')
					item.engineering_revision = engineering_revision
					item.manufacturing_package = manufacturing_package
@frappe.whitelist()
def on_submit(doc,method):
	if doc.work_order_pick_list:
		pick_list_doc = frappe.get_doc("Work Order Pick List",doc.work_order_pick_list)
		if pick_list_doc :
			for item in pick_list_doc.work_orders:
				if item.work_order == doc.work_order:
					item.stock_entry_status = "Submitted"
			pick_list_doc.save()
			pick_list_doc.submit()
@frappe.whitelist()
def get_items_from_pick_list(pick_list,work_order):
	if pick_list:
		qty_of_finish_good = frappe.db.get_value("Pick Orders",{'parent':pick_list,'work_order':work_order},'qty_of_finished_goods')
		items = frappe.db.sql("""SELECT item_code,warehouse as s_warehouse,picked_qty,work_order,stock_uom,engineering_revision,batch_no from `tabWork Order Pick List Item` where parent = '{0}' and work_order = '{1}' and picked_qty > 0""".format(pick_list,work_order),as_dict =1)
		# work_order_doc = frappe.get_doc("Work Order",work_order)
		# items.append({'item_code':work_order_doc.production_item,'t_warehouse':work_order_doc.fg_warehouse,'picked_qty':qty_of_finish_good,'stock_uom':work_order_doc.stock_uom,'engineering_revision':work_order_doc.engineering_revision})
		return items,qty_of_finish_good

# @frappe.whitelist()
# def before_save(doc):
# 	if doc.work_order_pick_list:
# 		if doc.items:
# 			qty_of_finish_good = frappe.db.get_value("Pick Orders",{'parent':doc.work_order_pick_list,'work_order':doc.work_order},'qty_of_finished_goods')
# 			doc.fg_completed_qty = qty_of_finish_good

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_warehouse_for_query(doctype, txt, searchfield, start, page_len, filters):
	item_doc = frappe.get_cached_doc('Item', filters.get('parent'))
	return frappe.db.sql(""" SELECT warehouse FROM `tabItem Locations` where parent = '{0}' """.format(filters.get("parent")))
@frappe.whitelist()
def get_target_warehouse(work_order):
	item = frappe.db.get_value("Work Order",{'name':work_order},'production_item')
	if item:
		item_data = frappe.db.sql(""" SELECT warehouse FROM `tabItem Locations` where parent = '{0}' """.format(item),as_dict=1)
		item_list = [item.warehouse for item in item_data]
		return item_list
		
def label_img(doc,method):
	url = frappe.db.get_value('URL Data',{'sourcedoctype_name':'Stock Entry'},'url')
	final_string = url + doc.name
	img = Image.new('RGB', (384,192), color='white')
	qrc = pyqrcode.create(final_string)
	inmf = io.BytesIO()
	qrc.png(inmf,scale=6)
	qrcimg = Image.open(inmf)
	qrcimg.thumbnail((72,72))
	img.paste(qrcimg,(26,30))
	d = ImageDraw.Draw(img)
	d.multiline_text((120,35), "{0}\n\n{1}\n\nWork Order: {2}\nTarget Warehouse: {3}".format(doc.name,doc.purpose,doc.work_order,doc.to_warehouse), fill=(0,0,0), spacing=2)
	d.text((35,160), "Stock Entry Traveler", fill=(0,0,0))
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
	imgfile = frappe.get_doc({'doctype':'File','file_name':namestr,'attached_to_doctype':"Stock Entry",'attached_to_name':doc.name,"content":b64str,"decode":1})
	imgfile.insert()
