# Copyright (c) 2021, instrument and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from erpnext.stock.doctype.item.item import get_item_defaults
from frappe.model.naming import make_autoname


# BOM Creation tool working
# 1) Create mapped item
# 2) Create standard item code for mapped item
# 3) create mapped bom for mapped item
# 4) Run bom creation tool over the mapped bom
# 5) Enter the attribute values for mapped item on bom creation tool
  # 6) Click on Review Item Mapping
  # 7) Review Standard item codes and standard boms
# 7) Standard bom tree will be generated according to standard item code for mapped items

class BOMCreationTool(Document):
	@frappe.whitelist()
	def review_item_mappings(doc,method):
		if doc.attribute_table:
			doc.review_item_mapping = ''
			for row in doc.attribute_table:
				std_item = frappe.db.sql("""SELECT i.item_code from `tabItem Mapping` i join `tabAttribute Table` at on at.parent = i.name where i.mapped_item = '{0}' and at.attribute = '{1}' and at.value = '{2}'""".format(row.mapped_item,row.attribute,row.value),as_dict=1)

				if std_item:
					item_details = frappe.db.get_values("Item",{'name':std_item[0].get("item_code")},['item_name','default_bom'],as_dict=1)
					override_bom = frappe.db.get_value("Item Mapping",{'item_code':std_item[0].get("item_code"),'mapped_item':row.mapped_item},'do_not_override_existing_bom')
					doc.append('review_item_mapping',{
						'mapped_bom':row.mapped_bom,
						'mapped_item':row.mapped_item,
						'attribute':row.attribute,
						'value' :row.value,
						'standard_item_code': std_item[0].get("item_code") if std_item else '',
						'standard_item_name':item_details[0].get('item_name') if std_item else '',
						'standard_bom':item_details[0].get('default_bom') if not override_bom else ''
						})
				else:
					frappe.msgprint("Standard Item Code Not Found For Item {0} With Attribute Value {1}".format(row.mapped_item,row.value))
					doc.append('review_item_mapping',{
						'mapped_bom':row.mapped_bom,
						'mapped_item':row.mapped_item,
						'attribute':row.attribute,
						'value' :row.value,
						'standard_item_code': '',
						'standard_item_name':'',
						'standard_bom': ''
						})

		doc.save()

	@frappe.whitelist()
	def copy_to_all_rows(doc,method):
		if doc.attribute_table:
			value_list = [item.value for item in doc.attribute_table if item.value]
			final_dict = dict()
			if len(value_list) == 0:
				frappe.throw("Please Select Atleast One Value")
			else:
				attribute_value_list = frappe.db.sql("""SELECT distinct attribute,value from `tabBOM Creation Attribute Table` where parent = '{0}' and value != ''""".format(doc.name),as_dict=1)
				for row in attribute_value_list:
					final_dict[row.get("attribute")] = row.get("value")
			for item in doc.attribute_table:
				if item.attribute in final_dict:
					item.value = final_dict.get(item.attribute)
			doc.save()
			return True


	def autoname(doc):
		doc.name = make_autoname('BOM-' + '.YYYY.' + '-' + doc.mapped_bom + '-' + '.#####')
		return doc.name

	def before_submit(doc,method=None):
		if doc.mapped_bom and doc.review_item_mapping:
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
					std_item = frappe.db.get_value("Review Item Mapping",{'mapped_bom':bom.get("name"),'mapped_item':bom_doc.item,'parent':doc.name},'standard_item_code')
					item_details = frappe.db.get_values("Item",{'name':std_item},['item_name','default_bom'],as_dict=1)
					override_bom = frappe.db.get_value("Item Mapping",{'item_code':std_item,'mapped_item':bom_doc.item},'do_not_override_existing_bom')
					if not override_bom and not item_details[0].get("default_bom") or override_bom:
						std_bom = frappe.new_doc("BOM")
						if std_bom:
							item_data = get_item_defaults(std_item, default_company)
							std_bom.item = std_item
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
									raw_std_item = frappe.db.get_value("Review Item Mapping",{'mapped_bom':bom.get("name"),'mapped_item':line.item_code},'standard_item_code')
									raw_item_data = get_item_defaults(raw_std_item, default_company)
									default_bom = frappe.db.get_value("BOM",{'item':raw_std_item,'is_active':1,'is_default':1,'docstatus' : 1},'name')
									std_bom.append('items',{
										'item_code':raw_std_item,
										'item_name':raw_item_data.get("item_name"),
										'qty' : line.qty,
										'description':raw_item_data.get("description"),
										'stock_uom':raw_item_data.get("stock_uom"),
										'bom_no':default_bom,
										'conversion_factor':1,
										'rate':raw_item_data.get("valuation_rate"),
										'engineering_revision':raw_item_data.get('engineering_revision'),
										'use_specific_engineering_revision':line.use_specific_engineering_revision,
										'uom' : raw_item_data.get('uom'),
										'reference_item':line.item_code
										
										})

								else : 
									line.reference_item = line.item_code
									std_bom.append('items',line)
							std_bom.save(ignore_permissions = True)
							std_bom.submit()
								
def get_map_item_list(item_code):
	map_item_list = frappe.db.sql("""SELECT name from `tabItem Mapping` where mapped_item = '{0}'""".format(item_code),as_dict=1)
	return map_item_list
# get all the attributes for all mapped items
@frappe.whitelist()
def get_map_item_attributes(mapped_bom):
	if mapped_bom:
		check_bom_creation_doc = frappe.db.get_value("BOM Creation Tool",{'mapped_bom':mapped_bom},'name')
		if check_bom_creation_doc:
			b_doc = frappe.get_doc("BOM Creation Tool",check_bom_creation_doc)
			return b_doc.attribute_table,True
		else :
			mapped_bom_doc = frappe.get_doc("Mapped BOM",mapped_bom)
			map_item_attributes_list = [] 
			bom_childs = []
			bom_child_list = get_child_boms(mapped_bom,bom_childs)
			final_bom_list = [row.get("mapped_bom") for row in bom_child_list if row.get("mapped_bom")]
			final_bom_list.append(mapped_bom)
			if len(final_bom_list) == 1 :
				 item_list = frappe.db.sql("""SELECT item_code,mapped_bom from `tabMapped BOM Item` where parent = '{0}' and is_map_item = 1""".format(final_bom_list[0],as_dict=1))
			else:
				item_list = frappe.db.sql("""SELECT item_code,parent from `tabMapped BOM Item` where parent in {0} and is_map_item = 1""".format(tuple(final_bom_list)),as_dict=1)
			for row in item_list:
				if item_list:
					attributes = frappe.db.sql("""SELECT distinct a.attribute,m.mapped_item from `tabItem Mapping` m join `tabAttribute Table` a on a.parent = m.name where m.mapped_item = '{0}'""".format(row.get('item_code')),as_dict=1)
					row['attribute_list'] = attributes
			# main_item = frappe.db.sql("""SELECT distinct a.attribute,m.mapped_item from `tabItem Mapping` m join `tabAttribute Table` a on a.parent = m.name where m.mapped_item = '{0}'""".format(mapped_bom_doc.item),as_dict=1)
			for bom in final_bom_list:
				mapped_bom_doc = frappe.get_doc("Mapped BOM",bom)
				main_item = frappe.db.sql("""SELECT distinct a.attribute,m.mapped_item from `tabItem Mapping` m join `tabAttribute Table` a on a.parent = m.name where m.mapped_item = '{0}'""".format(mapped_bom_doc.item),as_dict=1)
				item_list.append({'item_code':mapped_bom_doc.item,'parent':bom,'attribute_list':main_item})
			return item_list,False

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
		# childs = frappe.db.sql("""SELECT mapped_bom from `tabMapped BOM Item` where parent = '{0}' and mapped_bom is not null and override_existing_bom = 1 """.format(mapped_bom),as_dict=1)
		childs = frappe.db.sql("""SELECT mapped_bom from `tabMapped BOM Item` where parent = '{0}' and mapped_bom is not null""".format(mapped_bom),as_dict=1)

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

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_standard_bom_for_query(doctype, txt, searchfield, start, page_len, filters):
	return frappe.db.sql("""SELECT name from `tabBOM` where item = '{0}' and docstatus =1 and is_active=1 and is_default =1""".format(filters.get("standard_item_code")))

@frappe.whitelist()
def get_standard_bom(standard_item_code,mapped_item):
	check_flag = frappe.db.get_value("Item Mapping",{'item_code':standard_item_code,'mapped_item':mapped_item},'do_not_override_existing_bom')
	default_bom = frappe.db.get_value("BOM",{'item':standard_item_code,'docstatus':1,'is_default':1,'is_active':1},'name')
	if not check_flag and default_bom:
		return default_bom
	else :
		return False