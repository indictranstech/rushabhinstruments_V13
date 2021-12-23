from __future__ import unicode_literals
import frappe
from frappe.model.document import Document


def validate(doc,method):
	if doc.item_attribute_table:
		attribute_list = [item.attribute for item in doc.item_attribute_table]
		attribute_set = set(attribute_list)
		if len(attribute_set) != len(attribute_list):
			frappe.throw("Duplicate Attribute Not Allowed")

	warehouse_list  = []
	if doc.warehouses:
		for row in doc.warehouses:
			warehouse_list.append(row.warehouse)

	if doc.item_defaults:
		for row in doc.item_defaults:
			if row.default_warehouse not in warehouse_list:
				frappe.throw("Please Add Default Warehouse {0} in Item Locations".format(row.default_warehouse))
			
