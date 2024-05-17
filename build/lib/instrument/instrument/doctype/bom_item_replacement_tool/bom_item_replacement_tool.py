# Copyright (c) 2021, instrument and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from erpnext.stock.doctype.item.item import get_item_defaults
from frappe import _
from instrument.instrument.doctype.mapped_bom.mapped_bom import propogate_update_to_descendent
from instrument.instrument.doctype.item_mapping.item_mapping import propogate_updates_to_affected_boms
class BOMItemReplacementTool(Document):
	@frappe.whitelist()
	def replace(self):
		frappe.msgprint(_("Queued for replacing the BOM.Please Wait.. It may take a few minutes."))
		self.status = 'In Process'
		self.update_boms()
		self.update_mapped_boms()
		self.update_item_mapping()
		self.status = 'Completed'
		return True
	def update_item_mapping(self):
		item_mapping_list = frappe.db.sql("""SELECT name from `tabItem Mapping` where item_code = '{0}'""".format(self.old_item_number),as_dict=1)
		item_mapping_list = [i.name for i in item_mapping_list]
		if len(item_mapping_list) > 0:
			for i in item_mapping_list:
				i_doc = frappe.get_doc("Item Mapping",i)
				if i_doc:
					i_doc.item_code = self.new_item_number
				i_doc.save()
				# propogate_updates_to_affected_boms(i_doc.name)
		# return frappe.db.sql("""UPDATE `tabItem Mapping` set item_code = '{0}' where item_code = '{1}'""".format(self.new_item_number,self.old_item_number),debug=1)
	def update_boms(self):
		bom_list = self.get_all_boms()
		for bom in bom_list:
			old_bom = frappe.get_doc("BOM",bom.get("name"))
			default_company = frappe.db.get_single_value("Global Defaults",'default_company')
			item_details = get_item_defaults(self.new_item_number, default_company)
			new_bom = frappe.copy_doc(old_bom, ignore_no_copy=False)
			new_bom.old_reference_bom = bom.get('name')
			item_list = list()
			for row in old_bom.items:
				if row.item_code == self.old_item_number:
					row.item_code = self.new_item_number
					row.item_name = item_details.get('item_name')
					row.uom = item_details.get('stock_uom')
					row.stock_uom = item_details.get('stock_uom')
					row.bom_no = self.new_bom
					item_list.append(row)
				else:
					item_list.append(row)
			new_bom.items = ''
			for item in item_list:
				new_bom.append('items',item)
			if not old_bom.is_active:
				new_bom.is_active = 0
			new_bom.save()
			new_bom.submit()
			args ={
					"current_bom": new_bom.name,
					"new_bom": new_bom.old_reference_bom
				}
			frappe.enqueue("erpnext.manufacturing.doctype.bom_update_tool.bom_update_tool.replace_bom", args=args, timeout=40000)
			frappe.msgprint("New Version Created For BOM <b>{0}</b>".format(bom.get("name")))
	def get_all_boms(self):
		if self.old_bom_number:
			bom_list = frappe.db.sql("""SELECT distinct b.name from `tabBOM` b join `tabBOM Item` bi on bi.parent = b.name where bi.item_code = '{0}' and bi.bom_no = '{1}' and b.docstatus = 1 order by b.bom_level asc""".format(self.old_item_number,self.old_bom_number),as_dict=1)
		else:
			bom_list = frappe.db.sql("""SELECT distinct b.name from `tabBOM` b join `tabBOM Item` bi on bi.parent = b.name where bi.item_code = '{0}' and b.docstatus = 1 order by b.bom_level asc""".format(self.old_item_number),as_dict=1)
		return bom_list
	def update_mapped_boms(self):
		bom_list = self.get_all_mapped_boms()
		for bom in bom_list:
			old_bom = frappe.get_doc("Mapped BOM",bom.get("name"))
			default_company = frappe.db.get_single_value("Global Defaults",'default_company')
			item_details = get_item_defaults(self.new_item_number, default_company)
			new_bom = frappe.copy_doc(old_bom, ignore_no_copy=False)
			new_bom.old_reference_bom = bom.get('name')
			item_list = list()
			for row in old_bom.items:
				if row.item_code == self.old_item_number:
					row.item_code = self.new_item_number
					row.item_name = item_details.get('item_name')
					row.uom = item_details.get('stock_uom')
					row.stock_uom = item_details.get('stock_uom')
					row.bom_no = self.new_bom
					item_list.append(row)
				else:
					item_list.append(row)
			new_bom.items = ''
			for item in item_list:
				new_bom.append('items',item)
			if not old_bom.is_active:
				new_bom.is_active = 0
			new_bom.save()
			new_bom.submit()
			args ={
					"current_bom": new_bom.name,
					"new_bom": new_bom.old_reference_bom
				}
			frappe.enqueue("instrument.instrument.doctype.mapped_bom.mapped_bom.replace_bom", args=args, timeout=40000)
			propogate_update_to_descendent(new_bom.name)

			frappe.msgprint("New Version Created For Mapped BOM <b>{0}</b>".format(bom.get("name")))
	def get_all_mapped_boms(self):
		mapped_bom_list = frappe.db.sql("""SELECT distinct b.name from `tabMapped BOM` b join `tabMapped BOM Item` bi on bi.parent = b.name where bi.item_code = '{0}' and b.docstatus = 1 order by b.bom_level asc""".format(self.old_item_number),as_dict=1)
		return mapped_bom_list

@frappe.whitelist()
def get_default_bom(item):
	bom = frappe.db.get_value("BOM",{'item':item,'is_active':1,'is_default':1,'docstatus':1},'name')
	return bom
