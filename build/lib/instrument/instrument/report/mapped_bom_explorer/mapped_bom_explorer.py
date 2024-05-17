# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import frappe


def execute(filters=None):
	data = []
	columns = get_columns()
	get_data(filters, data)
	return columns, data

def get_data(filters, data):
	get_exploded_items(filters.mapped_bom, data)

def get_exploded_items(bom, data, indent=0, qty=1):
	exploded_items = frappe.get_all("Mapped BOM Item",
		filters={"parent": bom},
		fields= ['is_map_item','qty','bom_no','mapped_bom','qty','scrap','item_code','item_name','description','uom'])
	for item in exploded_items:
		print(item.mapped_bom, indent)
		item["indent"] = indent
		if item.is_map_item:	
			data.append({
				'item_code': item.item_code,
				'item_name': item.item_name,
				'indent': indent,
				'bom_level': (frappe.get_cached_value("Mapped BOM", item.mapped_bom, "bom_level")
					if item.mapped_bom else ""),
				'bom': item.bom_no,
				'mapped_bom':item.mapped_bom,
				'qty': item.qty * qty,
				'uom': item.uom,
				'description': item.description,
				'scrap': item.scrap
			})
		else:
			data.append({
				'item_code': item.item_code,
				'item_name': item.item_name,
				'indent': indent,
				'bom_level': (frappe.get_cached_value("BOM", item.bom_no, "bom_level")
					if item.bom_no else ""),
				'bom': item.bom_no,
				'mapped_bom':item.mapped_bom,
				'qty': item.qty * qty,
				'uom': item.uom,
				'description': item.description,
				'scrap': item.scrap
			})
		if item.bom_no:
			get_exploded_items_for_std_bom(item.bom_no, data, indent=indent+1, qty=item.qty)
		if item.mapped_bom:
			get_exploded_items(item.mapped_bom, data, indent=indent+1, qty=item.qty)

def get_exploded_items_for_std_bom(bom,data,indent=0,qty=1):
	exploded_items = frappe.get_all("BOM Item",
		filters={"parent": bom},
		fields= ['qty','bom_no','qty','scrap','item_code','item_name','description','uom'])
	for item in exploded_items:
		print(item.bom_no, indent)
		item["indent"] = indent
		data.append({
			'item_code': item.item_code,
			'item_name': item.item_name,
			'indent': indent,
			'bom_level': (frappe.get_cached_value("BOM", item.bom_no, "bom_level")
				if item.bom_no else ""),
			'bom': item.bom_no,
			'qty': item.qty * qty,
			'uom': item.uom,
			'description': item.description,
			'scrap': item.scrap
		})
		if item.bom_no:
			get_exploded_items_for_std_bom(item.bom_no, data, indent=indent+1, qty=item.qty)

def get_columns():
	return [
		{
			"label": "Item Code",
			"fieldtype": "Link",
			"fieldname": "item_code",
			"width": 300,
			"options": "Item"
		},
		{
			"label": "Item Name",
			"fieldtype": "data",
			"fieldname": "item_name",
			"width": 100
		},
		{
			"label": "BOM",
			"fieldtype": "Link",
			"fieldname": "bom",
			"width": 150,
			"options": "BOM"
		},
		{
			"label": "Mapped BOM",
			"fieldtype": "Link",
			"fieldname": "mapped_bom",
			"width": 150,
			"options": "Mapped BOM"
		},
		{
			"label": "Qty",
			"fieldtype": "data",
			"fieldname": "qty",
			"width": 100
		},
		{
			"label": "UOM",
			"fieldtype": "data",
			"fieldname": "uom",
			"width": 100
		},
		{
			"label": "BOM Level",
			"fieldtype": "Data",
			"fieldname": "bom_level",
			"width": 100
		},
		{
			"label": "Standard Description",
			"fieldtype": "data",
			"fieldname": "description",
			"width": 150
		},
		{
			"label": "Scrap",
			"fieldtype": "data",
			"fieldname": "scrap",
			"width": 100
		},
	]
