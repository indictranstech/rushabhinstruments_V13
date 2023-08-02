from __future__ import unicode_literals
import frappe

def validate(doc,method):
	set_bom_level(doc)
	# Sort bom items according to s item_code
	final_item_list = []
	for row in doc.items:
		final_item_list.append({
			'name' :row.get("name"),
			'creation' : row.get("creation"),
			'modified' : row.get("modified"),
			'modified_by' : row.get("modified_by"),
			'owner' : row.get("owner"),
			'docstatus' : row.get("docstatus"),
			'do_not_explode':row.get("do_not_explode"),
			'parent':row.get("parent"),
			'parentfield':row.get("parentfield"),
			'parenttype':row.get("parenttype"),
			'idx' :row.get("idx"),
			'item_code':row.get("item_code"),
			'item_name':row.get("item_name"),
			'operation':row.get("operation"),
			'bom_no':row.get("bom_no"),
			'source_warehouse':row.get("source_warehouse"),
			'allow_alternative_item':row.get("allow_alternative_item"),
			'description':row.get("description"),
			'image':row.get("image"),
			'qty':row.get("qty"),
			'uom':row.get("uom"),
			'stock_qty':row.get("stock_qty"),
			'stock_uom':row.get("stock_uom"),
			'conversion_factor':row.get("conversion_factor"),
			'rate':row.get("rate"),
			'base_rate':row.get("base_rate"),
			'amount':row.get("amount"),
			'base_amount':row.get("base_amount"),
			'scrap':row.get("scrap"),
			'qty_consumed_per_unit':row.get("qty_consumed_per_unit"),
			'has_variants':row.get("has_variants"),
			'include_item_in_manufacturing':row.get("include_item_in_manufacturing"),
			'original_item':row.get("original_item"),
			'sourced_by_supplier':row.get("sourced_by_supplier"),
			'engineering_revision' : row.get('engineering_revision'),
			'use_specific_engineering_revision' : row.get('use_specific_engineering_revision')
			})
	final_data = sorted(final_item_list,key = lambda x:x["item_code"])
	doc.items = ''
	count = 1
	for col in final_data:
		col.update({'idx' : count})
		doc.append("items",col)
		count = count + 1

	exploded_items_list = []
	for item in doc.exploded_items:
		default_uom = frappe.db.get_value("Item",{'item_code':item.get("item_code")},'stock_uom')
		exploded_items_list.append({
			'name':item.get("name"),
			'creation':item.get("creation"),
			'modified':item.get("modified"),
			'modified_by':item.get("modified_by"),
			'owner':item.get("owner"),
			'docstatus':item.get("docstatus"),
			'parent':item.get("parent"),
			'parentfield':item.get("parentfield"),
			'parenttype':item.get("parenttype"),
			'idx':item.get("idx"),
			'item_code':item.get("item_code"),
			'item_name':item.get("item_name"),
			'source_warehouse':item.get("source_warehouse"),
			'operation':item.get("operation"),
			'description':item.get("description"),
			'image':item.get("image"),
			'stock_qty':item.get("stock_qty"),
			'rate':item.get("rate"),
			'qty_consumed_per_unit':item.get("qty_consumed_per_unit"),
			'stock_uom':default_uom,
			'amount':item.get("amount"),
			'include_item_in_manufacturing':item.get("include_item_in_manufacturing"),
			'sourced_by_supplier':item.get("sourced_by_supplier")
			})

	exploded_items_data = sorted(exploded_items_list,key = lambda x:x['item_code'])
	doc.exploded_items = ''
	cont = 1

	for row in exploded_items_data:
		row.update({"idx":cont})
		doc.append("exploded_items",row)
		cont = cont + 1

def set_bom_level(doc, update=False):
		levels = []

		doc.bom_level = 0
		for row in doc.items:
			if row.bom_no:
				levels.append(frappe.get_cached_value("BOM", row.bom_no, "bom_level") or 0)

		if levels:
			doc.bom_level = max(levels) + 1

		if update:
			doc.db_set("bom_level", doc.bom_level)
@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_engineering_revisions_for_filter(doctype, txt, searchfield, start, page_len, filters):
	return frappe.db.sql(""" SELECT name FROM `tabEngineering Revision` where item_code = '{0}' """.format(filters.get("item_code")))
@frappe.whitelist()
def get_engineering_revision(item_code):
	if item_code:
		engineering_revision = frappe.db.get_value("Item",{'name':item_code},'engineering_revision')
		return engineering_revision

@frappe.whitelist()
def get_bom_query(item_code):
	bom_query = frappe.db.sql("""SELECT name from `tabBOM` where item = '{0}'""".format(item_code),as_dict=1)
	bom_list = [item.name for item in bom_query]
	return bom_list

@frappe.whitelist()
def get_default_bom(item_code, bom):
	bom_no = frappe.db.get_value("BOM",{'item':item_code,'is_default' :1,'is_active' : 1},'name')
	frappe.db.set_value("BOM", bom, "old_reference_bom", bom_no)
	frappe.db.commit()
	return bom_no

@frappe.whitelist()
def duplicate_bom(doc):
	bom_items = frappe.db.sql("""SELECT * from `tabBOM` where name = '{0}'""".format(doc),as_dict=1)
	item_data = frappe.db.sql("""SELECT * from `tabBOM Item` where parent = '{0}'""".format(doc),as_dict=1)
	operations = frappe.db.sql("""SELECT * from `tabBOM Operation` where parent = '{0}'""".format(doc),as_dict=1)
	scrap_data = frappe.db.sql("""SELECT * from `tabBOM Scrap Item` where parent = '{0}'""".format(doc),as_dict=1)
	bom_items[0]['items'] = item_data
	bom_items[0]['operations'] = operations
	bom_items[0]['scrap_data'] = scrap_data
	return bom_items[0]

def disable_old_boms(doc, method):
	if doc.is_default:
		if frappe.db.get_value("Item",{'name':doc.item},'auto_disable_old_active_boms'):
			old_boms = frappe.db.sql("""SELECT name from `tabBOM` WHERE item='{0}' AND name<'{1}' """.format(doc.item,doc.name), as_dict=1)
			for bom in old_boms:
				bom_doc = frappe.get_doc('BOM', bom)
				if bom_doc.is_active:
					any_wos = frappe.db.sql("""SELECT name FROM `tabWork Order` WHERE bom_no='{0}' AND status IN ('Submitted','Not Started', 'In Process','Draft')""".format(bom['name']))
					any_mboms = frappe.db.sql("""SELECT name FROM `tabMapped BOM Item` WHERE bom_no='{0}'""".format(bom['name']))
					if not any_wos and not any_mboms:
						bom_doc.is_active = 0
					if any_wos:
						bom_doc.to_be_disabled = 1
					bom_doc.save()
					bom_doc.submit()



@frappe.whitelist()
def update_bom_status():
	bom_list = frappe.db.sql("""SELECT name FROM `tabBOM` where name='BOM-13440-002' """, as_dict=1)

	for row in bom_list:
		bom_log = frappe.db.sql("""SELECT name, status, new_bom, current_bom FROM `tabBOM Update Log` where update_type='Replace BOM' and new_bom='{0}' order by name desc limit 1""".format(row.get("name")), as_dict=1)
		if bom_log:
			frappe.db.set_value("BOM", {"name":row.get("name")}, "update_status", bom_log[0].get("status"))
			frappe.db.commit()



@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_item_table(doctype, txt, searchfield, start, page_len):
	# return frappe.db.sql("""SELECT name from `tabCustom Item Attribute Value` where item_attribute = '{0}' and name like %(txt)s """.format(filters.get("attribute")),as_list=1,debug=1)
	return frappe.db.sql("""
		SELECT name
		FROM `tabItem` 
		WHERE  name LIKE %(txt)s
		ORDER BY name DESC
		LIMIT %(offset)s, %(limit)s
		""".format(searchfield), dict(
				txt="%{0}%".format(txt),
				offset=start,
				limit=page_len
			)
		)



@frappe.whitelist()
def update_defualt_uom_in_exploded_items():
	bom_list = frappe.db.sql("SELECT name from `tabBOM`",as_dict=1)
	if bom_list != []:
		for item in bom_list:
			bom_doc = frappe.get_doc("BOM",item.get("name"))
			if bom_doc.exploded_items:
				for row in bom_doc.exploded_items:
					stock_uom = frappe.db.get_value("Item",{'item_code':row.get('item_code')},'stock_uom')
					frappe.db.set_value("BOM Explosion Item",row.get('name'),'stock_uom',stock_uom)
					frappe.db.commit()