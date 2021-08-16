# Copyright (c) 2013, instrument and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt
from frappe import msgprint, _

def execute(filters=None):
	return _execute(filters)
	# columns, data = [], []
	# return columns, data

def _execute(filters, additional_table_columns=None, additional_query_columns=None):
	if not filters: filters = frappe._dict({})

	wo_list = get_work_orders(filters, additional_query_columns)
	columns = get_columns(wo_list, additional_table_columns)
	if not wo_list:
		msgprint(_("No record found"))
		return columns, wo_list
	data = []
	for row in wo_list:
		doc = frappe.get_doc("Work Order",row.name)
		row1 = [
			row.name,row.production_item,row.status,row.bom_level,row.qty,row.produced_qty,row.material_transferred_for_manufacturing
		]
		final_item_status = []
		final_item_percent = []
		ohs = get_current_stock()
		for item in doc.required_items:
			if item.item_code in ohs:
				if item.required_qty <= ohs.get(item.item_code):
					final_item_status.append('Full Qty Available')
					percent_stock = 100
					qty_will_be_produced = item.required_qty
					final_item_percent.append(qty_will_be_produced)
				# elif item.required_qty > ohs.get(item.item_code) and ohs.get(item.item_code) > 0:
				elif item.required_qty > ohs.get(item.item_code) and ohs.get(item.item_code) > 0: 
					final_item_status.append('Partial Qty Available')
					percent_stock = (ohs.get(item.item_code)/item.required_qty*100)
					qty_will_be_produced = (percent_stock/100*item.required_qty)
					final_item_percent.append(qty_will_be_produced)
				else : 
					final_item_status.append('Qty Not Available')
					percent_stock = (ohs.get(item.item_code)/item.required_qty*100)
					qty_will_be_produced = 0
					final_item_percent.append(qty_will_be_produced)
	
		row1.append(min(final_item_percent) if len(final_item_percent) > 1 else 0)
		row1.append(row.production_plan)
		status_list = ['Full Qty Available']
		status_list_pa = ['Partial Qty Available']
		status_list_na = ['Qty Not Available']
		check =  all(item in status_list for item in final_item_status)
		check_pa = all(item in status_list_pa for item in final_item_status)
		check_na = all(item in status_list_na for item in final_item_status)
		if check == True:
			row1.append('Full Qty Available')
		elif check_pa == True:
			row1.append('Partial Qty Available')
		elif check_na == True : 
			row1.append('Qty Not Available')
		elif 'Qty Not Available' in final_item_status and 'Partial Qty Available' in final_item_status:
			row1.append('Qty Available For Some Items')
		else :
			row1.append('Partial Qty Available')
		row1.append(row.planned_start_date)
		row1.append(row.planned_end_date)
		data.append(row1)

	return columns, data


def get_columns(wo_list, additional_table_columns):
	"""return columns based on filters"""
	columns = [
		_("Name") + ":Link/Work Order:120",_("Item to Manufacture") + ":Data:150", _("Status") + ":Data:120", _("BOM Level") + ":Data:120",_("Qty To Manufacture") + ":float:150",_("Manufactured Qty") + ":float:150",_("Material Transferred For Manufacturing") + ":float:200",_("Qty Will be Produced") + ":Float:180",_("Production Plan") + ":Link/Production Plan:150",_("Item Stock Status") + ":Data:150",_("Planned Start Date") + ":Date:150",_("Planned End Date") + ":Date:150"]
	columns = columns
	return columns

def get_conditions(filters):
	conditions = ""

	# if filters.get("planned_start_date"): conditions += " and planned_start_date >= %(planned_start_date)s"
	# if filters.get("planned_end_date"): conditions += " and planned_end_date <= %(planned_end_date)s"

	if filters.get("work_order"): conditions += " and name = %(work_order)s"
	if filters.get("production_plan"): conditions += " and production_plan = %(production_plan)s"

	return conditions

def get_work_orders(filters, additional_query_columns):
	if additional_query_columns:
		additional_query_columns = ', ' + ', '.join(additional_query_columns)

	conditions = get_conditions(filters)
	return frappe.db.sql("""
		SELECT name,production_item,qty,status,produced_qty,material_transferred_for_manufacturing,date(planned_start_date) as planned_start_date ,date(planned_end_date) as planned_end_date,item_stock_status,production_plan,bom_level
		from `tabWork Order`
		where status != 'Completed' %s order by planned_start_date desc, name desc"""%
		conditions, filters, as_dict=1,debug=1)


def get_current_stock():
	# 1.get wip warehouse
	wip_warehouse = frappe.db.get_single_value("Manufacturing Settings", 'default_wip_warehouse')
	current_stock = frappe.db.sql("""SELECT item_code,sum(actual_qty) as qty from `tabBin` where warehouse != '{0}' group by item_code """.format(wip_warehouse),as_dict=1)
	ohs_dict = {item.item_code : item.qty for item in current_stock}
	return ohs_dict