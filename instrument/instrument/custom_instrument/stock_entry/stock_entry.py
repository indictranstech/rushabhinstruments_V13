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

