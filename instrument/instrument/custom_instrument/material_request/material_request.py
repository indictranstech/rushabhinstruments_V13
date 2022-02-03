from __future__ import unicode_literals
import frappe
import json

def validate(doc,method):
	if doc.get("__islocal"):
		if doc.items:
			for item in doc.items:
				engineering_revision = frappe.db.get_value("Item",{'item_code':item.item_code},'engineering_revision') or frappe.db.get_value("Engineering Revision",{'item_code':item.item_code,'is_default':1,'is_active':1},'name')
				item.engineering_revision = engineering_revision
				if frappe.db.get_value("Item",{'item_code':item.item_code},'rfq_required'):
					item.rfq_required = 1

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_default_supplier_query(doctype, txt, searchfield, start, page_len, filters):
	doc = frappe.get_doc("Material Request", filters.get("doc"))
	item_list = []
	for d in doc.items:
		if not d.rfq_required:
			item_list.append(d.item_code)

	return frappe.db.sql("""SELECT default_supplier
		from `tabItem Default`
		where parent in ({0}) and
		default_supplier IS NOT NULL
		""".format(', '.join(['%s']*len(item_list))),tuple(item_list))
