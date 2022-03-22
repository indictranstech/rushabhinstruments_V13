from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import cstr, cint, flt, comma_or, getdate, nowdate, formatdate, format_time
import json
from erpnext.manufacturing.doctype.bom.bom import get_children, validate_bom_no

@frappe.whitelist()
def on_update(doc,method):
	ohs = get_current_stock()
	if doc.sub_assembly_items:
		for row in doc.sub_assembly_items:
			if row.production_item in ohs:
				qty = row.qty
				frappe.db.set_value("Production Plan Sub Assembly Item",{'name':row.name},'original_required_qty',qty)
				frappe.db.commit()
				frappe.db.set_value("Production Plan Sub Assembly Item",{'name':row.name},'available_quantity',ohs.get(row.production_item))
				frappe.db.commit()
				calculated_required_quantity = (flt(qty) - flt(ohs.get(row.production_item)) if flt(ohs.get(row.production_item)) < flt(qty) else 0)
				frappe.db.set_value("Production Plan Sub Assembly Item",{'name':row.name},'qty',calculated_required_quantity)
				frappe.db.commit()
	doc.reload()
				# if flt(row.original_required_qty) <= 0:
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