# Copyright (c) 2021, instrument and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname
import json
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
		if self.get("__islocal"):
			data_dict = dict()
			data_dict['item_code'] = self.item_code
			attribute_value_dict = {item.attribute:item.value for item in self.attribute_table}
			data_dict['attribute_value_data']=attribute_value_dict
			self.data_for_compare = frappe.as_json(data_dict)
			self.propogate_updates_to_affected_boms_status = ""
		else:
			if self.data_for_compare:
				data_dict = json.loads(self.data_for_compare)
				d1 = data_dict.get('attribute_value_data')
				d2 = {item.attribute:item.value for item in self.attribute_table}
				if self.item_code != data_dict.get('item_code') or not(all((d2.get(k) == v for k, v in d1.items()))) or not(all((d1.get(k) == v for k, v in d2.items()))):
					self.propogate_updates_to_affected_boms_status = "Need To Run"
				else:
					self.propogate_updates_to_affected_boms_status = "Propogation Not Needed"
			else:
				data_dict = dict()
				data_dict['item_code'] = self.item_code
				attribute_value_dict = {item.attribute:item.value for item in self.attribute_table}
				data_dict['attribute_value_data']=attribute_value_dict
				self.data_for_compare = frappe.as_json(data_dict)


@frappe.whitelist()
def propogate_updates_to_affected_boms(doc):
	doc = json.loads(doc)
	old_data = json.loads(doc.get('data_for_compare'))
	old_standrad_item_code = old_data.get('item_code')
	find_BCT_for_main = frappe.db.sql("""SELECT bct.name from `tabBOM Creation Tool` bct join `tabReview Item Mapping` rim on rim.parent = bct.name where  bct.standard_item_code = '{0}' order by bct.name desc""".format(old_standrad_item_code),as_dict=1)
	find_BCT_for_table = frappe.db.sql("""SELECT bct.name from `tabBOM Creation Tool` bct join `tabReview Item Mapping` rim on rim.parent = bct.name where  rim.standard_item_code = '{0}' order by bct.name desc""".format(old_standrad_item_code),as_dict=1)
	new_bct_doc_list = []
	if find_BCT_for_main != []:
		get_bct = frappe.get_doc("BOM Creation Tool",find_BCT_for_main[0].get('name'))
		if get_bct:
			if get_bct.docstatus == 1:
				new_doc = frappe.copy_doc(get_bct, ignore_no_copy=True)
				if new_doc.standard_item_code == old_standrad_item_code:
					new_doc.standard_item_code = doc.get('item_code')
				for item in new_doc.review_item_mapping:
					if item.standard_item_code == old_standrad_item_code:
						item.standard_item_code = doc.get('item_code')
						item.item_mapping_retrived = doc.get('name')
				new_doc.table_of_standard_boms_produced = []
				new_doc.difference_between_previous_and_current_review_item_mappings = []
				new_doc.save()
				new_bct_doc_list.append(new_doc.name)
			else:
				if get_bct.standard_item_code == old_standrad_item_code:
					get_bct.standard_item_code = doc.get('item_code')
				for item in get_bct.review_item_mapping:
					if item.standard_item_code == old_standrad_item_code:
						item.standard_item_code = doc.get('item_code')
						item.item_mapping_retrived = doc.get('name')
				get_bct.table_of_standard_boms_produced = []
				get_bct.difference_between_previous_and_current_review_item_mappings = []
				get_bct.save()
				new_bct_doc_list.append(get_bct.name)
				# mapped_bom = get_bct.mapped_bom
				# get_bct.mapped_bom = ''
				# get_bct.mapped_bom = mapped_bom
				# get_bct.save()
	elif find_BCT_for_table != []:
		get_bct = frappe.get_doc("BOM Creation Tool",find_BCT_for_table[0].get('name'))
		if get_bct:
			if get_bct.docstatus == 1:
				new_doc = frappe.copy_doc(get_bct, ignore_no_copy=True)
				if new_doc.standard_item_code == old_standrad_item_code:
					new_doc.standard_item_code = doc.get('item_code')
				for item in new_doc.review_item_mapping:
					if item.standard_item_code == old_standrad_item_code:
						item.standard_item_code = doc.get('item_code')
						item.item_mapping_retrived = doc.get('name')
				# new_doc.standard_item_code = doc.get('item_code')
				new_doc.table_of_standard_boms_produced = []
				new_doc.difference_between_previous_and_current_review_item_mappings = []
				new_doc.save()
				new_bct_doc_list.append(new_doc.name)
			else:
				if get_bct.standard_item_code == old_standrad_item_code:
					get_bct.standard_item_code = doc.get('item_code')
				for item in get_bct.review_item_mapping:
					if item.standard_item_code == old_standrad_item_code:
						item.standard_item_code = doc.get('item_code')
						item.item_mapping_retrived = doc.get('name')
				get_bct.table_of_standard_boms_produced = []
				get_bct.difference_between_previous_and_current_review_item_mappings = []
				get_bct.save()
				new_bct_doc_list.append(get_bct.name)
	item_mapping_doc = frappe.get_doc("Item Mapping",doc.get('name'))
	
	if  item_mapping_doc:
		data_dict = dict()
		data_dict['item_code'] = item_mapping_doc.item_code
		attribute_value_dict = {item.attribute:item.value for item in item_mapping_doc.attribute_table}
		data_dict['attribute_value_data']=attribute_value_dict
		item_mapping_doc.data_for_compare = frappe.as_json(data_dict)
		item_mapping_doc.propogate_updates_to_affected_boms_status = 'Completed'
		item_mapping_doc.save()
		frappe.msgprint("Propogation Completed")
		print("========",new_bct_doc_list)
		if len(new_bct_doc_list) > 0:
			return new_bct_doc_list
			

@frappe.whitelist()
def get_attribute_value(attribute):
	attribute_value = frappe.db.sql("""SELECT attribute_value from `tabItem Attribute Value` where parent = '{0}'""".format(attribute),as_dict=1,debug=1)
	return attribute_value

@frappe.whitelist()
def get_attributes(mapped_item):
	attribute_list = frappe.db.sql("""SELECT attribute from `tabItem Attribute Table` where parent = '{0}'""".format(mapped_item),as_dict=1)
	if attribute_list != []:
		return attribute_list

# Filter attributes
@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_attribute_in_table(doctype, txt, searchfield, start, page_len, filters):
	# return frappe.db.sql("""SELECT name from `tabCustom Item Attribute Value` where item_attribute = '{0}' and name like %(txt)s """.format(filters.get("attribute")),as_list=1,debug=1)
	return frappe.db.sql("""
		SELECT attribute
		FROM `tabItem Attribute Table` 
		WHERE parent = %(attribute)s
			
			AND name LIKE %(txt)s
		ORDER BY name DESC
		LIMIT %(offset)s, %(limit)s
		""".format(searchfield), dict(
				attribute=filters.get("mapped_item"),
				txt="%{0}%".format(txt),
				offset=start,
				limit=page_len
			)
		)
@frappe.whitelist()
def check_propogation_for_item_mapping(doc):
	pass