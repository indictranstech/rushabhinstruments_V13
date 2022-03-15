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
				doc.append('warehouses',{
					'warehouse':row.default_warehouse
					})
				# frappe.throw("Please Add Default Warehouse {0} in Item Locations".format(row.default_warehouse))

def disable_old_boms(doc,method):
	if doc.auto_disable_old_active_boms:
		old_boms = frappe.db.sql("""SELECT name from `tabBOM` WHERE item='{0}' name<(SELECT name FROM `tabBOM` WHERE item='{0}' AND is_default=1) """.format(doc.name), as_dict=1)
		for bom in old_boms:
			bom_doc = frappe.get_doc('BOM', bom)
			if bom_doc.is_active:
				any_wos = frappe.db.sql("""SELECT name FROM `tabWork Order` WHERE bom_no='{0}' AND status IN ('Submitted','Not Started', 'In Process','Draft')""".format(bom['name']))
				any_mboms = frappe.db.sql("""SELECT name FROM `tabMapped BOM Item` WHERE bom_no='{0}'""".format(bom['name']))
				if not any_wos and not any_mboms:
					bom_doc.is_active = 0
				if any_wos:
					bom_doc.to_be_disabled = 1
				bom_doc.save()
				bom_doc.submit()
