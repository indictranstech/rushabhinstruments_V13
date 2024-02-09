# Copyright (c) 2021, instrument and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from erpnext.stock.doctype.item.item import get_item_defaults
from frappe.model.naming import make_autoname
from frappe.utils import (
	add_days,
	ceil,
	cint,
	comma_and,
	flt,
	get_link_to_form,
	getdate,
	now_datetime,
	nowdate,
)

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
	def review_item_mappings(doc,method=None):
		if doc.attribute_table:
			final_items_review = []
			doc.review_item_mapping = ''
			doc.difference_between_previous_and_current_review_item_mappings = ''
			attributes_values = doc.attribute_table
			bom_childs = []
			bom_child_list = get_child_boms(doc.mapped_bom,bom_childs)
			bom_child_list.append({
				'mapped_bom' : doc.mapped_bom
				})
			final_bom_list = get_all_boms_in_order(bom_child_list)
			for bom in final_bom_list:
				bom_doc = frappe.get_doc("Mapped BOM",bom.get('name'))
				if bom_doc:
					# attribute_list = [row.attribute for row in doc.attribute_table if row.mapped_item == bom_doc.item and row.mapped_bom == bom.get("name")]
					# value_list = [row.value for row in doc.attribute_table if row.mapped_item == bom_doc.item and row.value and row.mapped_bom == bom.get("name")]
					attribute_list = [row.attribute for row in doc.attribute_table if row.mapped_item == bom_doc.item]
					value_list = [row.value for row in doc.attribute_table if row.mapped_item == bom_doc.item and row.value ]
					attribute_value_dict = {row.attribute:row.value for row in doc.attribute_table if row.mapped_item == bom_doc.item}

					if len(attribute_list) == 0 and len(value_list) == 0:
						attribute_list = get_attribute_for_main_item(bom_doc.item,doc.standard_item_code)
						value_list = get_value_for_main_item(bom_doc.item,doc.standard_item_code)
						attribute_value_dict = {attribute_list[i]: value_list[i] for i in range(len(attribute_list))}
						# attribute_list = [row.attribute for row in doc.item_assignment_table_for_mapped_item if row.mapped_item == bom_doc.item]
						# value_list = [row.value for row in doc.item_assignment_table_for_mapped_item if row.mapped_item == bom_doc.item and row.value]
						# attribute_value_dict = {row.attribute:row.value for row in doc.item_assignment_table_for_mapped_item if row.mapped_item == bom_doc.item}

					map_item_list_for_parent = get_map_item_list(bom_doc.item)
					parent_std_item_set  = []
					for parent_map_item in map_item_list_for_parent:
						parent_map_item_doc = frappe.get_doc("Item Mapping",parent_map_item)
						parent_map_attribute_list = [row.attribute for row in parent_map_item_doc.attribute_table]
						parent_map_value_list = [row.value for row in parent_map_item_doc.attribute_table]

						if set(parent_map_value_list) == set(value_list):
							parent_std_item_set.append(parent_map_item_doc.item_code)
					parent_std_item_list =list(set(parent_std_item_set))
					if len(parent_std_item_list) > 1 :
						frappe.msgprint("There are more than one standard item {1} mapped with selected attribute value {2} for item {0}".format(bom_doc.item,parent_std_item_list,value_list))
					if len(parent_std_item_list) == 0:
						frappe.msgprint("Standard Item Code not found for Mapped Item {0}".format(bom_doc.item))
						if bom_doc.item not in final_items_review:
							doc.append('review_item_mapping',{
								'mapped_bom':bom.get("name"),
								'mapped_item':bom_doc.item,
								'standard_item_code': '',
								'standard_item_name':'',
								'standard_bom': '',
								'to_be_created_standard_bom':'To Be Created from Mapped BOM',
								'attribute_value':str(attribute_value_dict),
								'item_mapping_retrived':''
								})
							final_items_review.append(bom_doc.item)
					else:
						item_name = frappe.db.get_value("Item",{'name':parent_std_item_list[0]},'item_name')
						item_details = frappe.db.get_values("Item",{'name':parent_std_item_list[0]},['item_name','default_bom'],as_dict=1)
						override_bom = frappe.db.get_value("Item Mapping",{'item_code':parent_std_item_list[0],'mapped_item':bom_doc.item},'do_not_override_existing_bom')
						bom_for_item = frappe.db.get_value("BOM",{'item':parent_std_item_list[0],'is_active':1,'is_default':1,'mapped_bom':bom.get('name')},'name')
						if not bom_for_item:
							bom_for_item = frappe.db.get_value("BOM",{'item':parent_std_item_list[0],'is_active':1},'name')
						item_mapping_retrived = frappe.db.get_value("Item Mapping",{'mapped_item':bom_doc.item,'item_code':parent_std_item_list[0]},'name')
						if bom_doc.item not in final_items_review:
							doc.append('review_item_mapping',{
								'mapped_bom':bom.get("name"),
								'mapped_item':bom_doc.item,
								'standard_item_code': parent_std_item_list[0],
								'standard_item_name':item_name,
								'standard_bom': bom_for_item if override_bom else '',
								'to_be_created_standard_bom':bom_for_item if override_bom else 'To Be Created from Mapped BOM',
								'attribute_value':str(attribute_value_dict),
								'item_mapping_retrived':item_mapping_retrived
								})
							final_items_review.append(bom_doc.item)
						for line in bom_doc.items:
							if line.is_map_item ==1 :
								raw_attribute_list = [row.attribute for row in doc.attribute_table if row.mapped_item == line.item_code]
								raw_value_list = [row.value for row in doc.attribute_table if row.mapped_item == line.item_code and row.value]

								raw_attribute_value_dict = {row.attribute:row.value for row in doc.attribute_table if row.mapped_item == line.item_code}
								map_item_list = get_map_item_list(line.item_code)
								raw_std_item_set  = []
											
								for map_item in map_item_list:
									map_item_doc = frappe.get_doc("Item Mapping",map_item)
									map_attribute_list = [row.attribute for row in map_item_doc.attribute_table]
									map_value_list = [row.value for row in map_item_doc.attribute_table]
			

									if set(map_value_list) == set(raw_value_list):
										raw_std_item_set.append(map_item_doc.item_code)
									
								raw_std_item_list =list(set(raw_std_item_set))
								if len(raw_std_item_list) > 1 :
									frappe.throw("There are more than one standard item {1} mapped with selected attribute value {2} for item {0}".format(line.item_code,raw_std_item_list,raw_value_list))
								if len(raw_std_item_list) == 0:
									frappe.msgprint("Standard Item Code not found for Mapped Item {0}".format(line.item_code))
									if line.item_code not in final_items_review:
										doc.append('review_item_mapping',{
											'mapped_bom':bom.get("name"),
											'mapped_item':line.item_code,
											'standard_item_code': '',
											'standard_item_name':'',
											'standard_bom': '',
											'to_be_created_standard_bom':'To Be Created from Mapped BOM',
											'attribute_value':str(raw_attribute_value_dict),
											'item_mapping_retrived':''
											})
										final_items_review.append(line.item_code)
								else:
									raw_item_name = frappe.db.get_value("Item",{'name':raw_std_item_list[0]},'item_name')
									raw_item_details = frappe.db.get_values("Item",{'name':raw_std_item_list[0]},['item_name','default_bom'],as_dict=1)
									raw_override_bom = frappe.db.get_value("Item Mapping",{'item_code':raw_std_item_list[0],'mapped_item':line.item_code},'do_not_override_existing_bom')
									bom_for_raw_item = frappe.db.get_value("BOM",{'item':raw_std_item_list[0],'is_active':1,'is_default':1},'name')
									if not bom_for_raw_item:
										bom_for_raw_item = frappe.db.get_value("BOM",{'item':raw_std_item_list[0],'is_active':1},'name')
									item_mapping_retrived_rm = frappe.db.get_value("Item Mapping",{'mapped_item':line.item_code,'item_code':raw_std_item_list[0]},'name')
									if line.item_code not in final_items_review:	
										doc.append('review_item_mapping',{
											'mapped_bom':bom.get("name"),
											'mapped_item':line.item_code,
											'standard_item_code': raw_std_item_list[0],
											'standard_item_name':raw_item_name,
											'standard_bom': bom_for_raw_item if raw_override_bom else '',
											'to_be_created_standard_bom':bom_for_raw_item if raw_override_bom else 'To Be Created from Mapped BOM',
											'attribute_value':str(raw_attribute_value_dict),
											'item_mapping_retrived':item_mapping_retrived_rm
											})
										final_items_review.append(line.item_code)
			doc.difference_table_data()
			if doc.check:
				doc.check = 0
			else:
				doc.check = 1
			# doc.save()
			return True
	def difference_table_data(doc):
		if doc.mapped_item and doc.mapped_bom and doc.standard_item_code:
			bom_creation_doc = frappe.db.get_value("BOM Creation Tool",{'mapped_item':doc.mapped_item,'standard_item_code':doc.standard_item_code,'docstatus':1},'name')

			if bom_creation_doc:
				previous_mapping = frappe.db.sql("""SELECT * from `tabReview Item Mapping` where parent = '{0}'""".format(bom_creation_doc),as_dict=1)
				for i in doc.review_item_mapping:
					if i not in previous_mapping:
						doc.append('difference_between_previous_and_current_review_item_mappings',i)

				# current_dict = {row.mapped_item:row for row in doc.review_item_mapping}
				# print("=-====",current_dict)
				previous_mapping_dict = dict()
				for row in previous_mapping:
					previous_mapping_dict[row.mapped_item]=row
				# for row in previous_mapping_dict:
				# 	if row not in current_dict:
				# 		doc.append('difference_between_previous_and_current_review_item_mappings',{
				# 				'mapped_bom':row.mapped_bom,
				# 				'mapped_item':row.mapped_item,
				# 				'standard_item_code': row.standard_item_code,
				# 				'standard_item_name':row.standard_item_name,
				# 				'standard_bom': row.standard_bom,
				# 				'attribute_value':row.attribute_value
				# 			})

				for row in doc.review_item_mapping:
					if row.mapped_item not in previous_mapping_dict:
						doc.append('difference_between_previous_and_current_review_item_mappings',{
								'mapped_bom':row.mapped_bom,
								'mapped_item':row.mapped_item,
								'standard_item_code': row.standard_item_code,
								'standard_item_name':row.standard_item_name,
								'standard_bom': row.standard_bom,
								'attribute_value':row.attribute_value
							})
					else:
						previous_mapping_dict.pop(row.mapped_item)
				if previous_mapping_dict:
					dict_values = previous_mapping_dict.values()
					dict_values_list = list(dict_values)
					for row in dict_values_list:
						doc.append('difference_between_previous_and_current_review_item_mappings',{
								'mapped_bom':row.get("mapped_bom"),
								'mapped_item':row.get("mapped_item"),
								'standard_item_code': row.get("standard_item_code"),
								'standard_item_name':row.get("standard_item_name"),
								'standard_bom': row.get("standard_bom"),
								'attribute_value':row.get("attribute_value")
							})
		# doc.save()
		return True
	@frappe.whitelist()
	def copy_to_all_rows(doc,method):
		if doc.attribute_table:
			value_list = [item.value for item in doc.attribute_table if item.value]
			final_dict = dict()
			if len(value_list) == 0:
				frappe.throw("Please Select Atleast One Value")
			else:
				final_dict = {row.attribute:row.value for row in doc.attribute_table if row.parent == doc.name and row.value != ''}
				# attribute_value_list = frappe.db.sql("""SELECT distinct attribute,value from `tabBOM Creation Attribute Table` where parent = '{0}' and value != ''""".format(doc.name),as_dict=1)
				# for row in attribute_value_list:
				# 	final_dict[row.get("attribute")] = row.get("value")
			for item in doc.attribute_table:
				if item.attribute in final_dict:
					item.value = final_dict.get(item.attribute)
			# doc.save()
			# doc.reload()
			return True


	def autoname(doc):
		# doc.name = make_autoname('BOM-' + '.YYYY.' + '-' + doc.mapped_bom + '-' + '.#####')
		# if doc.mapped_item and doc.item_assignment_table_for_mapped_item and not doc.standard_item_code:
		# 	attribute_list = [row.attribute for row in doc.item_assignment_table_for_mapped_item if row.mapped_item == doc.mapped_item]
		# 	value_list = [row.value for row in doc.item_assignment_table_for_mapped_item if row.mapped_item == doc.mapped_item and row.value]
		# 	map_item_list_for_parent = get_map_item_list(doc.mapped_item)
		# 	parent_std_item_set  = []
		# 	for parent_map_item in map_item_list_for_parent:
		# 		parent_map_item_doc = frappe.get_doc("Item Mapping",parent_map_item)
		# 		parent_map_attribute_list = [row.attribute for row in parent_map_item_doc.attribute_table]
		# 		parent_map_value_list = [row.value for row in parent_map_item_doc.attribute_table]
		# 		if set(parent_map_value_list) == set(value_list):
		# 			parent_std_item_set.append(parent_map_item_doc.item_code)
		# 	parent_std_item_list =list(set(parent_std_item_set))
		# 	if len(parent_std_item_list) > 1 :
		# 		frappe.msgprint("There are more than one standard item {1} mapped with selected attribute value {2} for item {0}".format(doc.mapped_item,parent_std_item_list,value_list))
		# 	if len(parent_std_item_list) == 0 and not doc.standard_item_code:
		# 		frappe.throw("Standard Item Code not found for Mapped Item {0}".format(doc.mapped_item))
		# 	doc.standard_item_code = parent_std_item_list[0]
		# 	default_bom = frappe.db.get_value("BOM",{'item':parent_std_item_list[0],'is_default':1,'is_active':1,'docstatus':1},'name')
		# 	if not default_bom :
		# 		default_bom = frappe.db.get_value("BOM",{'item':parent_std_item_list[0],'is_active':1,'docstatus':1},'name')
		# 	doc.standard_bom = default_bom

		if doc.mapped_item and doc.standard_item_code:
			doc.name = make_autoname('BOM-CREATE-' + doc.mapped_item + '-' +  doc.standard_item_code + '-'+'.###')
		else:
			frappe.throw("Please Enter The Value For Mapped Item And Standard Item Code")
		return doc.name

	def on_submit(doc,method=None):
		bom_name = frappe.db.get_value("BOM",{'item':doc.standard_item_code,'bom_creation_tool':doc.name},'name')
		if bom_name:
			doc.version_of_bom_released = bom_name
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
			print("=============final_bom_list",final_bom_list)
			std_bom_list_for_bct = []
			for bom in final_bom_list:
				bom_doc = frappe.get_doc("Mapped BOM",bom.get('name'))
				if bom_doc:
					default_company = frappe.db.get_single_value("Global Defaults",'default_company')
					# std_item = frappe.db.get_value("Review Item Mapping",{'mapped_bom':bom.get("name"),'mapped_item':bom_doc.item,'parent':doc.name},'standard_item_code')
					std_item = frappe.db.get_value("Review Item Mapping",{'mapped_item':bom_doc.item,'parent':doc.name},'standard_item_code',debug=1)
					print("==============std_item",std_item,bom_doc.item)
					if not std_item:
						frappe.throw("Standard Item Code Not found for {0}".format(bom_doc.item))
					item_details = frappe.db.get_values("Item",{'name':std_item},['item_name','default_bom'],as_dict=1)
					override_bom = frappe.db.get_value("Item Mapping",{'item_code':std_item,'mapped_item':bom_doc.item},'do_not_override_existing_bom')
					bom_for_item = frappe.db.get_value("BOM",{'item':std_item,'is_active':1,'mapped_bom':bom_doc.get('name')},'name')
					# last_doc = frappe.get_last_doc("BOM",filters={'item':std_item})
					if not bom_for_item or not override_bom:
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
							std_bom.with_operations = bom_doc.get("with_operations")
							std_bom.inspection_required = bom_doc.get("inspection_required")
							std_bom.bom_level = bom_doc.get("bom_level")
							std_bom.mapped_bom = bom.get('name')
							item_mapping = frappe.db.get_value("Item Mapping",{'item_code':std_item,'mapped_item':bom_doc.item},'name')
							if bom_doc.get("with_operations"):
								std_bom.transfer_material_against =  bom_doc.get('transfer_material_against')
								std_bom.routing = bom_doc.get('routing')
								
							if item_mapping:
								item_mapping_doc = frappe.get_doc("Item Mapping",item_mapping)
								if item_mapping_doc.override_mapped_bom_operation_table:
									if item_mapping_doc.bom_operations:
										for op in item_mapping_doc.bom_operations:
											std_bom.append('operations',{
												'operation' : op.operation,
												'workstation' : op.workstation,
												'time_in_mins' : op.time_in_mins,
												'hour_rate' : op.hour_rate,
												'base_operating_cost' : op.base_operating_cost,
												'batch_size' : op.batch_size,
												'set_cost_based_on_bom_qty' : op.set_cost_based_on_bom_qty,
												'description' : op.description
												})
								else:
									for op in bom_doc.operations:
										std_bom.append('operations',{
											'operation' : op.operation,
											'workstation' : op.workstation,
											'time_in_mins' : op.time_in_mins,
											'hour_rate' : op.hour_rate,
											'base_operating_cost' : op.base_operating_cost,
											'batch_size' : op.batch_size,
											'set_cost_based_on_bom_qty' : op.set_cost_based_on_bom_qty,
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
							print("=================bom items",bom_doc.items)
							for line in bom_doc.items:
								if line.is_map_item ==1 :
									print("===============yes")
									# raw_std_item = frappe.db.get_value("Review Item Mapping",{'mapped_bom':bom.get("name"),'mapped_item':line.item_code},'standard_item_code')
									raw_std_item = frappe.db.get_value("Review Item Mapping",{'mapped_item':line.item_code},'standard_item_code')
									if not raw_std_item:
										frappe.throw("Standard Item Code Not found for {0}".format(line.item_code))
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
									print("=====================no")

									line.reference_item = line.item_code
									raw_item_data = get_item_defaults(line.item_code, default_company)
									default_bom = frappe.db.get_value("BOM",{'item':line.item_code,'is_active':1,'is_default':1,'docstatus' : 1},'name')
									std_bom.append('items',{
										'item_code': line.item_code,
										'item_name':raw_item_data.get("item_name"),
										'qty' : line.qty,
										'description':line.description,
										'stock_uom':line.stock_uom,
										'bom_no':line.bom_no,
										'conversion_factor':1,
										'rate':line.rate,
										'engineering_revision':line.engineering_revision,
										'use_specific_engineering_revision':line.use_specific_engineering_revision,
										'uom' : line.uom,
										'reference_item':line.item_code
										
										})

									# std_bom.append('items',line)
							std_bom.bom_creation_tool = doc.name
							std_bom.save(ignore_permissions = True)
							std_bom.submit()
							doc.append('table_of_standard_boms_produced',{
								'standard_item':std_item,
								# 'previous_standard_bom':last_doc if last_doc else '',
								'new_standard_bom':std_bom.name,
								'bom_level':std_bom.bom_level
								})
			doc.status = 'Completed'
		else:
			frappe.throw("Please Check Review Item Mapping")

def get_attribute_for_main_item(map_item,std_item):
	attributes = frappe.db.sql("""SELECT distinct a.attribute from `tabItem Mapping` m join `tabAttribute Table` a on a.parent = m.name where m.mapped_item = '{0}' and m.item_code = '{1}'""".format(map_item,std_item),as_dict=1)
	attribute_list = [item.attribute for item in attributes]
	return attribute_list
def get_value_for_main_item(map_item,std_item):
	values = frappe.db.sql("""SELECT distinct a.value from `tabItem Mapping` m join `tabAttribute Table` a on a.parent = m.name where m.mapped_item = '{0}' and m.item_code = '{1}'""".format(map_item,std_item),as_dict=1)
	value_list = [item.value for item in values]
	return value_list				
def get_map_item_list(item_code):
	map_item_list = frappe.db.sql("""SELECT name from `tabItem Mapping` where mapped_item = '{0}'""".format(item_code),as_dict=1)
	return map_item_list
# get all the attributes for all mapped items
@frappe.whitelist()
def get_map_item_attributes(mapped_bom,mapped_item,standard_item_code,item_mapping):
	if mapped_bom:
		# check_bom_creation_doc = frappe.db.get_value("BOM Creation Tool",{'mapped_bom':mapped_bom,'docstatus':1,'mapped_item':mapped_item,'standard_item_code':standard_item_code},'name')
		# if check_bom_creation_doc:
		# 	b_doc = frappe.get_doc("BOM Creation Tool",check_bom_creation_doc)
		# 	return b_doc.attribute_table,True
		# else :
		mapped_bom_doc = frappe.get_doc("Mapped BOM",mapped_bom)
		map_item_attributes_list = [] 
		bom_childs = []
		bom_child_list = get_child_boms(mapped_bom,bom_childs)
		final_bom_list = [row.get("mapped_bom") for row in bom_child_list if row.get("mapped_bom")]
		final_bom_list.append(mapped_bom)
		# final_bom_list.remove(mapped_bom)
		
		if len(final_bom_list) == 1 :
			 item_list = frappe.db.sql("""SELECT item_code,parent from `tabMapped BOM Item` where parent = '{0}' and is_map_item = 1""".format(final_bom_list[0]),as_dict=1)
		else:
			item_list = frappe.db.sql("""SELECT item_code,parent from `tabMapped BOM Item` where parent in {0} and is_map_item = 1""".format(tuple(final_bom_list)),as_dict=1)
		for row in item_list:	
			if item_list:
				attributes = frappe.db.sql("""SELECT distinct a.attribute,m.mapped_item from `tabItem Mapping` m join `tabAttribute Table` a on a.parent = m.name where m.mapped_item = '{0}'""".format(row.get('item_code')),as_dict=1)
				row['attribute_list'] = attributes
		# main_item = frappe.db.sql("""SELECT distinct a.attribute,m.mapped_item from `tabItem Mapping` m join `tabAttribute Table` a on a.parent = m.name where m.mapped_item = '{0}'""".format(mapped_bom_doc.item),as_dict=1)
		final_item_list = []
		check_items = []
		final_bom_list.remove(mapped_bom)
		for bom in final_bom_list:
			mapped_bom_doc = frappe.get_doc("Mapped BOM",bom)
			main_item = frappe.db.sql("""SELECT distinct a.attribute,m.mapped_item from `tabItem Mapping` m join `tabAttribute Table` a on a.parent = m.name where m.mapped_item = '{0}'""".format(mapped_bom_doc.item),as_dict=1)
			item_list.append({'item_code':mapped_bom_doc.item,'parent':bom,'attribute_list':main_item})
		for row in item_list:
			mapped_bom_list = [item.get("parent") for item in item_list if item.get("item_code") == row.get("item_code")]
			mapped_bom_list = [get_link_to_form(mapped_bom_doc.doctype, p) for p in mapped_bom_list]
			if row.get("item_code") not in check_items:
				row['mapped_boms'] = str(mapped_bom_list)
				final_item_list.append(row)
				check_items.append(row.get("item_code"))
		check_bom_creation_doc = frappe.db.get_value("BOM Creation Tool",{'mapped_bom':mapped_bom,'mapped_item':mapped_item,'standard_item_code':standard_item_code},'name')
		if check_bom_creation_doc:
			b_doc = frappe.get_doc("BOM Creation Tool",check_bom_creation_doc)
			data_dict = {(row.mapped_item,row.attribute):row for row in b_doc.attribute_table}
			for row in final_item_list:
				if (row.attribute_list[0].get('mapped_item'),row.attribute_list[0].get('attribute')) in data_dict:
					for item in row.attribute_list:
						if (item.get('mapped_item'),item.get('attribute')) in data_dict:
							item['value'] = data_dict.get((item.get('mapped_item'),item.get('attribute'))).get("value")
						else:
							item['value'] = ''
		else:
			item_mapping_doc = frappe.get_doc("Item Mapping",item_mapping)
			attribute_dict = {item.attribute:item.value for item in item_mapping_doc.attribute_table}
			if item_mapping_doc:
				for row in final_item_list:
					for col in row.attribute_list:
						if col.attribute in attribute_dict:
							col['value'] = attribute_dict.get(col.attribute)
		return final_item_list,False

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
		final_list = [row.get('mapped_bom') for row in bom_childs if row.get("mapped_bom")]

		final_list = '(' + ','.join("'{}'".format(i) for i in final_list) + ')'
		childs = frappe.db.sql("""SELECT mb.name,mb.bom_level from `tabMapped BOM` mb where mb.name in {0} order by mb.bom_level asc""".format(final_list),as_dict=1)
		return childs

# Filter attribute values
@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_attribute_value(doctype, txt, searchfield, start, page_len, filters):
	# return frappe.db.sql("""SELECT name from `tabCustom Item Attribute Value` where item_attribute = '{0}' and name like %(txt)s """.format(filters.get("attribute")),as_list=1,debug=1)
	return frappe.db.sql("""
		SELECT name
		FROM `tabCustom Item Attribute Value` 
		WHERE item_attribute = %(attribute)s
			
			AND name LIKE %(txt)s
		ORDER BY name DESC
		LIMIT %(offset)s, %(limit)s
		""".format(searchfield), dict(
				attribute=filters.get("attribute"),
				txt="%{0}%".format(txt),
				offset=start,
				limit=page_len
			)
		)


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
@frappe.whitelist()
def get_map_item_attributes_for_mapped_item(mapped_bom):
	if mapped_bom:
		item_list = []
		mapped_item = frappe.db.get_value("Mapped BOM",{'name':mapped_bom},'item')
		mapped_item_data = frappe.db.sql("""SELECT distinct a.attribute,m.mapped_item from `tabItem Mapping` m join `tabAttribute Table` a on a.parent = m.name where m.mapped_item = '{0}'""".format(mapped_item),as_dict=1)
		if len(mapped_item_data) == 0:
			frappe.throw("Please Create Item Mapping for item {0}".format(mapped_item))
		item_list.append(mapped_item_data)
		return item_list

@frappe.whitelist()
def get_mapped_bom(mapped_item):
	mapped_bom = frappe.db.get_value("Mapped BOM",{'item':mapped_item,'is_active':1,'is_default':1,'docstatus':1},'name')
	if not mapped_bom:
		mapped_bom = frappe.db.get_value("Mapped BOM",{'item':mapped_item,'is_active':1,'docstatus':1},'name')
	return mapped_bom

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_standard_item_code(doctype, txt, searchfield, start, page_len, filters):
	cond = ''
	if filters and filters.get('mapped_item'):
		# mapped_item = frappe.db.get_value('Item Mappings', filters.get('mapped_item'), 'mapped_item')
		cond = "and mapped_item = '%s'" % filters.get('mapped_item')

	return frappe.db.sql("""SELECT item_code from `tabItem Mapping`
			where `{key}` LIKE %(txt)s {cond}
			order by name limit %(start)s, %(page_len)s"""
			.format(key=searchfield, cond=cond), {
				'txt': '%' + txt + '%',
				'start': start, 'page_len': page_len
			})
@frappe.whitelist()
def check_recent_version_of_BCT(standard_item_code):
	if standard_item_code:
		check_BCT = frappe.db.sql("""SELECT b.name from `tabBOM Creation Tool` b where b.standard_item_code = '{0}' and b.status != 'Cancelled' order by b.name desc""".format(standard_item_code),as_dict=1)
		if check_BCT:
			return check_BCT[0].get('name')

@frappe.whitelist()
def review_item_mapping_for_affected(new_doc):
	review_item_mappings(new_doc)


@frappe.whitelist()
def get_std_item_from_mapping(item_mapping):
	std_item_code = frappe.db.get_value("Item Mapping",{'name':item_mapping},'item_code')
	if std_item_code:
		return std_item_code