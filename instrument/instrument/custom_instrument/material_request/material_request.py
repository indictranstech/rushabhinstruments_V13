from __future__ import unicode_literals
import frappe
import json

def validate(doc,method):
	if doc.get("__islocal"):
		if doc.items:
			for item in doc.items:
				engineering_revision = frappe.db.get_value("Item",{'item_code':item.item_code},'engineering_revision') or frappe.db.get_value("Engineering Revision",{'item_code':item.item_code,'is_default':1,'is_active':1},'name')
				item.engineering_revision = engineering_revision
