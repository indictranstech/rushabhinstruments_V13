# Copyright (c) 2024, instrument and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	columns = get_column()
	data = get_data(filters)
	return columns, data

def get_column():
	column = [{
			"label": "Mapped BOM",
			"fieldtype": "Link",
			"fieldname": "name",
			"options":"Mapped BOM",
			"width": 450
		},
		{
			"label": "Mapped Item",
			"fieldtype": "Link",
			"fieldname": "mapped_item",
			"options":"Item",
			"width": 400
		},
		{
			"label": "Mapped Item Name",
			"fieldtype": "Data",
			"fieldname": "mapped_item_name",
			"width": 400
		},
		{
			"label": "Item Mapping",
			"fieldtype": "Link",
			"fieldname": "Item_Mapping",
			"options":"Item Mapping",
			"width": 400
		},
		{
			"label": "Old Reference BOM",
			"fieldtype": "Link",
			"fieldname": "old_reference_bom",
			"options":"Mapped BOM",
			"width": 400
		}]
	return column

def get_data(filters):
	cond = ""
	if filters.get('mapped_bom'):
		cond += " AND tmb.name = '{0}'".format(filters.get('mapped_bom'))

	if filters.get('mapped_item'):
		cond += " AND tim.mapped_item = '{0}'".format(filters.get('mapped_item'))

	pending_data = []
	query = """
			SELECT 
				tmb.name,
				tim.mapped_item as mapped_item,
				tmb.item_name as mapped_item_name,
				tim.name as Item_Mapping,
				tmb.old_reference_bom
			FROM `tabMapped BOM` tmb 
			left join `tabItem Mapping` tim  on tmb.item = tim.mapped_item
			where 1 = 1 {0}
			""".format(cond)
	data = frappe.db.sql(query, as_dict=True)

	for i in data:
		query_1 = """
				SELECT 
					tbct.name,
					tbct.mapped_bom,
					tbct.mapped_item,
					tbct.item_mapping
				FROM `tabBOM Creation Tool` tbct
				WHERE tbct.mapped_bom = '{0}' and tbct.mapped_item = '{1}' and tbct.item_mapping = '{2}'
				""".format(i.get("name"), i.get("mapped_item"), i.get("Item_Mapping"))
		data_1 = frappe.db.sql(query_1, as_dict=True)
		if len(data_1) == 0:
			pending_data.append(i)

	return pending_data

