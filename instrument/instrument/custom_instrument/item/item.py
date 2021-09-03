from __future__ import unicode_literals
import frappe
from frappe.model.document import Document


def validate(doc,method):
	pass
	# warehouse_list  = []
	# if doc.warehouses:
	# 	for row in doc.warehouses:
	# 		warehouse_list.append(row.warehouse)

	# if doc.item_defaults:
	# 	for row in doc.item_defaults:
	# 		if row.default_warehouse not in warehouse_list:
	# 			frappe.throw("Please Add Default Warehouse {0} in Item Locations".format(row.default_warehouse))
			
