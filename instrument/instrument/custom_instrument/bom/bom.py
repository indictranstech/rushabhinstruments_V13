from __future__ import unicode_literals
import frappe

def validate(doc,method):
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
			'sourced_by_supplier':row.get("sourced_by_supplier")
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
			'stock_uom':item.get("stock_uom"),
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