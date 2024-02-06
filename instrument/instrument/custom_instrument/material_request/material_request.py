from __future__ import unicode_literals
import frappe
import json
from frappe.utils import nowdate, cstr, flt, cint, now, getdate,get_datetime,time_diff_in_seconds,add_to_date,time_diff_in_seconds,add_days,today
from frappe import _, msgprint
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
def after_insert(doc,method):
	pdf_data=frappe.attach_print('Material Request',doc.name, print_format='Material Request Print')
		
	_file = frappe.get_doc({
	"doctype": "File",
	"file_name": pdf_data.get('fname'),
	"attached_to_doctype": "Material Request",
	"attached_to_name": doc.name,
	"is_private": 1,
	"content": pdf_data.get('fcontent')
	})
	_file.save()
def validate(doc,method):
	if doc.get("__islocal"):
		if doc.items:
			for item in doc.items:
				engineering_revision = frappe.db.get_value("Item",{'item_code':item.item_code},'engineering_revision') or frappe.db.get_value("Engineering Revision",{'item_code':item.item_code,'is_default':1,'is_active':1},'name')
				item.engineering_revision = engineering_revision
				if frappe.db.get_value("Item",{'item_code':item.item_code},'rfq_required'):
					item.rfq_required = 1
	else:
		frappe.db.sql("""DELETE from `tabFile` where attached_to_doctype='Material Request' and attached_to_name=%s""",
			(doc.name))
		pdf_data=frappe.attach_print('Material Request',doc.name, print_format='Material Request Print')
		
		_file = frappe.get_doc({
		"doctype": "File",
		"file_name": pdf_data.get('fname'),
		"attached_to_doctype": "Material Request",
		"attached_to_name": doc.name,
		"is_private": 1,
		"content": pdf_data.get('fcontent')
		})
		_file.save()

	if doc.items:
		item_data = doc.items
		item_dict = {(item.item_code,item.schedule_date):item.schedule_date for item in doc.items}
		final_data = []
		count = 0
		for item in item_dict:
			total = 0
			count = count + 1
			for info in doc.items:
				item_date_dict = (info.get('item_code'),info.get('schedule_date'))
				if item ==  item_date_dict:
					total = total + info.get('qty')
					item_info = info
			item_info.qty = total
			item_info.idx = count
			final_data.append(item_info)
		doc.items = ''
		for i in final_data:
			doc.append("items",i)

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

@frappe.whitelist()
def make_purchase_order(doc):
	try:
		doc = json.loads(doc)
		doc = frappe.get_doc("Material Request", doc.get("name"))
		item_list = []
		for d in doc.items:
			if not d.rfq_required:
				item_list.append(d.item_code)
		po_item_list = frappe.db.sql("""SELECT distinct poi.item_code from `tabPurchase Order Item` poi join `tabPurchase Order` po on po.name = poi.parent where poi.material_request = '{0}'""".format(doc.name),as_dict=1,debug=0)
		po_item_list = [poi.item_code for poi in po_item_list]
		for row in po_item_list:
			if row in item_list:
				item_list.remove(row)
		item_list = "', '".join(item_list)
		no_supplier = frappe.db.sql("""SELECT parent
			from `tabItem Default`
			where parent in ('{0}') and
			default_supplier IS NULL
			""".format(item_list),as_dict=1,debug=0)
		no_supplier = [item.parent for item in no_supplier]
		if no_supplier:
			frappe.throw("Please Add Default Supplier For Items {0}".format(no_supplier))
		supplier = frappe.db.sql("""SELECT distinct default_supplier
			from `tabItem Default`
			where parent in ('{0}') and
			default_supplier IS NOT NULL
			""".format(item_list),as_dict=1,debug=0)
		if supplier:
			supplier_list = [item.get("default_supplier") for item in supplier]
		print("================supplier_list",len(supplier_list),supplier_list)
		po_list = []
		for row in supplier_list:
			item_lists = frappe.db.sql("""SELECT distinct mri.* from `tabItem` i join `tabMaterial Request Item` mri on mri.item_code = i.item_code join `tabItem Default` id on id.parent = i.name where id.default_supplier = '{0}' and i.item_code in ('{1}') and mri.parent = '{2}' and (mri.qty-mri.received_qty) > 0""".format(row,item_list,doc.name),as_dict=1,debug=0)
			po = create_purchase_order(item_lists,row,doc,item_list)
			po_list.append(po)
		if po_list:
			po_list = ["""<a href="/app/Form/Purchase Order/{0}">{1}</a>""".format(m, m) \
				for m in po_list]
			msgprint(_("{0} created").format(comma_and(po_list)))
		else :
			msgprint(_("No purchase order created"))
		return po_list
	except Exception as e:
		traceback = frappe.get_traceback()
		frappe.log_error(
			title=_("Error while creating Purchase Order"),
			message=traceback,
		)
		raise e

def create_purchase_order(item_lists,supplier,doc,item_list):
	# update material request & material request item in purchase order item
	if item_lists:
		check_po = frappe.db.sql("""SELECT po.name from `tabPurchase Order` po join `tabPurchase Order Item` poi on poi.parent = po.name where poi.item_code in ('{0}') and po.supplier = '{1}' and po.docstatus in (0,2)""".format(item_list,supplier),as_dict=1)
		print("============check_po",check_po)
		if not check_po:
			po_doc = frappe.new_doc("Purchase Order")
			if po_doc:
				po_doc.supplier = supplier
				po_doc.schedule_date = doc.schedule_date
				for item in item_lists:
					item['material_request'] = doc.name
					item['material_request_item'] = item.name
					po_doc.append('items',item)
				po_doc.save()
				return po_doc.name
@frappe.whitelist()
def make_rfq(doc):
	doc = json.loads(doc)
	doc = frappe.get_doc("Material Request", doc.get("name"))
	item_list = []
	for d in doc.items:
		if d.rfq_required:
			item_list.append(d.item_code)

	supplier = frappe.db.sql("""SELECT distinct default_supplier_for_rfq
		from `tabItem Default`
		where parent in ({0}) and
		default_supplier_for_rfq IS NOT NULL
		""".format(', '.join(['%s']*len(item_list))),tuple(item_list),as_dict=1)
	supplier_list = [item.get("default_supplier_for_rfq") for item in supplier]
	rfq_list = []
	if supplier_list:
		for row in supplier_list:
			if item_list:
				if len(item_list) == 1:
					item_lists = frappe.db.sql("""SELECT distinct mri.* from `tabItem` i join `tabMaterial Request Item` mri on mri.item_code = i.item_code join `tabItem Default` id on id.parent = i.name where id.default_supplier_for_rfq = '{0}' and i.item_code = '{1}' and mri.parent = '{2}'""".format(row,item_list[0],doc.name),as_dict=1,debug=1)
					rfq = create_rfq(item_lists,row,doc)
					rfq_list.append(rfq)
				else:
					item_lists = frappe.db.sql("""SELECT distinct mri.* from `tabItem` i join `tabMaterial Request Item` mri on mri.item_code = i.item_code join `tabItem Default` id on id.parent = i.name where id.default_supplier_for_rfq = '{0}' and i.item_code in {1} and mri.parent = '{2}'""".format(row,tuple(item_list),doc.name),as_dict=1,debug=1)
					rfq = create_rfq(item_lists,row,doc)
					rfq_list.append(rfq)
	if rfq_list:
		rfq_list = ["""<a href="/app/Form/Request for Quotation/{0}">{1}</a>""".format(m, m) \
			for m in rfq_list]
		msgprint(_("{0} created").format(comma_and(rfq_list)))
	else :
		msgprint(_("No purchase order created"))
	return rfq_list
def create_rfq(item_lists,row,doc):
	if item_lists and row:
		suppler_for_rfq = frappe.db.sql("""SELECT srq.supplier from `tabSupplier` s join `tabSuppliers For RFQ` srq on srq.parent = s.name where s.name = '{0}' and srq.supplier IS NOT NULL""".format(row),as_dict=1,debug=1)
		suppler_for_rfq_list = [item.supplier for item in suppler_for_rfq]
		if suppler_for_rfq_list == []:
			suppler_for_rfq_list = []
			suppler_for_rfq_list.append(row)
		rfq_doc = frappe.new_doc("Request for Quotation")
		if rfq_doc:
			rfq_doc.schedule_date = doc.schedule_date
			if suppler_for_rfq_list:
				for item in suppler_for_rfq_list:
					rfq_doc.append('suppliers',{
						'supplier':item
						})
			for item in item_lists:
				item['material_request'] = doc.name
				rfq_doc.append('items',item)
			rfq_doc.message_for_supplier = "Please supply the specified items at the best possible rates"
			rfq_doc.save()
			return rfq_doc.name


def update_status_on_production_planning_with_lead_time(doc, method=None):
	if doc.production_planning_with_lead_time:
		for row in doc.items:
			frappe.db.set_value("Raw Materials Table", {'item':row.item_code, 'parent':doc.production_planning_with_lead_time}, "mr_status", doc.status)
			frappe.db.commit()


def on_trash(doc, method=None):
	if doc.production_planning_with_lead_time:
		for row in doc.items:
			frappe.db.set_value("Raw Materials Table", {'item':row.item_code, 'parent':doc.production_planning_with_lead_time}, "mr_status", "")
			frappe.db.commit()