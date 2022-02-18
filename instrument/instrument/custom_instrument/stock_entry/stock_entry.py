from __future__ import unicode_literals
import frappe


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
		item_data = frappe.db.sql(""" SELECT warehouse FROM `tabItem Locations` where parent = '{0}' """.format(item))
		item_list = [item.warehouse for item in item_data]
		return item_list