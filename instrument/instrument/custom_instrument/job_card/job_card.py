from __future__ import unicode_literals
import frappe
import json


@frappe.whitelist()
def get_engineering_revision(item_code,work_order):
	if item_code:
		engineering_revision = frappe.db.get_value("Item",{'name':item_code},'engineering_revision')
		er_from_wo = frappe.db.get_value("Work Order Item",{'parent':work_order,'item_code':item_code},'engineering_revision')
		if er_from_wo:
			return er_from_wo
		else:
			return engineering_revision
