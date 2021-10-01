# Copyright (c) 2021, instrument and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from erpnext.manufacturing.doctype.bom.bom import get_bom_items_as_dict
from erpnext.stock.doctype.item.item import get_item_defaults
# from erpnext.stock.doctype.batch.batch import get_batch_no
from frappe import _
from frappe.utils import cint, flt, get_link_to_form

import json
from datetime import datetime
from frappe.utils import nowdate,nowtime, today, flt
from frappe.utils.pdf import get_pdf
from frappe.utils.xlsxutils import make_xlsx
import openpyxl
from openpyxl import load_workbook
from openpyxl.styles import Font, Color, Fill, PatternFill, Alignment
from openpyxl.drawing.image import Image
from openpyxl import Workbook
from six import StringIO, string_types
import sys
from openpyxl import Workbook
from openpyxl.styles import Alignment
from openpyxl.utils.cell import get_column_letter

class WorkOrderPickList(Document):
	@frappe.whitelist()
	def get_work_order_items(self):
		final_raw_item_list = []
		
		final_data = dict()
		if self.work_orders:
			for item in self.work_orders:
				item_list = []
				bom_no = frappe.db.get_value("Work Order",{'name':item.work_order},'bom_no')
				if bom_no:
					# Get all the required raw materials with required qty according to qty of qty_of_finished_goods
					raw_materials = get_raw_material(bom_no,self.company,item.qty_of_finished_goods,item.work_order)
					final_raw_item_list.append(raw_materials)
					i_list = [item for item in raw_materials]
					for i in i_list:
						item_list.append(i)
					final_item_list= list(set(item_list))
					# Get all the avaialble locations for required items
					item_locations_dict = get_item_locations(final_item_list,self.company)
					
					# Manipulate in order to show in table
					for row in raw_materials:
						engineering_revision = frappe.db.get_value("Work Order Item",{'parent':item.work_order,'item_code':row},'engineering_revision')

						if row in item_locations_dict:
							col = item_locations_dict.get(row)
							for i in col:
								# Fetch batch  FIFO basis
								batch_no = get_batch_no(row, i.get("warehouse"),raw_materials.get(row).get("qty"), throw=False)
								i['required_qty'] = raw_materials.get(row).get("qty")
								i['picked_qty'] = 0
								i['stock_uom'] = raw_materials.get(row).get('stock_uom')
								i['engineering_revision'] = engineering_revision
								i['batch_no'] = batch_no
								# Prefill the picked qty
								if batch_no:
									batch_qty = frappe.db.get_value("Batch",{'name':batch_no},'batch_qty')
									if batch_qty >= raw_materials.get(row).get("qty"):
										i['picked_qty'] = raw_materials.get(row).get("qty")
									else:
										i['picked_qty'] = batch_qty	
					final_data[item.work_order] = item_locations_dict
			# add items in item_locations
			work_order_list = [item.work_order for item in self.work_orders]
			for work_order in work_order_list:
				for row in final_data:
					if row == work_order:
						final_row = final_data.get(row)
						for i in final_row:
							item_data = get_item_defaults(i, self.company)
							j = final_row.get(i)
							for d in j:
								self.append("work_order_pick_list_item",{
									"item_code": i,
									"item_name": item_data.get("item_name"),
									"warehouse":d.get("warehouse"),
									"required_qty":d.get("required_qty"),
									"stock_qty": d.get("qty"),
									"work_order" : row,
									"picked_qty" : d.get('picked_qty'),
									"uom" : d.get('stock_uom'),
									"stock_uom":d.get('stock_uom'),
									"description" :item_data.get('description'),
									"item_group" : item_data.get("item_group"),
									"engineering_revision" : d.get("engineering_revision"),
									"batch_no" : d.get('batch_no')
								})
		self.save()
							
def get_item_locations(item_list,company):
	item_locations_dict = dict()
	wip_warehouse = frappe.db.get_single_value("Manufacturing Settings", "default_wip_warehouse")
	warehouses = [x.get('name') for x in frappe.get_list("Warehouse", {'company': company}, "name")]
	if wip_warehouse in warehouses:
		warehouses.remove(wip_warehouse)
	for item in item_list :
		item_locations = frappe.get_all('Bin',
							fields=['warehouse', 'actual_qty as qty'],
							filters={'item_code':item,
							'actual_qty': ['>', 0],
							'warehouse' :['in', warehouses]
							},
							order_by='creation')
		item_locations_dict[item] = item_locations
	return item_locations_dict
# 	
def get_raw_material(bom_no, company, qty,work_order):
	try:
		work_order_doc = frappe.get_doc("Work Order",work_order)
		if work_order_doc.use_multi_level_bom == 1:
			raw_materials = get_bom_items_as_dict(bom_no,company,qty,fetch_exploded=1)
		else:
			raw_materials = get_bom_items_as_dict(bom_no,company,qty,fetch_exploded=0)
		for item in raw_materials:
			item_info = raw_materials.get(item)
			item_info['work_order'] = work_order
		return raw_materials
	except Exception as e:
		frappe.log_error(message = frappe.get_traceback() , title = "Get Raw Material")

@frappe.whitelist()
def get_work_orders(production_plan):
	if production_plan:
		work_order_data = frappe.db.sql("""SELECT wo.name,(wo.qty-wo.produced_qty) as qty from `tabWork Order` wo where production_plan = '{0}' and (wo.produced_qty < wo.qty)  and wo.status in ('In process','Not Started') and wo.docstatus = 1 order by wo.name asc""".format(production_plan),as_dict =1,debug=1)
		return work_order_data

@frappe.whitelist()
def validate_picked_qty(work_order,required_qty,picked_qty,doc_name,row_name,item_code):
	picked_qty = frappe.db.sql("""SELECT sum(picked_qty) as picked_qty from `tabWork Order Pick List Item` where parent = '{0}' and work_order = '{1}' and item_code = '{2}' and name != '{3}'""".format(doc_name,work_order,item_code,row_name),as_dict=1)
	return picked_qty[0].get('picked_qty')

@frappe.whitelist()
def get_pick_list_details(doc):
	data = json.loads(doc)
	header = ['Sr.No','Work Order','Qty of Finished Good']
	header_2 = ['Sr.No','Item','Warehouse','Work Order','Required Qty','Stock Qty','Picked Qty','Item Name','Description','Item Group','Engineering Revision','UOM','Stock UOM','Conversion Factor']
	
	book = Workbook()
	sheet = book.active
	
	row = 1
	col = 1

	cell = sheet.cell(row=row,column=col)
	cell.value = 'Company'
	cell.font = cell.font.copy(bold=True)
	cell.alignment = cell.alignment.copy(horizontal="center", vertical="center")
	cell.fill = PatternFill(start_color='ffff00', end_color='ffff00', fill_type = 'solid')

	cell = sheet.cell(row=row,column=col+1)
	cell.value = data.get("company")
	cell.font = cell.font.copy(bold=True)
	cell.alignment = cell.alignment.copy(horizontal="center", vertical="center")
	cell.fill = PatternFill(start_color='ffff00', end_color='ffff00', fill_type = 'solid')

	cell = sheet.cell(row=row+1,column=col)
	cell.value = 'Purpose'
	cell.font = cell.font.copy(bold=True)
	cell.alignment = cell.alignment.copy(horizontal="center", vertical="center")
	cell.fill = PatternFill(start_color='ffff00', end_color='ffff00', fill_type = 'solid')

	cell = sheet.cell(row=row+1,column=col+1)
	cell.value = data.get("purpose")
	cell.font = cell.font.copy(bold=True)
	cell.alignment = cell.alignment.copy(horizontal="center", vertical="center")
	cell.fill = PatternFill(start_color='ffff00', end_color='ffff00', fill_type = 'solid')

	cell = sheet.cell(row=row+2,column=col)
	cell.value = 'Production Plan'
	cell.font = cell.font.copy(bold=True)
	cell.alignment = cell.alignment.copy(horizontal="center", vertical="center")
	cell.fill = PatternFill(start_color='ffff00', end_color='ffff00', fill_type = 'solid')

	cell = sheet.cell(row=row+2,column=col+1)
	cell.value = data.get("production_plan")
	cell.font = cell.font.copy(bold=True)
	cell.alignment = cell.alignment.copy(horizontal="center", vertical="center")
	cell.fill = PatternFill(start_color='ffff00', end_color='ffff00', fill_type = 'solid')

	cell = sheet.cell(row=row+4,column=col)
	cell.value = 'Pick List Work Order Table'
	cell.font = cell.font.copy(bold=True)
	cell.alignment = cell.alignment.copy(horizontal="center", vertical="center")
	cell.fill = PatternFill(start_color='ffff00', end_color='ffff00', fill_type = 'solid')

	for item in header:
		cell = sheet.cell(row=row+5,column=col)
		cell.value = item
		cell.font = cell.font.copy(bold=True)
		cell.alignment = cell.alignment.copy(horizontal="center", vertical="center")
		cell.fill = PatternFill(start_color='1E90FF', end_color='1E90FF', fill_type = 'solid')

		col+=1
	row = 7
	col = 1
	# last_row = row
	for item in data.get("work_orders"):
		cell = sheet.cell(row=row,column=col)
		cell.value = item.get('idx')
		cell.font = cell.font.copy(bold=False)
		cell.alignment = cell.alignment.copy(horizontal="center", vertical="center")

		cell = sheet.cell(row=row,column=col+1)
		cell.value = item.get('work_order')
		cell.font = cell.font.copy(bold=False)
		cell.alignment = cell.alignment.copy(horizontal="center", vertical="center")

		cell = sheet.cell(row=row,column=col+2)
		cell.value = item.get('qty_of_finished_goods')
		cell.font = cell.font.copy(bold=False)
		cell.alignment = cell.alignment.copy(horizontal="center", vertical="center")
		
		row+=1

	cell = sheet.cell(row=row+1,column=col)
	cell.value = 'Work Order Pick List Item'
	cell.font = cell.font.copy(bold=True)
	cell.alignment = cell.alignment.copy(horizontal="center", vertical="center")
	cell.fill = PatternFill(start_color='ffff00', end_color='ffff00', fill_type = 'solid')


	for item in header_2:
		cell = sheet.cell(row=row+2,column=col)
		cell.value = item
		cell.font = cell.font.copy(bold=True)
		cell.alignment = cell.alignment.copy(horizontal="center", vertical="center")
		cell.fill = PatternFill(start_color='1E90FF', end_color='1E90FF', fill_type = 'solid')

		col+=1
	row = row+3
	col = 1
	for item in data.get('work_order_pick_list_item'):
		cell = sheet.cell(row=row,column=col)
		cell.value = item.get('idx')
		cell.font = cell.font.copy(bold=False)
		cell.alignment = cell.alignment.copy(horizontal="center", vertical="center")

		cell = sheet.cell(row=row,column=col+1)
		cell.value = item.get('item_code')
		cell.font = cell.font.copy(bold=False)
		cell.alignment = cell.alignment.copy(horizontal="center", vertical="center")

		cell = sheet.cell(row=row,column=col+2)
		cell.value = item.get('warehouse')
		cell.font = cell.font.copy(bold=False)
		cell.alignment = cell.alignment.copy(horizontal="center", vertical="center")

		cell = sheet.cell(row=row,column=col+3)
		cell.value = item.get('work_order')
		cell.font = cell.font.copy(bold=False)
		cell.alignment = cell.alignment.copy(horizontal="center", vertical="center")

		cell = sheet.cell(row=row,column=col+4)
		cell.value = item.get('required_qty')
		cell.font = cell.font.copy(bold=False)
		cell.alignment = cell.alignment.copy(horizontal="center", vertical="center")

		cell = sheet.cell(row=row,column=col+5)
		cell.value = item.get('stock_qty')
		cell.font = cell.font.copy(bold=False)
		cell.alignment = cell.alignment.copy(horizontal="center", vertical="center")

		cell = sheet.cell(row=row,column=col+6)
		cell.value = item.get('picked_qty')
		cell.font = cell.font.copy(bold=False)
		cell.alignment = cell.alignment.copy(horizontal="center", vertical="center")


		cell = sheet.cell(row=row,column=col+7)
		cell.value = item.get('item_name')
		cell.font = cell.font.copy(bold=False)
		cell.alignment = cell.alignment.copy(horizontal="center", vertical="center")


		cell = sheet.cell(row=row,column=col+8)
		cell.value = item.get('description')
		cell.font = cell.font.copy(bold=False)
		cell.alignment = cell.alignment.copy(horizontal="center", vertical="center")

		cell = sheet.cell(row=row,column=col+9)
		cell.value = item.get('item_group')
		cell.font = cell.font.copy(bold=False)
		cell.alignment = cell.alignment.copy(horizontal="center", vertical="center")

		cell = sheet.cell(row=row,column=col+10)
		cell.value = item.get('engineering_revision')
		cell.font = cell.font.copy(bold=False)
		cell.alignment = cell.alignment.copy(horizontal="center", vertical="center")

		cell = sheet.cell(row=row,column=col+11)
		cell.value = item.get('uom')
		cell.font = cell.font.copy(bold=False)
		cell.alignment = cell.alignment.copy(horizontal="center", vertical="center")

		cell = sheet.cell(row=row,column=col+12)
		cell.value = item.get('stock_uom')
		cell.font = cell.font.copy(bold=False)
		cell.alignment = cell.alignment.copy(horizontal="center", vertical="center")

		cell = sheet.cell(row=row,column=col+13)
		cell.value = item.get('conversion_factor')
		cell.font = cell.font.copy(bold=False)
		cell.alignment = cell.alignment.copy(horizontal="center", vertical="center")

		row+=1



	file_path = frappe.utils.get_site_path("public")
	now = datetime.now()
	fname = "WORK_ORDER_PICK_LIST" + nowdate() + ".xlsx"
	book.save(file_path+fname)


@frappe.whitelist()
def download_xlsx():
	import openpyxl
	from io import BytesIO
	file_path = frappe.utils.get_site_path("public")
	now = datetime.now()
	fname = "WORK_ORDER_PICK_LIST" + nowdate() + ".xlsx"
	wb = openpyxl.load_workbook(filename=file_path+fname)
	xlsx_file = BytesIO()
	wb.save(xlsx_file)
	frappe.local.response.filecontent=xlsx_file.getvalue()

	frappe.local.response.type = "download"
	
	frappe.local.response.filename = fname


@frappe.whitelist()
def get_batch_no(item_code, warehouse, qty=1, throw=False):
	"""
	Get batch number using First Expiring First Out method.
	:param item_code: `item_code` of Item Document
	:param warehouse: name of Warehouse to check
	:param qty: quantity of Items
	:return: String represent batch number of batch with sufficient quantity else an empty String
	"""

	batch_no = None
	batches = get_batches(item_code, warehouse, qty, throw)
	for batch in batches:
		if cint(qty) <= cint(batch.qty):
			batch_no = batch.name
			break

	# if not batch_no:
	# 	frappe.msgprint(_('Please select a Batch for Item {0}. Unable to find a single batch that fulfills this requirement').format(frappe.bold(item_code)))
	# 	if throw:
	# 		raise UnableToSelectBatchError

	return batch_no


def get_batches(item_code, warehouse, qty=1, throw=False):
	# from erpnext.stock.doctype.serial_no.serial_no import get_serial_nos
	cond = ''
	if frappe.get_cached_value('Item', item_code, 'has_batch_no'):
		# serial_nos = get_serial_nos(serial_no)
		batch = frappe.get_all("Serial No",
			fields = ["distinct batch_no"],
			filters= {
				"item_code": item_code,
				"warehouse": warehouse
			}
		)
		# if not batch:
		# 	validate_serial_no_with_batch(serial_nos, item_code)

		if batch and len(batch) > 1:
			return []

		cond = " and b.name = %s" %(frappe.db.escape(batch[0].batch_no))

	return frappe.db.sql("""
		select b.name, sum(`tabStock Ledger Entry`.actual_qty) as qty
		from `tabBatch` b
			join `tabStock Ledger Entry` ignore index (item_code, warehouse)
				on (b.name = `tabStock Ledger Entry`.batch_no )
		where `tabStock Ledger Entry`.item_code = %s and `tabStock Ledger Entry`.warehouse = %s
			and (b.expiry_date >= CURDATE() or b.expiry_date IS NULL) {0}
		group by batch_id
		order by b.expiry_date ASC, b.creation ASC
	""".format(cond), (item_code, warehouse), as_dict=True)

def validate_serial_no_with_batch(serial_nos, item_code):
	if frappe.get_cached_value("Serial No", serial_nos[0], "item_code") != item_code:
		frappe.throw(_("The serial no {0} does not belong to item {1}")
			.format(get_link_to_form("Serial No", serial_nos[0]), get_link_to_form("Item", item_code)))

	serial_no_link = ','.join(get_link_to_form("Serial No", sn) for sn in serial_nos)

	message = "Serial Nos" if len(serial_nos) > 1 else "Serial No"
	frappe.throw(_("There is no batch found against the {0}: {1}")
		.format(message, serial_no_link))