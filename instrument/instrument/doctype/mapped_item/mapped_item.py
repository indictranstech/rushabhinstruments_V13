# Copyright (c) 2021, instrument and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class MappedItem(Document):
	pass


@frappe.whitelist()
def get_attribute_value(attribute):
	attribute_value = frappe.db.sql("""SELECT attribute_value from `tabItem Attribute Value` where parent = '{0}'""".format(attribute),as_dict=1,debug=1)
	return attribute_value