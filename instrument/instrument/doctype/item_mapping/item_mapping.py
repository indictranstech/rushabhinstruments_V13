# Copyright (c) 2021, instrument and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname

class ItemMapping(Document):
	def autoname(self):
		attribute_values = []
		for row in self.attribute_table:
			attribute_values.append(row.value)
		value = "_".join(attribute_values)
		self.name = self.mapped_item+"_"+value


	def validate(self):
		if self.attribute_table:
			attribute_list = [item.attribute for item in self.attribute_table]
			attribute_set = set(attribute_list)
			if len(attribute_set) != len(attribute_list):
				frappe.throw("Duplicate Attribute Not Allowed")


@frappe.whitelist()
def get_attribute_value(attribute):
	attribute_value = frappe.db.sql("""SELECT attribute_value from `tabItem Attribute Value` where parent = '{0}'""".format(attribute),as_dict=1,debug=1)
	return attribute_value

@frappe.whitelist()
def get_attributes(mapped_item):
	attribute_list = frappe.db.sql("""SELECT attribute from `tabItem Attribute Table` where parent = '{0}'""".format(mapped_item),as_dict=1)
	if attribute_list != []:
		return attribute_list