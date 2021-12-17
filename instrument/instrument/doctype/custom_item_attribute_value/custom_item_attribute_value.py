# Copyright (c) 2021, instrument and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class CustomItemAttributeValue(Document):
	def validate(self):
		if self.get("__islocal"):
			attribute_list_data = frappe.db.sql("""SELECT attribute_value from `tabItem Attribute Value` where parent = '{0}'""".format(self.item_attribute),as_dict =1)
			attribute_list = [item.attribute_value for item in attribute_list_data]
			doc_string = str(self.name)
			if self.name not in attribute_list:
				item_attribute_doc = frappe.get_doc("Item Attribute",self.item_attribute)
				item_attribute_doc.append('item_attribute_values',{
					'attribute_value' : self.name,
					'abbr' : doc_string[0:3]
					})
				item_attribute_doc.flags.ignore_validate = True
				item_attribute_doc.save()
