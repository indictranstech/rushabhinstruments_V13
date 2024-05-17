from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

def after_insert(doc,method):
	create_custom_attribute_value(doc)

def validate(doc,method):
	if not doc.get('__islocal'):
		create_custom_attribute_value(doc)
		
def create_custom_attribute_value(doc):
	if doc.item_attribute_values:
		frappe.db.sql("""delete from `tabCustom Item Attribute Value` where item_attribute = %s""",(doc.name))
		for item in doc.item_attribute_values:
			if_exists = frappe.db.get_value("Custom Item Attribute Value",{'value':item.attribute_value,'item_attribute':doc.name},'name')
			if not if_exists:
				item_attribute_value_doc = frappe.new_doc("Custom Item Attribute Value")
				if item_attribute_value_doc:
					item_attribute_value_doc.item_attribute = doc.name
					item_attribute_value_doc.value = item.attribute_value
					item_attribute_value_doc.save(ignore_permissions=1)