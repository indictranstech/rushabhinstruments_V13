from __future__ import unicode_literals
import frappe
import json
import pyqrcode
from PIL import Image, ImageDraw
import io
import requests
import base64
import textwrap
import re
from frappe import _

@frappe.whitelist()
def check_stock(doc,method):
	frappe.db.set_value("Final Work Orders", {'item':doc.production_item, 'sales_order':doc.sales_order}, "wo_status", doc.status)
	frappe.db.commit()
	if doc.get('__islocal')!= 1:
		final_item_status = []
		final_item_percent = []
		ohs = get_current_stock()
		for item in doc.required_items:
			if item.item_code in ohs:
				if item.required_qty <= ohs.get(item.item_code):
					final_item_status.append('Full Qty Available')
					percent_stock = 100
					final_item_percent.append(percent_stock)
				# elif item.required_qty > ohs.get(item.item_code) and ohs.get(item.item_code) > 0:
				elif item.required_qty > ohs.get(item.item_code) and ohs.get(item.item_code) > 0:
					final_item_status.append('Partial Qty Available')
					percent_stock = (ohs.get(item.item_code)/item.required_qty*100)
					final_item_percent.append(percent_stock)

				else : 
					final_item_status.append('Qty Not Available')
					percent_stock = (ohs.get(item.item_code)/item.required_qty*100)
					final_item_percent.append(percent_stock)

		status_list = ['Full Qty Available']
		status_list_pa = ['Partial Qty Available']
		status_list_na = ['Qty Not Available']
		check =  all(item in status_list for item in final_item_status)
		check_pa = all(item in status_list_pa for item in final_item_status)
		check_na = all(item in status_list_na for item in final_item_status)
		min_value = min(final_item_percent) if len(final_item_percent) > 1 else 0
		if check == True:
			frappe.db.set_value("Work Order",doc.name,'item_stock_status','Full Qty Available')
			frappe.db.set_value("Work Order",doc.name,'stock_percentage',min_value)
			frappe.db.commit()
			doc.reload()
		elif check_pa == True:
			frappe.db.set_value("Work Order",doc.name,'item_stock_status','Partial Qty Available')
			frappe.db.set_value("Work Order",doc.name,'stock_percentage',min_value)
			frappe.db.commit()
			doc.reload()
		elif check_na == True : 
			frappe.db.set_value("Work Order",doc.name,'item_stock_status','Qty Not Available')
			frappe.db.set_value("Work Order",doc.name,'stock_percentage',min_value)
			frappe.db.commit()
			doc.reload()
		elif 'Qty Not Available' in final_item_status and 'Partial Qty Available' in final_item_status: 
			frappe.db.set_value("Work Order",doc.name,'item_stock_status','Qty Available For Some Items')
			frappe.db.set_value("Work Order",doc.name,'stock_percentage',min_value)
			frappe.db.commit()
		else: 
			frappe.db.set_value("Work Order",doc.name,'item_stock_status','Partial Qty Available')
			frappe.db.set_value("Work Order",doc.name,'stock_percentage',min_value)
			frappe.db.commit()
			doc.reload()
	doc.reload()
def get_current_stock():
	# 1.get wip warehouse
	wip_warehouse = frappe.db.get_single_value("Manufacturing Settings", 'default_wip_warehouse')
	current_stock = frappe.db.sql("""SELECT item_code,sum(actual_qty) as qty from `tabBin` where warehouse != '{0}' group by item_code """.format(wip_warehouse),as_dict=1)
	ohs_dict = {item.item_code : item.qty for item in current_stock}
	return ohs_dict

@frappe.whitelist()
def add_bom_level(doc,method):
	if doc.bom_no:
		bom_level = frappe.db.get_value("BOM",{'name' : doc.bom_no},'bom_level')
		if bom_level:
			doc.bom_level = bom_level
			
			# frappe.db.set_value("Work Order",doc.name,'bom_level',bom_level)
			# frappe.db.commit()
			# doc.reload()

@frappe.whitelist()
def on_submit(doc,method):
	if doc.required_items:
		for item in doc.required_items:
			if item.engineering_revision:
				er_rev = frappe.get_doc("Engineering Revision",item.engineering_revision)
				if er_rev :
					if not (er_rev.start_date and er_rev.start_transaction and er_rev.document_type):
						er_rev.start_date = doc.planned_start_date
						er_rev.document_type = "Work Order"
						er_rev.start_transaction = doc.name
					er_rev.last_date = doc.planned_start_date
					er_rev.end_document_type = "Work Order"
					er_rev.end_transaction = doc.name
					er_rev.save(ignore_permissions = True)

@frappe.whitelist()
def get_prod_engineering_revision(item_code,bom_no):
	if item_code:
		engineering_revision = frappe.db.sql("""SELECT engineering_revision from `tabItem` where item_code = '{0}'""".format(item_code),as_dict=1)
		engineering_revision[0]['use_specific_engineering_revision'] = 0
		er_from_bom = frappe.db.sql("""SELECT boi.engineering_revision ,boi.use_specific_engineering_revision from `tabBOM` bo join `tabBOM Item` boi on boi.parent = bo.name where bo.name = '{0}' and boi.item_code = '{1}' and boi.engineering_revision != ''""".format(bom_no,item_code),as_dict=1)
		if len(er_from_bom) > 0 and er_from_bom[0].get("engineering_revision") != None:
			return er_from_bom
		else:
			return engineering_revision

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_engineering_revisions_for_filter(doctype, txt, searchfield, start, page_len, filters):
	return frappe.db.sql(""" SELECT name FROM `tabEngineering Revision` where item_code = '{0}' """.format(filters.get("item_code")))
def after_insert(doc,method):
	start_string = doc.name 
	end_string = '.png'
	label_files = frappe.db.sql("""SELECT file_name from `tabFile` where attached_to_name = '{0}' and attached_to_doctype = 'Work Order' and file_name like '{1}%{2}'""".format(doc.name,start_string,end_string),as_dict=1)
	if label_files:
		frappe.db.sql("""DELETE from `tabFile` where attached_to_doctype='Work Order' and attached_to_name=%s and file_name != %s""",
		(doc.name,label_files[0].file_name))
	else:
		frappe.db.sql("""DELETE from `tabFile` where attached_to_doctype='Work Order' and attached_to_name=%s""",
		(doc.name))
	pdf_data=frappe.attach_print('Work Order',doc.name, print_format='Work Order')
	
	_file = frappe.get_doc({
	"doctype": "File",
	"file_name": pdf_data.get('fname'),
	"attached_to_doctype": "Work Order",
	"attached_to_name": doc.name,
	"is_private": 1,
	"content": pdf_data.get('fcontent')
	})
	_file.save()

def validate(doc,method):
	# doc.skip_transfer =1
	prod_item_engineering_revision = get_engineering_revision(doc.production_item)
	doc.engineering_revision = prod_item_engineering_revision
	if doc.engineering_revision:
		manufacturing_package = frappe.db.get_value("Manufacturing Package Table",{'parent':doc.engineering_revision},'manufacturing_package_name')
		doc.manufacturing_package_name = manufacturing_package
	for item in doc.required_items:
		engineering_revision = get_prod_engineering_revision(item.item_code,doc.bom_no)
		item.engineering_revision = engineering_revision[0].get("engineering_revision")
		item.use_specific_engineering_revision = engineering_revision[0].get("use_specific_engineering_revision")
		if item.engineering_revision:
			manufacturing_package = frappe.db.get_value("Manufacturing Package Table",{'parent':item.engineering_revision},'manufacturing_package_name')
			item.manufacturing_package = manufacturing_package
	if not doc.get("__islocal"):
		start_string = doc.name 
		end_string = '.png'
		label_files = frappe.db.sql("""SELECT file_name from `tabFile` where attached_to_name = '{0}' and attached_to_doctype = 'Work Order' and file_name like '{1}%{2}'""".format(doc.name,start_string,end_string),as_dict=1)
		if label_files:
			frappe.db.sql("""DELETE from `tabFile` where attached_to_doctype='Work Order' and attached_to_name=%s and file_name != %s""",
			(doc.name,label_files[0].file_name))
		else:
			frappe.db.sql("""DELETE from `tabFile` where attached_to_doctype='Work Order' and attached_to_name=%s""",
			(doc.name))
		pdf_data=frappe.attach_print('Work Order',doc.name, print_format='Work Order')
		
		_file = frappe.get_doc({
		"doctype": "File",
		"file_name": pdf_data.get('fname'),
		"attached_to_doctype": "Work Order",
		"attached_to_name": doc.name,
		"is_private": 1,
		"content": pdf_data.get('fcontent')
		})
		_file.save()

@frappe.whitelist()
def get_engineering_revision(item_code):
	if item_code:
		engineering_revision = frappe.db.get_value("Item",{'name':item_code},'engineering_revision')
		return engineering_revision

def disable_bom(doc,method):
	bom = frappe.get_doc('BOM',doc.bom_no)
	wos_for_bom = frappe.db.sql("""SELECT COUNT(name) as wo_num FROM `tabWork Order` WHERE bom_no='{}' AND status IN ('Submitted','Not Started','In Process','Draft') GROUP BY bom_no""".format(doc.bom_no), as_dict=True)
	if not wos_for_bom:
		if bom.to_be_disabled and frappe.db.get_value("Item",{'name':bom.item},'auto_disable_old_active_boms'):
			any_mboms = frappe.db.sql("""SELECT name FROM `tabMapped BOM Item` WHERE bom_no='{0}'""".format(bom.name))
			if not any_mboms:
				bom.is_active = 0
				bom.save()
				bom.submit()
				
def label_img(doc,method):
	url = frappe.db.get_value('URL Data',{'sourcedoctype_name':'Work Order'},'url')
	final_string = url + doc.name
	img = Image.new('RGB', (384,192), color='white')
	qrc = pyqrcode.create(final_string)
	inmf = io.BytesIO()
	qrc.png(inmf,scale=6)
	qrcimg = Image.open(inmf)
	qrcimg.thumbnail((72,72))
	img.paste(qrcimg,(26,30))
	d = ImageDraw.Draw(img)
	itemname = textwrap.fill(doc.item_name,width=35)
	d.multiline_text((120,30), "{0}\n\nItem to Manufacture: {1}\n\nQty to Manufacture: {2} \nSales Order: {3}\nWIPWarehouse: {4}\nTarget Warehouse: {5}\nItem Name: {6}".format(doc.name,doc.production_item,doc.qty,doc.sales_order,doc.wip_warehouse,doc.fg_warehouse,itemname), fill=(0,0,0), spacing=1)
	d.text((35,160), "Work Order Traveler", fill=(0,0,0))
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
	imgfile = frappe.get_doc({'doctype':'File','file_name':namestr,'attached_to_doctype':"Work Order",'attached_to_name':doc.name,"content":b64str,"decode":1})
	imgfile.insert()
	


# Overriding Methods
@frappe.whitelist()
def stop_unstop(work_order, status):
	"""Called from client side on Stop/Unstop event"""
	if not frappe.has_permission("Work Order", "write"):
		frappe.throw(_("Not permitted"), frappe.PermissionError)

	pro_order = frappe.get_doc("Work Order", work_order)

	if pro_order.status == "Closed":
		frappe.throw(_("Closed Work Order can not be stopped or Re-opened"))

	pro_order.update_status(status)
	pro_order.update_planned_qty()
	frappe.msgprint(_("Work Order has been {0}").format(status))
	pro_order.notify_update()
	frappe.db.set_value("Final Work Orders", {'item':pro_order.production_item, 'sales_order':pro_order.sales_order}, "wo_status", pro_order.status)
	frappe.db.commit()
	return pro_order.status	
	

def update_status_on_production_planning_with_lead_time(doc, method=None):
	frappe.db.set_value("Final Work Orders", {'item':doc.production_item, 'sales_order':doc.sales_order}, "wo_status", doc.status)
	frappe.db.commit()


def on_trash(doc, method=None):
	frappe.db.set_value("Final Work Orders", {'item':doc.production_item, 'sales_order':doc.sales_order}, "wo_status", "")
	frappe.db.commit()


@frappe.whitelist()
def unstock_items_details(bom_no):
	unstock_items = []
	if bom_no:
		bom_doc = frappe.get_doc("BOM", bom_no)
		for row in bom_doc.items:
			if not frappe.db.get_value("Item", row.item_code, "is_stock_item"):
				unstock_items.append({"item_code":row.item_code, "item_name":row.item_name, "description":row.description, "qty":row.qty})				
	return unstock_items