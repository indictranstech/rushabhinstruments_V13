# Copyright (c) 2021, instrument and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.core.doctype.version.version import get_diff
from frappe.model.mapper import get_mapped_doc
from frappe.utils import cint, cstr, flt, today

class MappedBOM(Document):
	def autoname(self):
		names = frappe.db.sql_list("""SELECT name from `tabMapped BOM` where item=%s""", self.item)

		if names:
			# name can be BOM/ITEM/001, BOM/ITEM/001-1, BOM-ITEM-001, BOM-ITEM-001-1

			# split by item
			names = [name.split(self.item, 1) for name in names]
			names = [d[-1][1:] for d in filter(lambda x: len(x) > 1 and x[-1], names)]

			# split by (-) if cancelled
			if names:
				names = [cint(name.split('-')[-1]) for name in names]
				idx = max(names) + 1
			else:
				idx = 1
		else:
			idx = 1

		name = 'Map-BOM-' + self.item + ('-%.3i' % idx)
		if frappe.db.exists("Mapped BOM", name):
			conflicting_bom = frappe.get_doc("Mapped BOM", name)

			if conflicting_bom.item != self.item:
				msg = (_("A Mapped BOM with name {0} already exists for item {1}.")
					.format(frappe.bold(name), frappe.bold(conflicting_bom.item)))

				frappe.throw(_("{0}{1} Did you rename the item? Please contact Administrator / Tech support")
					.format(msg, "<br>"))

		self.name = name
	def on_submit(self):
		self.manage_default_bom()
	def validate(self):
		self.set_bom_level()
	def on_cancel(self):
		frappe.db.set(self, "is_active", 0)
		frappe.db.set(self, "is_default", 0)
		self.manage_default_bom()
	def on_update_after_submit(self):
		self.manage_default_bom()
	def set_bom_level(self, update=False):
		levels = []

		self.bom_level = 0
		for row in self.items:
			if row.mapped_bom:
				levels.append(frappe.get_cached_value("Mapped BOM", row.mapped_bom, "bom_level") or 0)

		if levels:
			self.bom_level = max(levels) + 1

		if update:
			self.db_set("bom_level", self.bom_level)
	def manage_default_bom(self):
		""" Uncheck others if current one is selected as default or
			check the current one as default if it the only doc for the selected item
		"""
		if self.is_default and self.is_active:
			frappe.db.sql("""UPDATE `tabMapped BOM`
				set is_default=0
				where item = %s and name !=%s""",
				(self.item,self.name))
		elif not frappe.db.exists(dict(doctype='Mapped BOM',item=self.item,is_default=1)) \
			and self.is_active:
			frappe.db.set(self, "is_default", 1)
		else:
			frappe.db.set(self, "is_default", 0)

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_mapped_bom(doctype, txt, searchfield, start, page_len, filters):
	return frappe.db.sql(""" SELECT name FROM `tabMapped BOM` where item = '{0}' """.format(filters.get("item_code")))	

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_bom(doctype, txt, searchfield, start, page_len, filters):
	return frappe.db.sql(""" SELECT name FROM `tabBOM` where item = '{0}' """.format(filters.get("item_code")))	

@frappe.whitelist()
def get_default_bom(item_code):
	item_doc = frappe.get_doc("Item",item_code)
	if item_doc.is_map_item:
		bom_no = frappe.db.get_value("Mapped BOM",{'item':item_code,'is_default' :1,'is_active' : 1},'name')
		return bom_no,'Yes'
	else:
		bom_no = frappe.db.get_value("BOM",{'item':item_code,'is_default' :1,'is_active' : 1},'name')
		return bom_no,'No'


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_items(doctype, txt, searchfield, start, page_len, filters):
	return frappe.db.sql(""" SELECT name FROM `tabItem` where is_map_item = '{0}' """.format(filters.get("is_map_item")))
