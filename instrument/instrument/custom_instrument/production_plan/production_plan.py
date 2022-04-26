from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import cstr, cint, flt, comma_or, getdate, nowdate, formatdate, format_time
import json
from erpnext.manufacturing.doctype.bom.bom import get_children, validate_bom_no

# @frappe.whitelist()
# def on_update(doc,method):
# 	ohs = get_current_stock()
# 	if doc.sub_assembly_items:
# 		for row in doc.sub_assembly_items:
# 			if row.production_item in ohs:
# 				qty = row.qty
# 				frappe.db.set_value("Production Plan Sub Assembly Item",{'name':row.name},'original_required_qty',qty)
# 				frappe.db.commit()
# 				frappe.db.set_value("Production Plan Sub Assembly Item",{'name':row.name},'available_quantity',ohs.get(row.production_item))
# 				frappe.db.commit()
# 				calculated_required_quantity = (flt(qty) - flt(ohs.get(row.production_item)) if flt(ohs.get(row.production_item)) < flt(qty) else 0)
# 				frappe.db.set_value("Production Plan Sub Assembly Item",{'name':row.name},'qty',calculated_required_quantity)
# 				frappe.db.commit()
# 	doc.reload()
# 				# if flt(row.original_required_qty) <= 0:
				# 	# row.original_required_qty = row.qty 
				# 	frappe.db.set_value("Production Plan Sub Assembly Item",{'name':row.name},'original_required_qty',row.qty)
				# else:
				# 	pass 
				# frappe.db.set_value("Production Plan Sub Assembly Item",{'name':row.name},'available_quantity',ohs.get(row.production_item))
				# # row.available_quantity = ohs.get(row.production_item)
				# calculated_required_quantity = abs(flt(row.original_required_qty) - flt(ohs.get(row.production_item))) if ohs.get(row.production_item) <= 0 else 0
				# frappe.db.set_value("Production Plan Sub Assembly Item",{'name':row.name},'calculated_required_quantity',calculated_required_quantity)
				# # row.calculated_required_quantity = abs(row.original_required_qty - ohs.get(row.production_item)) if ohs.get(row.production_item) <= 0 else 0
				# frappe.db.set_value("Production Plan Sub Assembly Item",{'name':row.name},'qty',calculated_required_quantity)
				# frappe.db.commit()
				# # row.qty = row.calculated_required_quantity

@frappe.whitelist()
def validate(doc,method):
	ohs = get_current_stock()
	if doc.po_items:
		for row in doc.po_items:
			if row.item_code in ohs:
				row.available_quantity = ohs.get(row.item_code)
				# frappe.db.set_value("Work Order",doc.name,'available_quantity',ohs.get(row.item_code))
				# frappe.db.commit()
				# doc.reload()
	# if doc.sub_assembly_items:
	# 	doc.sub_assembly_items.sort(key= lambda d: d.bom_level, reverse=True)
	# 	for idx, row in enumerate(doc.sub_assembly_items, start=1):
	# 		row.idx = idx
	if not doc.get("__islocal"):
		frappe.db.sql("""DELETE from `tabFile` where attached_to_doctype='Production Plan' and attached_to_name=%s""",
			(doc.name))
		pdf_data=frappe.attach_print('Production Plan',doc.name, print_format='Production Plan')
		
		_file = frappe.get_doc({
		"doctype": "File",
		"file_name": pdf_data.get('fname'),
		"attached_to_doctype": "Production Plan",
		"attached_to_name": doc.name,
		"is_private": 1,
		"content": pdf_data.get('fcontent')
		})
		_file.save()
def get_current_stock():
	# 1.get wip warehouse
	wip_warehouse = frappe.db.get_single_value("Manufacturing Settings", 'default_wip_warehouse')
	current_stock = frappe.db.sql("""SELECT item_code,sum(projected_qty) as qty from `tabBin` where warehouse != '{0}' group by item_code """.format(wip_warehouse),as_dict=1)
	ohs_dict = {item.item_code : item.qty for item in current_stock}
	return ohs_dict

@frappe.whitelist()
def make_work_order(doc):
	from erpnext.manufacturing.doctype.work_order.work_order import get_default_warehouse
	doc = json.loads(doc)
	production_plan_doc = frappe.get_doc("Production Plan",doc.get("name"))
	wo_list, po_list = [], []
	subcontracted_po = {}
	default_warehouses = get_default_warehouse()
	validate_data(production_plan_doc)
	make_work_order_for_finished_goods(production_plan_doc,wo_list)
	production_plan_doc.make_work_order_for_subassembly_items(wo_list, subcontracted_po,default_warehouses)
	production_plan_doc.make_subcontracted_purchase_order(subcontracted_po, po_list)
	production_plan_doc.show_list_created_message('Work Order', wo_list)
	production_plan_doc.show_list_created_message('Purchase Order', po_list)

def validate_data(production_plan_doc):
	for d in production_plan_doc.get('po_items'):
		if not d.bom_no:
			frappe.throw(_("Please select BOM for Item in Row {0}").format(d.idx))
		else:
			validate_bom_no(d.item_code, d.bom_no)

		if not flt(d.planned_qty):
			frappe.throw(_("Please enter Planned Qty for Item {0} at row {1}").format(d.item_code, d.idx))

def make_work_order_for_finished_goods(production_plan_doc, wo_list):
		items_data = get_production_items(production_plan_doc)
		for key, item in items_data.items():
			if production_plan_doc.sub_assembly_items:
				item['use_multi_level_bom'] = 0

			work_order =create_work_order(production_plan_doc,item)
			if work_order:
				wo_list.append(work_order)
def get_production_items(production_plan_doc):
		item_dict = {}
		for d in production_plan_doc.po_items:
			item_details = {
				"production_item"		: d.item_code,
				"use_multi_level_bom"   : d.include_exploded_items,
				"sales_order"			: d.sales_order,
				"sales_order_item"		: d.sales_order_item,
				"material_request"		: d.material_request,
				"material_request_item"	: d.material_request_item,
				"bom_no"				: d.bom_no,
				"description"			: d.description,
				"stock_uom"				: d.stock_uom,
				"company"				: production_plan_doc.company,
				"fg_warehouse"			: d.warehouse,
				"production_plan"       : production_plan_doc.name,
				"production_plan_item"  : d.name,
				"product_bundle_item"	: d.product_bundle_item,
				"planned_start_date"    : d.planned_start_date
			}

			item_details.update({
				"project": production_plan_doc.project or frappe.db.get_value("Sales Order", d.sales_order, "project")
			})

			if production_plan_doc.get_items_from == "Material Request":
				item_details.update({
					"qty": d.planned_qty
				})
				item_dict[(d.item_code, d.material_request_item, d.warehouse,d.name)] = item_details
			else:
				item_details.update({
					"qty": flt(item_dict.get((d.item_code, d.sales_order, d.warehouse,d.name),{})
						.get("qty")) + (flt(d.planned_qty) - flt(d.ordered_qty))
				})
				item_dict[(d.item_code, d.sales_order, d.warehouse,d.name)] = item_details

		return item_dict
def create_work_order(self, item):
		from erpnext.manufacturing.doctype.work_order.work_order import (
			OverProductionError,
			get_default_warehouse,
		)
		warehouse = get_default_warehouse()
		wo = frappe.new_doc("Work Order")
		wo.update(item)
		schedule_date = frappe.db.get_value("Sales Order Item",{'parent':item.get("sales_order"),'item_code':item.get("production_item"),'qty':item.get('qty')},'delivery_date')

		wo.planned_start_date =  item.get('planned_start_date') or item.get('schedule_date')
		wo.expected_delivery_date = schedule_date or ''

		if item.get("warehouse"):
			wo.fg_warehouse = item.get("warehouse")

		wo.set_work_order_operations()

		if not wo.fg_warehouse:
			wo.fg_warehouse = warehouse.get('fg_warehouse')
		try:
			wo.flags.ignore_mandatory = True
			wo.insert()
			return wo.name
		except OverProductionError:
			pass
@frappe.whitelist()
def get_sub_assembly_items(doc, manufacturing_type=None):
	doc = json.loads(doc)
	final_data = []
	final_datas = []
	ohs = get_current_stock()
	# print("============ohs",ohs)
	for row in doc.get("po_items"):
		bom_data = []
		get_sub_assembly_item(row.get("bom_no"), bom_data, row.get("planned_qty"))
		# print("===========bom_data",bom_data)
		for data in bom_data:
			qty = data.stock_qty
			data.original_required_qty = data.stock_qty
			data.available_quantity = ohs.get(data.production_item)
			calculated_required_quantity = (flt(qty) - flt(ohs.get(data.production_item)) if flt(ohs.get(data.production_item)) < flt(qty) else 0)
			data.qty = calculated_required_quantity
			remaining_qty = flt(ohs.get(data.production_item))-flt(qty) if flt(ohs.get(data.production_item)) > flt(qty) else 0
			ohs.update({data.production_item:remaining_qty})
			data.production_plan_item = row.get("name")
			data.fg_warehouse = row.get("warehouse")
			data.schedule_date = row.get("planned_start_date")
			data.type_of_manufacturing = manufacturing_type or ("Subcontract" if data.is_sub_contracted_item
				else "In House")
		# data=set_sub_assembly_items_based_on_level(row, bom_data, final_data,manufacturing_type)
		final_datas.append(bom_data)
	return final_datas

	
@frappe.whitelist()
def get_sub_assembly_item(bom_no, bom_data, to_produce_qty, indent=0):
	data = get_children('BOM', parent = bom_no)
	for d in data:
		if d.expandable:
			parent_item_code = frappe.get_cached_value("BOM", bom_no, "item")
			stock_qty = (d.stock_qty / d.parent_bom_qty) * flt(to_produce_qty)
			bom_data.append(frappe._dict({
				'parent_item_code': parent_item_code,
				'description': d.description,
				'production_item': d.item_code,
				'item_name': d.item_name,
				'stock_uom': d.stock_uom,
				'uom': d.stock_uom,
				'bom_no': d.value,
				'is_sub_contracted_item': d.is_sub_contracted_item,
				'bom_level': indent,
				'indent': indent,
				'stock_qty': stock_qty
			}))

			if d.value:
				get_sub_assembly_item(d.value, bom_data, stock_qty, indent=indent+1)

def set_sub_assembly_items_based_on_level(row, bom_data, final_data,manufacturing_type=None):
	ohs = get_current_stock()
	for data in bom_data:
		qty = data.stock_qty
		data.original_required_qty = data.stock_qty
		data.available_quantity = ohs.get(data.production_item)
		calculated_required_quantity = (flt(qty) - flt(ohs.get(data.production_item)) if flt(ohs.get(data.production_item)) < flt(qty) else 0)
		data.qty = calculated_required_quantity
		data.production_plan_item = row.get("name")
		data.fg_warehouse = row.get("warehouse")
		data.schedule_date = row.get("planned_start_date")
		data.type_of_manufacturing = manufacturing_type or ("Subcontract" if data.is_sub_contracted_item
			else "In House")
	return bom_data
		