# Copyright (c) 2022, instrument and contributors
# For license information, please see license.txt

import frappe
from frappe import msgprint, _

def execute(filters=None):
	return _execute(filters)
	# columns, data = [], []
	# return columns, data

def _execute(filters, additional_table_columns=None, additional_query_columns=None):
	if not filters: filters = frappe._dict({})
	work_order_pick_list = filters.get("work_order_pick_list")
	columns = get_columns(work_order_pick_list, additional_table_columns)
	if not work_order_pick_list:
		msgprint(_("No record found"))
		return columns, work_order_pick_list
	data = get_pick_list_data(filters, additional_query_columns)
	return columns, data


def get_columns(work_order_pick_list, additional_table_columns):
	"""return columns based on filters"""
	columns = [
		_("Item Code") + ":Link/Item:120",_("Item Name") + ":Data:150", _("Description") + ":Data:120", _("Item Group") + ":Data:120",_("Warehouse") + ":Link/Warehouse:150",_("Work Order") + ":Link/Work Order:150",_("UOM") + ":Link/UOM:200",_("UOM Conversion Factor") + ":Float:150",_("Required Qty") + ":Float:150",_("Stock Qty") + ":Float:150",_("Picked Qty") + ":Float:150",_("Stock UOM") + ":Link/UOM:150" , _("Batch No") + ":Link/Batch:150", _("Serial No") + ":Small Text:150"]
	columns = columns
	return columns

def get_conditions(filters):
	conditions = ""

	if filters.get("work_order_pick_list"): conditions += " and parent = %(work_order_pick_list)s"
	return conditions

def get_pick_list_data(filters, additional_query_columns):
	if additional_query_columns:
		additional_query_columns = ', ' + ', '.join(additional_query_columns)

	conditions = get_conditions(filters)
	return frappe.db.sql("""
		SELECT item_code,item_name,description,item_group,warehouse,work_order,uom,uom_conversion_factor,required_qty,stock_qty,picked_qty,stock_uom,batch_no,serial_no
		from `tabWork Order Pick List Item`
		where parent = '{0}'""".format(filters.get('work_order_pick_list')), as_dict=1,debug=1)

