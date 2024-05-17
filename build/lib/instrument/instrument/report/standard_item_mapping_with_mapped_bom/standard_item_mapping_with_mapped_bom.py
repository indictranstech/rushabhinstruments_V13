# Copyright (c) 2023, instrument and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	columns, data = [], []
	# return columns, data
	get_data(filters, data)
	return columns, data

def get_data(filters, data):
	if filters.get('mapped_bom'):
		data = frappe.db.sql("SELECT m.item_code ,i.name from `tabMapped BOM Item` m join `tabItem Mapping` i on i.item_code = m.item_code where m.name = '{0}' ".format(filters.get('mapped_bom')),as_dict=1,debug=1)


def get_columns():
	return [
		{
			"label": "Standard Item",
			"fieldtype": "Link",
			"fieldname": "item_code",
			"width": 300,
			"options": "Item"
		},
		{
			"label": "Item Mapping",
			"fieldtype": "Link",
			"fieldname": "item_mapping",
			"width": 100
		}
	]
