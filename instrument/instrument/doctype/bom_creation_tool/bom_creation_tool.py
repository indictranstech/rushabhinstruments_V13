# Copyright (c) 2021, instrument and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from erpnext.stock.doctype.item.item import get_item_defaults


# BOM Creation tool working
# 1) Create mapped item
# 2) Create standard item code for mapped item
# 3) create mapped bom for mapped item
# 4) Run bom creation tool over the mapped bom
# 5) Enter the attribute values for mapped item on bom creation tool
# 6) Standard bom tree will be generated according to standard item code for mapped items

class BOMCreationTool(Document):
	def before_submit(doc,method=None):
		if doc.mapped_bom:
			attributes_values = doc.attribute_table
			bom_childs = []
			override_bom_child = []
			bom_child_list = get_child_boms(doc.mapped_bom,bom_childs)
			override_bom_child_dict = override_bom_list(doc.mapped_bom,override_bom_child)
			override_bom_child_list = [row.mapped_bom for row in override_bom_child_dict]
			bom_child_list.append({
				'mapped_bom' : doc.mapped_bom
				})
			final_bom_list = get_all_boms_in_order(bom_child_list)
			for bom in final_bom_list:
				bom_doc = frappe.get_doc("Mapped BOM",bom.get('name'))
				if bom_doc:
					default_company = frappe.db.get_single_value("Global Defaults",'default_company')
					attribute_list = [row.attribute for row in doc.attribute_table if row.mapped_item == bom_doc.item]
					value_list = [row.value for row in doc.attribute_table if row.mapped_item == bom_doc.item and row.value]
					if len(value_list) == 0:
						frappe.throw("Please Select Atlease One Attribute Value for Item {0}".format(bom_doc.item))
					map_item_list_for_parent = get_map_item_list(bom_doc.item)
					parent_std_item_set  = []
					for parent_map_item in map_item_list_for_parent:
						parent_map_item_doc = frappe.get_doc("Mapped Item",parent_map_item)
						parent_map_attribute_list = [row.attribute for row in parent_map_item_doc.attribute_table]
						parent_map_value_list = [row.value for row in parent_map_item_doc.attribute_table]

						if set(parent_map_value_list) == set(value_list):
							parent_std_item_set.append(parent_map_item_doc.item_code)
					parent_std_item_list =list(set(parent_std_item_set))
					if len(parent_std_item_list) > 1 :
						frappe.throw("There are more than one standard item {1} mapped with selected attribute value {2} for item {0}".format(bom_doc.item,parent_std_item_list,value_list))
					elif len(parent_std_item_list) == 1 :
						default_bom_available = frappe.db.get_value("BOM",{'is_active':1,'is_default':1,'item':parent_std_item_list[0],'docstatus':1},'name')
						if (bom.get("name") in override_bom_child_list and not default_bom_available) or bom.get("name") not in override_bom_child_list :
							std_bom = frappe.new_doc("BOM")
							if std_bom:
								item_data = get_item_defaults(parent_std_item_list[0], default_company)
								std_bom.item = parent_std_item_list[0]
								std_bom.item_name = item_data.get("item_name")
								std_bom.company = default_company
								std_bom.uom = item_data.get("stock_uom")
								std_bom.is_active = 1
								std_bom.is_default = 1
								std_bom.quantity = bom_doc.get("quantity")
								std_bom.set_rate_of_sub_assembly_item_based_on_bom = bom_doc.get("set_rate_of_sub_assembly_item_based_on_bom")
								std_bom.currency = bom_doc.get("currency")
								std_bom.rm_cost_as_per = bom_doc.get("rm_cost_as_per")
								std_bom.operations = bom_doc.get("operations")
								std_bom.inspection_required = bom_doc.get("inspection_required")
								std_bom.bom_level = bom_doc.get("bom_level")
								std_bom.mapped_bom = bom.get('name')
								if bom_doc.get("operations"):
									std_bom.transfer_material_against =  bom_doc.get('transfer_material_against')
									std_bom.routing = bom_doc.get('routing')
									for op in bom_doc.operations:
										std_bom.append('operations',{
											'operation' : op.operation,
											'workstation' : op.workstation,
											'time_in_mins' : op.time_in_mins,
											'hour_rate' : op.hour_rate,
											'base_operating_cost' : op.base_operating_cost,
											'batch_size' : op.batch_size,
											'set_cost_based_on_bom_quantity' : op.set_cost_based_on_bom_quantity,
											'description' : op.description

											})
								if bom_doc.scrap_items :
									for scrap in bom_doc.scrap_items :
										std_bom.append('scrap_items',{
											'item_code' : scrap.item_code,
											'item_name' : scrap.item_name,
											'is_process_loss' : scrap.is_process_loss,
											'stock_qty' : scrap.stock_qty,
											'stock_uom' : scrap.stock_uom,
											'rate' :scrap.rate
											})
								for line in bom_doc.items:
									if line.is_map_item ==1 :
										raw_attribute_list = [row.attribute for row in doc.attribute_table if row.mapped_item == line.item_code]
										raw_value_list = [row.value for row in doc.attribute_table if row.mapped_item == line.item_code and row.value]
										if len(raw_value_list) == 0:
											frappe.throw("Please Select Atlease One Attribute Value for Item {0}".format(line.item_code))
										map_item_list = get_map_item_list(line.item_code)
										raw_std_item_set  = []
										
										for map_item in map_item_list:
											map_item_doc = frappe.get_doc("Mapped Item",map_item)
											map_attribute_list = [row.attribute for row in map_item_doc.attribute_table]
											map_value_list = [row.value for row in map_item_doc.attribute_table]
						

											# for value in map_value_list:
											# 	if value in raw_value_list:
											# 		raw_std_item_set.append(map_item_doc.item_code)

										

											if set(map_value_list) == set(raw_value_list):
												raw_std_item_set.append(map_item_doc.item_code)
											
										raw_std_item_list =list(set(raw_std_item_set))
										if len(raw_std_item_list) > 1 :
											frappe.throw("There are more than one standard item {1} mapped with selected attribute value {2} for item {0}".format(line.item_code,raw_std_item_list,raw_value_list))
										elif len(raw_std_item_list) == 1 :
											raw_item_data = get_item_defaults(raw_std_item_list[0], default_company)
											default_bom = frappe.db.get_value("BOM",{'item':raw_std_item_list[0],'is_active':1,'is_default':1,'docstatus' : 1},'name')
											std_bom.append('items',{
												'item_code':raw_std_item_list[0],
												'item_name':raw_item_data.get("item_name"),
												'description':raw_item_data.get("description"),
												'stock_uom':raw_item_data.get("stock_uom"),
												'bom_no':default_bom,
												'conversion_factor':1,
												'rate':raw_item_data.get("valuation_rate"),
												'engineering_revision':raw_item_data.get('engineering_revision'),
												'use_specific_engineering_revision':line.use_specific_engineering_revision,
												'uom' : raw_item_data.get('uom')
												})
										else :
											frappe.throw("Standard Item Code not found for Mapped Item {0}".format(line.item_code))

									else : 
										std_bom.append('items',line)
								std_bom.save(ignore_permissions = True)
								std_bom.submit()

						else :
							frappe.throw("Standard Item Code not found for Mapped Item {0}".format(bom_doc.item))			
								
def get_map_item_list(item_code):
	map_item_list = frappe.db.sql("""SELECT name from `tabMapped Item` where mapped_item = '{0}'""".format(item_code),as_dict=1)
	return map_item_list
# get all the attributes for all mapped items
@frappe.whitelist()
def get_map_item_attributes(mapped_bom):
	if mapped_bom:
		mapped_bom_doc = frappe.get_doc("Mapped BOM",mapped_bom)
		map_item_attributes_list = [] 
		bom_childs = []
		bom_child_list = get_child_boms(mapped_bom,bom_childs)
		final_bom_list = [row.get("mapped_bom") for row in bom_child_list]
		final_bom_list.append(mapped_bom)
		if len(final_bom_list) == 1:
			item_list = frappe.db.sql("""SELECT item_code from `tabMapped BOM Item` where parent = '{0}' and is_map_item = 1""".format(final_bom_list[0]),as_dict=1)
		else :
			item_list = frappe.db.sql("""SELECT item_code from `tabMapped BOM Item` where parent in {0} and is_map_item = 1""".format(tuple(final_bom_list)),as_dict=1)
		final_item_list = [item.item_code for item in item_list]
		final_item_list.append(mapped_bom_doc.item)
		if len(final_item_list) == 1:
			attributes = frappe.db.sql("""SELECT distinct a.attribute,m.mapped_item from `tabMapped Item` m join `tabAttribute Table` a on a.parent = m.name where m.mapped_item = '{0}'""".format(final_item_list[0]),as_dict=1)
		else : 
			attributes = frappe.db.sql("""SELECT distinct a.attribute , m.mapped_item from `tabMapped Item` m join `tabAttribute Table` a on a.parent = m.name where m.mapped_item in {0}""".format(tuple(final_item_list)),as_dict=1)
		for col in attributes:
			map_item_attributes_list.append(col)
		
		return map_item_attributes_list

# Get all child mapped_bom
def get_child_boms(mapped_bom,bom_childs):
		if mapped_bom:
			childs = frappe.db.sql("""SELECT mapped_bom from `tabMapped BOM Item` where parent = '{0}' and mapped_bom is not null """.format(mapped_bom),as_dict=1)

			bom_childs += childs

			if len(childs)>0:
				for c in childs:
					get_child_boms(c.get('mapped_bom'),bom_childs)
			return bom_childs
def override_bom_list(mapped_bom,override_bom_child):
	if mapped_bom:
		childs = frappe.db.sql("""SELECT mapped_bom from `tabMapped BOM Item` where parent = '{0}' and mapped_bom is not null and override_existing_bom = 1 """.format(mapped_bom),as_dict=1)

		override_bom_child += childs

		if len(childs)>0:
			for c in childs:
				override_bom_list(c.get('mapped_bom'),override_bom_child)
		return override_bom_child

# Get all the boms in order
def get_all_boms_in_order(bom_childs):
	if len(bom_childs)>1:
		final_list = [row.get('mapped_bom') for row in bom_childs]
		childs = frappe.db.sql("""SELECT mb.name,mb.bom_level from `tabMapped BOM` mb where mb.name in {0} order by mb.bom_level asc""".format(tuple(final_list)),as_dict=1,debug=1)
		return childs

# Filter attribute values
@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_attribute_value(doctype, txt, searchfield, start, page_len, filters):
	return frappe.db.sql("""SELECT name from `tabCustom Item Attribute Value` where item_attribute = '{0}'""".format(filters.get("attribute")))