# Copyright (c) 2013, instrument and contributors
# For license information, please see license.txt

import frappe
def execute(filters=None):
	data = []
	columns = get_columns()
	get_data(filters, data)
	return columns, data

def get_data(filters, data):
	get_exploded_items(filters, data)

def get_exploded_items(filters, data, indent=0):
	conditions = get_conditions(filters)
	fg_item_groups = frappe.db.sql("""SELECT item_group from `tabTable For Item Group`""",as_dict=1)
	fg_item_groups = [item.get('item_group') for item in fg_item_groups]
	joined_fg_list = "', '".join(fg_item_groups)
	wo_list = frappe.db.sql("""SELECT distinct wo.name,wo.production_item,wo.item_name ,wo.status,wo.planned_start_date,wo.planned_end_date,wo.so_reference,wo.mr_reference,wo.bom_no,wo.bom_level from `tabWork Order` wo join `tabItem` i on i.item_code = wo.production_item where {0} and i.item_group in ('{1}') group by wo.name order by wo.name""".format(conditions,joined_fg_list),as_dict=1,debug=1)
	for item in wo_list:
		print(item.name, indent)
		item["indent"] = indent
		data.append({
			'name': item.name,
			'production_item':item.production_item,
			'item_name':item.item_name,
			'indent': indent,
			'status': item.status,
			'planned_start_date':item.planned_start_date,
			'planned_end_date':item.planned_end_date,
			'so_reference':item.so_reference,
			'mr_reference':item.mr_reference,
			'bom_no':item.bom_no,
			'bom_level':item.bom_level
		})
		get_exploded_wo(item.bom_no, data,item.so_reference,item.mr_reference, indent=indent+1)
		
def get_exploded_wo(bom_no,data,so_reference,mr_reference,indent=0):
	bom_items = frappe.get_all(
			"BOM Item",
			fields=["item_code", "bom_no"],
			filters=[["parent", "=", bom_no]],
			order_by="idx",
		)
	for row in bom_items:
		exploded_items = frappe.get_all("Work Order",
			filters={"bom_no": row.bom_no,"so_reference":so_reference},
			fields= ['name','production_item','item_name','status','planned_start_date','planned_end_date','so_reference','mr_reference','bom_level','bom_no'])
		for item in exploded_items:
			print(item.name, indent)
			item["indent"] = indent
			data.append({
				'name': item.name,
			'production_item':item.production_item,
			'item_name':item.item_name,
			'indent': indent,
			'status': item.status,
			'planned_start_date':item.planned_start_date,
			'planned_end_date':item.planned_end_date,
			'so_reference':item.so_reference,
			'mr_reference':item.mr_reference,
			'bom_no':item.bom_no,
			'bom_level':item.bom_level
			})
			get_exploded_wo(item.bom_no, data,item.so_reference,item.mr_reference, indent=indent+1)

def get_columns():
	return [
		{
			"label": "Work Order",
			"fieldtype": "Link",
			"fieldname": "name",
			"width": 250,
			"options": "Work Order"
		},
		{
			"label": "Production Item",
			"fieldtype": "Link",
			"fieldname": "production_item",
			"options" : "Item",
			"width": 300
		},
		{
			"label": "Item Name",
			"fieldtype": "Data",
			"fieldname": "item_name",
			"width": 150
		},
		{
			"label": "Status",
			"fieldtype": "Data",
			"fieldname": "status",
			"width": 150
		},
		{
			"label": "Planned Start Date",
			"fieldtype": "Date",
			"fieldname": "planned_start_date",
			"width": 150
		},
		{
			"label": "Planned End Date",
			"fieldtype": "Date",
			"fieldname": "planned_end_date",
			"width": 150
		},
		{
			"label": "SO Reference",
			"fieldtype": "data",
			"fieldname": "so_reference",
			"width": 150
		},
		{
			"label": "MR Reference",
			"fieldtype": "data",
			"fieldname": "mr_reference",
			"width": 150
		},
		{
			"label": "BOM No",
			"fieldtype": "data",
			"fieldname": "bom_no",
			"width": 150
		},
		{
			"label": "BOM Level",
			"fieldtype": "data",
			"fieldname": "bom_level",
			"width": 150
		}
	]
def get_conditions(filters=None):
	conditions = "1=1 "
	if filters.get("work_order") :
		conditions += "and wo.name = '{0}'".format(filters.get("work_order"))
	if filters.get("production_item") :
		conditions += "and wo.production_item = '{0}'".format(filters.get("production_item"))
	if filters.get("status") :
		conditions += " and wo.status = '{0}' ".format(filters.get("status"))
	return conditions
