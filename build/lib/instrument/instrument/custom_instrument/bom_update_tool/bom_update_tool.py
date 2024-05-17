# Copyright (c) 2017, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import json

import click
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cstr, flt
from six import string_types
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
	now
)
from erpnext.manufacturing.doctype.bom_update_log.bom_updation_utils import (
	get_leaf_boms,
	get_next_higher_level_boms,
	handle_exception,
	replace_bom,
	set_values_in_log,
	get_ancestor_boms
)
# from erpnext.manufacturing.doctype.bom.bom import get_boms_in_bottom_up_order

# def replacee_bom(self):
# 	self.validate_bom()

# 	unit_cost = get_new_bom_unit_cost(self.new_bom)
# 	self.update_new_bom(unit_cost)

# 	frappe.cache().delete_key('bom_children')
# 	bom_list = self.get_parent_boms(self.new_bom)

# 	with click.progressbar(bom_list) as bom_list:
# 		pass
# 	for bom in bom_list:
# 		try:
# 			bom_obj = frappe.get_cached_doc('BOM', bom)
# 			# this is only used for versioning and we do not want
# 			# to make separate db calls by using load_doc_before_save
# 			# which proves to be expensive while doing bulk replace
# 			bom_obj._doc_before_save = bom_obj
# 			bom_obj.update_new_bom(self.current_bom, self.new_bom, unit_cost)
# 			bom_obj.update_exploded_items()
# 			bom_obj.calculate_cost()
# 			bom_obj.update_parent_cost()
# 			bom_obj.db_update()
# 			if bom_obj.meta.get('track_changes') and not bom_obj.flags.ignore_version:
# 				bom_obj.save_version()
# 		except Exception:
# 			frappe.log_error(frappe.get_traceback())
# 	frappe.db.set_value("BOM",{'name':self.new_bom},'update_status','Completed')
# 	frappe.db.commit()
# def validate_bom(self):
# 	if cstr(self.current_bom) == cstr(self.new_bom):
# 		frappe.throw(_("Current BOM and New BOM can not be same"))

# 	if frappe.db.get_value("BOM", self.current_bom, "item") \
# 		!= frappe.db.get_value("BOM", self.new_bom, "item"):
# 			frappe.throw(_("The selected BOMs are not for the same item"))

# def update_new_bom(self, unit_cost):
# 	frappe.db.sql("""update `tabBOM Item` set bom_no=%s,
# 		rate=%s, amount=stock_qty*%s where bom_no = %s and docstatus < 2 and parenttype='BOM'""",
# 		(self.new_bom, unit_cost, unit_cost, self.current_bom))

# def get_parent_boms(self, bom, bom_list=None):
# 	if bom_list is None:
# 		bom_list = []
# 	data = frappe.db.sql("""SELECT DISTINCT parent FROM `tabBOM Item`
# 		WHERE bom_no = %s AND docstatus < 2 AND parenttype='BOM'""", bom)

# 	for d in data:
# 		if self.new_bom == d[0]:
# 			frappe.throw(_("BOM recursion: {0} cannot be child of {1}").format(bom, self.new_bom))

# 		bom_list.append(d[0])
# 		self.get_parent_boms(d[0], bom_list)

# 	return list(set(bom_list))

# def get_new_bom_unit_cost(bom):
# 	new_bom_unitcost = frappe.db.sql("""SELECT `total_cost`/`quantity`
# 		FROM `tabBOM` WHERE name = %s""", bom)

# 	return flt(new_bom_unitcost[0][0]) if new_bom_unitcost else 0

# @frappe.whitelist()
# def enqueue_replace_bom(args):
# 	if isinstance(args, string_types):
# 		args = json.loads(args)
# 		bom_doc = frappe.get_doc("BOM",args.get("new_bom"))
# 		bom_doc.update_status =  'In Process'
# 		# bom_doc.save()
# 		# frappe.db.set_value("BOM",{'name':args.get("current_bom")},'update_status','In Process')
# 		# frappe.db.commit()
# 	frappe.msgprint(_("Queued for replacing the BOM. It may take a few minutes."))
# 	custom_replace_bom(args)

# 	# frappe.enqueue("instrument.instrument.custom_instrument.bom_update_tool.bom_update_tool.custom_replace_bom", args=args, timeout=40000)
	

# @frappe.whitelist()
# def enqueue_update_cost():
# 	frappe.enqueue("instrument.instrument.custom_instrument.bom_update_tool.bom_update_tool.update_cost", timeout=40000)
# 	frappe.msgprint(_("Queued for updating latest price in all Bill of Materials. It may take a few minutes."))

# def update_latest_price_in_all_boms():
# 	if frappe.db.get_single_value("Manufacturing Settings", "update_bom_costs_automatically"):
# 		update_cost()

# def custom_replace_bom(args):
# 	frappe.msgprint("==========Working=========")
# 	frappe.db.auto_commit_on_many_writes = 1
# 	args = frappe._dict(args)

# 	# doc.replace_bom()


# 	doc = frappe.get_doc("BOM Update Tool")
# 	doc.current_bom = args.current_bom
# 	doc.new_bom = args.new_bom
# 	replacee_bom(doc)
# 	frappe.db.auto_commit_on_many_writes = 0


# def update_cost():
# 	frappe.db.auto_commit_on_many_writes = 1
# 	bom_list = get_boms_in_bottom_up_order()
# 	for bom in bom_list:
# 		frappe.get_doc("BOM", bom).update_cost(update_parent=False, from_child_bom=True)

# 	frappe.db.auto_commit_on_many_writes = 0

@frappe.whitelist()
def update_mapped_bom_item(current_bom, new_bom,current_doc):
	mapped_bom_list = frappe.db.sql("""SELECT m.name from `tabMapped BOM`m join `tabMapped BOM Item`mi on mi.parent = m.name where mi.bom_no = '{0}'""".format(current_bom),as_dict=1,debug=1)
	mapped_bom_list = [i.name for i in mapped_bom_list]
	frappe.db.sql("""update `tabMapped BOM Item` set bom_no=%s where bom_no = %s and parenttype='Mapped BOM'""",
		(new_bom, current_bom), debug=1)
	if len(mapped_bom_list) > 0:
		add_update_comment(current_bom,new_bom,current_doc,mapped_bom_list)
	bct_doc_list = frappe.db.sql("""SELECT b.name from `tabBOM Creation Tool`b join `tabReview Item Mapping`ri on ri.parent = b.name where ri.standard_bom = '{0}'""".format(current_bom),as_dict=1,debug=1)
	bct_doc_list = [i.name for i in bct_doc_list]
	frappe.db.sql("""update `tabReview Item Mapping` set standard_bom=%s where standard_bom = %s and parenttype='BOM Creation Tool'""",
		(new_bom, current_bom), debug=1)
	if len(bct_doc_list) > 0:
		add_update_comment_for_bct(current_bom,new_bom,current_doc,bct_doc_list)
	boms = {'current_bom':current_bom,'new_bom':new_bom}
	bom_list = get_ancestor_boms(new_bom)
	print("----------bom",bom_list)

@frappe.whitelist()
def add_update_comment(current_bom,new_bom,current_doc,mapped_bom_list):
	for row in mapped_bom_list:
		mapbom_doc = frappe.get_doc("Mapped BOM", row)
		msg = "'{0}' updated BOM No. from {1} to {2} by Update Reference From document '{3}' on {4}".format(frappe.session.user, current_bom,new_bom ,current_doc, now())
		mapbom_doc.add_comment('Comment', msg)
@frappe.whitelist()
def add_update_comment_for_bct(current_bom,new_bom,current_doc,bct_doc_list):
	for row in bct_doc_list:
		bct_doc = frappe.get_doc("BOM Creation Tool", row)
		msg = "'{0}' updated Standard BOM No. from {1} to {2} by Update Reference From document '{3}' on {4}".format(frappe.session.user, current_bom,new_bom ,current_doc, now())
		bct_doc.add_comment('Comment', msg)

	# # frappe.db.set_value("BOM", new_bom, "update_status", "Completed")

	# frappe.db.commit()
