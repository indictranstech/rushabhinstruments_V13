# Copyright (c) 2021, instrument and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.core.doctype.version.version import get_diff
from frappe.model.mapper import get_mapped_doc
from frappe.utils import cint, cstr, flt, today
from six import string_types
import json

import click

import functools
from collections import deque
from operator import itemgetter
from typing import List


from frappe.website.website_generator import WebsiteGenerator

import erpnext
from erpnext.setup.utils import get_exchange_rate
from erpnext.stock.doctype.item.item import get_item_details
from erpnext.stock.get_item_details import get_conversion_factor, get_price_list_rate
from instrument.instrument.doctype.bom_creation_tool.bom_creation_tool import get_map_item_attributes

class MappedBOMTree:
	"""Full tree representation of a BOM"""

	# specifying the attributes to save resources
	# ref: https://docs.python.org/3/reference/datamodel.html#slots
	__slots__ = ["name", "child_items", "is_bom", "item_code", "exploded_qty", "qty"]

	def __init__(self, name: str, is_bom: bool = True, exploded_qty: float = 1.0, qty: float = 1) -> None:
		self.name = name  # name of node, BOM number if is_bom else item_code
		self.child_items: List["MappedBOMTree"] = []  # list of child items
		self.is_bom = is_bom   # true if the node is a BOM and not a leaf item
		self.item_code: str = None  # item_code associated with node
		self.qty = qty  # required unit quantity to make one unit of parent item.
		self.exploded_qty = exploded_qty  # total exploded qty required for making root of tree.
		if not self.is_bom:
			self.item_code = self.name
		else:
			self.__create_tree()

	def __create_tree(self):
		bom = frappe.get_cached_doc("Mapped BOM", self.name)
		self.item_code = bom.item

		for item in bom.get("items", []):
			qty = item.qty / bom.quantity  # quantity per unit
			exploded_qty = self.exploded_qty * qty
			if item.bom_no:
				child = MappedBOMTree(item.bom_no, exploded_qty=exploded_qty, qty=qty)
				self.child_items.append(child)
			else:
				self.child_items.append(
					MappedBOMTree(item.item_code, is_bom=False, exploded_qty=exploded_qty, qty=qty)
				)

	def level_order_traversal(self) -> List["MappedBOMTree"]:
		"""Get level order traversal of tree.
		E.g. for following tree the traversal will return list of nodes in order from top to bottom.
		BOM:
			- SubAssy1
				- item1
				- item2
			- SubAssy2
				- item3
			- item4

		returns = [SubAssy1, item1, item2, SubAssy2, item3, item4]
		"""
		traversal = []
		q = deque()
		q.append(self)

		while q:
			node = q.popleft()

			for child in node.child_items:
				traversal.append(child)
				q.append(child)

		return traversal

	def __str__(self) -> str:
		return (
			f"{self.item_code}{' - ' + self.name if self.is_bom else ''} qty(per unit): {self.qty}"
			f" exploded_qty: {self.exploded_qty}"
		)

	def __repr__(self, level: int = 0) -> str:
		rep = "┃  " * (level - 1) + "┣━ " * (level > 0) + str(self) + "\n"
		for child in self.child_items:
			rep += child.__repr__(level=level + 1)
		return rep

class MappedBOM(WebsiteGenerator):
	website = frappe._dict(
		# page_title_field = "item_name",
		condition_field = "show_in_website",
		template = "mapped_bom.html"
	)
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
		self.check_propogation()
	def validate(self):
		self.route = frappe.scrub(self.name).replace('_', '-')
		if self.get("__islocal"):
			self.propogate_to_descendent_bom = 0
			self.check_propogation_to_descendent_bom = 0
		self.route = frappe.scrub(self.name).replace('_', '-')
		
		if not self.company:
			frappe.throw(_("Please select a Company first."), title=_("Mandatory"))
		self.clear_operations()
		self.validate_main_item()
		self.validate_currency()
		self.set_conversion_rate()
		self.set_plc_conversion_rate()
		self.validate_uom_is_interger()
		self.set_bom_material_details()
		self.set_bom_scrap_items_detail()
		self.validate_materials()
		self.set_routing_operations()
		self.validate_operations()
		self.calculate_cost()
		self.update_stock_qty()
		self.validate_scrap_items()
		self.update_cost(update_parent=False, from_child_bom=True, update_hour_rate = False, save=False)
		self.set_bom_level()
		self.check_deleted_items()

	def check_deleted_items(self):
		if self.items and self.old_reference_bom:
			old_bom_data = get_bom_data(self.old_reference_bom)
			item_dict = {row.get("item_code"):row for row in old_bom_data}
			new_item_dict = {row.item_code:row for row in self.items}
			deleted_item_list = list()
			for item in item_dict:
				if item not in new_item_dict:
					deleted_item_list.append(item_dict.get(item))
			if len(deleted_item_list) > 0:
				self.deleted_items = ''
				for row in deleted_item_list:
					self.append('deleted_items',{
						'item_code':row.get("item_code"),
						'item_name':row.get("item_name"),
						'is_map_item':row.get("is_map_item")
						})

	def clear_operations(self):
		if not self.with_operations:
			self.set('operations', [])

	def validate_main_item(self):
		""" Validate main FG item"""
		item = self.get_item_det(self.item)
		if not item:
			frappe.throw(_("Item {0} does not exist in the system or has expired").format(self.item))
		else:
			ret = frappe.db.get_value("Item", self.item, ["description", "stock_uom", "item_name"])
			self.description = ret[0]
			self.uom = ret[1]
			self.item_name= ret[2]

		if not self.quantity:
			frappe.throw(_("Quantity should be greater than 0"))
	def get_item_det(self, item_code):
		item = get_item_details(item_code)

		if not item:
			frappe.throw(_("Item: {0} does not exist in the system").format(item_code))

		return item
	def validate_currency(self):
		if self.rm_cost_as_per == 'Price List':
			price_list_currency = frappe.db.get_value('Price List', self.buying_price_list, 'currency')
			if price_list_currency not in (self.currency, self.company_currency()):
				frappe.throw(_("Currency of the price list {0} must be {1} or {2}")
					.format(self.buying_price_list, self.currency, self.company_currency()))

	def set_conversion_rate(self):
		if self.currency == self.company_currency():
			self.conversion_rate = 1
		elif self.conversion_rate == 1 or flt(self.conversion_rate) <= 0:
			self.conversion_rate = get_exchange_rate(self.currency, self.company_currency(), args="for_buying")

	def set_plc_conversion_rate(self):
		if self.rm_cost_as_per in ["Valuation Rate", "Last Purchase Rate"]:
			self.plc_conversion_rate = 1
		elif not self.plc_conversion_rate and self.price_list_currency:
			self.plc_conversion_rate = get_exchange_rate(self.price_list_currency,
				self.company_currency(), args="for_buying")
	def validate_uom_is_interger(self):
		from erpnext.utilities.transaction_base import validate_uom_is_integer
		validate_uom_is_integer(self, "uom", "qty", "Mapped BOM Item")
		validate_uom_is_integer(self, "stock_uom", "stock_qty", "Mapped BOM Item")

	def validate_bom_currency(self, item):
		if item.get('mapped_bom') and frappe.db.get_value('Mapped BOM', item.get('mapped_bom'), 'currency') != self.currency:
			frappe.throw(_("Row {0}: Currency of the Mapped BOM #{1} should be equal to the selected currency {2}")
				.format(item.idx, item.mapped_bom, self.currency))
	def validate_materials(self):
		""" Validate raw material entries """

		if not self.get('items'):
			frappe.throw(_("Raw Materials cannot be blank."))

		check_list = []
		for m in self.get('items'):
			if m.mapped_bom and m.is_map_item:
				validate_bom_no(m.item_code, m.mapped_bom)
			if flt(m.qty) <= 0:
				frappe.throw(_("Quantity required for Item {0} in row {1}").format(m.item_code, m.idx))
			check_list.append(m)
	def set_routing_operations(self):
		if self.routing and self.with_operations and not self.operations:
			self.get_routing()
	@frappe.whitelist()
	def get_routing(self):
		if self.routing:
			self.set("operations", [])
			fields = ["sequence_id", "operation", "workstation", "description",
				"time_in_mins", "batch_size", "operating_cost", "idx", "hour_rate"]

			for row in frappe.get_all("BOM Operation", fields = fields,
				filters = {'parenttype': 'Routing', 'parent': self.routing}, order_by="sequence_id, idx"):
				child = self.append('operations', row)
				child.hour_rate = flt(row.hour_rate / self.conversion_rate, 2)
	def validate_operations(self):
		if self.with_operations and not self.get('operations') and self.docstatus == 1:
			frappe.throw(_("Operations cannot be left blank"))

		if self.with_operations:
			for d in self.operations:
				if not d.description:
					d.description = frappe.db.get_value('Operation', d.operation, 'description')
				if not d.batch_size or d.batch_size <= 0:
					d.batch_size = 1
	def calculate_cost(self, update_hour_rate = False):
		"""Calculate bom totals"""
		self.calculate_op_cost(update_hour_rate)
		self.calculate_rm_cost()
		self.calculate_sm_cost()
		self.total_cost = self.operating_cost + self.raw_material_cost - self.scrap_material_cost
		self.base_total_cost = self.base_operating_cost + self.base_raw_material_cost - self.base_scrap_material_cost
	def calculate_op_cost(self, update_hour_rate = False):
		"""Update workstation rate and calculates totals"""
		self.operating_cost = 0
		self.base_operating_cost = 0
		for d in self.get('operations'):
			if d.workstation:
				self.update_rate_and_time(d, update_hour_rate)

			operating_cost = d.operating_cost
			base_operating_cost = d.base_operating_cost
			if d.set_cost_based_on_bom_qty:
				operating_cost = flt(d.cost_per_unit) * flt(self.quantity)
				base_operating_cost = flt(d.base_cost_per_unit) * flt(self.quantity)

			self.operating_cost += flt(operating_cost)
			self.base_operating_cost += flt(base_operating_cost)
	def calculate_rm_cost(self):
		"""Fetch RM rate as per today's valuation rate and calculate totals"""
		total_rm_cost = 0
		base_total_rm_cost = 0

		for d in self.get('items'):
			d.base_rate = flt(d.rate) * flt(self.conversion_rate)
			d.amount = flt(d.rate, d.precision("rate")) * flt(d.qty, d.precision("qty"))
			d.base_amount = d.amount * flt(self.conversion_rate)
			d.qty_consumed_per_unit = flt(d.stock_qty, d.precision("stock_qty")) \
				/ flt(self.quantity, self.precision("quantity"))

			total_rm_cost += d.amount
			base_total_rm_cost += d.base_amount

		self.raw_material_cost = total_rm_cost
		self.base_raw_material_cost = base_total_rm_cost
	def calculate_sm_cost(self):
		"""Fetch RM rate as per today's valuation rate and calculate totals"""
		total_sm_cost = 0
		base_total_sm_cost = 0

		for d in self.get('scrap_items'):
			d.base_rate = flt(d.rate, d.precision("rate")) * flt(self.conversion_rate, self.precision("conversion_rate"))
			d.amount = flt(d.rate, d.precision("rate")) * flt(d.stock_qty, d.precision("stock_qty"))
			d.base_amount = flt(d.amount, d.precision("amount")) * flt(self.conversion_rate, self.precision("conversion_rate"))
			total_sm_cost += d.amount
			base_total_sm_cost += d.base_amount

		self.scrap_material_cost = total_sm_cost
		self.base_scrap_material_cost = base_total_sm_cost
	def validate_scrap_items(self):
		for item in self.scrap_items:
			msg = ""
			if item.item_code == self.item and not item.is_process_loss:
				msg = _('Scrap/Loss Item: {0} should have Is Process Loss checked as it is the same as the item to be manufactured or repacked.') \
					.format(frappe.bold(item.item_code))
			elif item.item_code != self.item and item.is_process_loss:
				msg = _('Scrap/Loss Item: {0} should not have Is Process Loss checked as it is different from  the item to be manufactured or repacked') \
					.format(frappe.bold(item.item_code))

			must_be_whole_number = frappe.get_value("UOM", item.stock_uom, "must_be_whole_number")
			if item.is_process_loss and must_be_whole_number:
				msg = _("Item: {0} with Stock UOM: {1} cannot be a Scrap/Loss Item as {1} is a whole UOM.") \
					.format(frappe.bold(item.item_code), frappe.bold(item.stock_uom))

			if item.is_process_loss and (item.stock_qty >= self.quantity):
				msg = _("Scrap/Loss Item: {0} should have Qty less than finished goods Quantity.") \
					.format(frappe.bold(item.item_code))

			if item.is_process_loss and (item.rate > 0):
				msg = _("Scrap/Loss Item: {0} should have Rate set to 0 because Is Process Loss is checked.") \
					.format(frappe.bold(item.item_code))

			if msg:
				frappe.throw(msg, title=_("Note"))
	@frappe.whitelist()
	def update_cost(self, update_parent=True, from_child_bom=False, update_hour_rate = True, save=True):
		if self.docstatus == 2:
			return

		existing_bom_cost = self.total_cost

		for d in self.get("items"):
			rate = self.get_rm_rate({
				"company": self.company,
				"item_code": d.item_code,
				"mapped_bom": d.mapped_bom if d.mapped_bom else '',
				"qty": d.qty,
				"uom": d.uom,
				"stock_uom": d.stock_uom,
				"conversion_factor": d.conversion_factor,
				"sourced_by_supplier": d.sourced_by_supplier
			})

			if rate:
				d.rate = rate
			d.amount = flt(d.rate) * flt(d.qty)
			d.base_rate = flt(d.rate) * flt(self.conversion_rate)
			d.base_amount = flt(d.amount) * flt(self.conversion_rate)

			if save:
				d.db_update()

		if self.docstatus == 1:
			self.flags.ignore_validate_update_after_submit = True
			self.calculate_cost(update_hour_rate)
		if save:
			self.db_update()

		self.update_exploded_items(save=save)

		# update parent BOMs
		if self.total_cost != existing_bom_cost and update_parent:
			parent_boms = frappe.db.sql_list("""SELECT distinct parent from `tabMapped BOM Item`
				where mapped_bom = %s and docstatus=1 and parenttype='Mapped BOM'""", self.name)

			for bom in parent_boms:
				frappe.get_doc("Mapped BOM", bom).update_cost(from_child_bom=True)

		if not from_child_bom:
			frappe.msgprint(_("Cost Updated"), alert=True)
	def update_stock_qty(self):
		for m in self.get('items'):
			if not m.conversion_factor:
				m.conversion_factor = flt(get_conversion_factor(m.item_code, m.uom)['conversion_factor'])
			if m.uom and m.qty:
				m.stock_qty = flt(m.conversion_factor)*flt(m.qty)
			if not m.uom and m.stock_uom:
				m.uom = m.stock_uom
				m.qty = m.stock_qty
	def set_bom_material_details(self):
		for item in self.get("items"):
			self.validate_bom_currency(item)

			ret = self.get_bom_material_detail({
				"company": self.company,
				"item_code": item.item_code,
				"item_name": item.item_name,
				"mapped_bom": item.mapped_bom,
				"stock_qty": item.stock_qty,
				"include_item_in_manufacturing": item.include_item_in_manufacturing,
				"qty": item.qty,
				"uom": item.uom,
				"stock_uom": item.stock_uom,
				"conversion_factor": item.conversion_factor,
				"sourced_by_supplier": item.sourced_by_supplier
			})
			for r in ret:
				if not item.get(r):
					item.set(r, ret[r])
	def set_bom_scrap_items_detail(self):
		for item in self.get("scrap_items"):
			args = {
				"item_code": item.item_code,
				"company": self.company,
				"scrap_items": True,
				"mapped_bom": '',
			}
			ret = self.get_bom_material_detail(args)
			for key, value in ret.items():
				if item.get(key) is None:
					item.set(key, value)

	@frappe.whitelist()
	def get_bom_material_detail(self, args=None):
		""" Get raw material details like uom, desc and rate"""
		if not args:
			args = frappe.form_dict.get('args')

		if isinstance(args, str):
			import json
			args = json.loads(args)

		item = self.get_item_det(args['item_code'])

		# args['mapped_bom'] = args['mapped_bom'] or item and cstr(item['default_bom']) or ''
		args['mapped_bom'] = args['mapped_bom']
		args['transfer_for_manufacture'] = (cstr(args.get('include_item_in_manufacturing', '')) or
			item and item.include_item_in_manufacturing or 0)
		args.update(item)

		rate = self.get_rm_rate(args)
		ret_item = {
			 'item_name'	: item and args['item_name'] or '',
			 'description'  : item and args['description'] or '',
			 'image'		: item and args['image'] or '',
			 'stock_uom'	: item and args['stock_uom'] or '',
			 'uom'			: item and args['stock_uom'] or '',
 			 'conversion_factor': 1,
			 'mapped_bom'		: args['mapped_bom'],
			 'rate'			: rate,
			 'qty'			: args.get("qty") or args.get("stock_qty") or 1,
			 'stock_qty'	: args.get("qty") or args.get("stock_qty") or 1,
			 'base_rate'	: flt(rate) * (flt(self.conversion_rate) or 1),
			 'include_item_in_manufacturing': cint(args.get('transfer_for_manufacture')),
			 'sourced_by_supplier'		: args.get('sourced_by_supplier', 0)
		}

		return ret_item
	def get_rm_rate(self, arg):
		"""	Get raw material rate as per selected method, if bom exists takes bom cost """
		rate = 0
		if not self.rm_cost_as_per:
			self.rm_cost_as_per = "Valuation Rate"

		if arg.get('scrap_items'):
			rate = get_valuation_rate(arg)
		elif arg:
			#Customer Provided parts and Supplier sourced parts will have zero rate
			if not frappe.db.get_value('Item', arg["item_code"], 'is_customer_provided_item') and not arg.get('sourced_by_supplier'):
				if arg.get('mapped_bom') and self.set_rate_of_sub_assembly_item_based_on_bom:
					rate = flt(self.get_bom_unitcost(arg['mapped_bom'])) * (arg.get("conversion_factor") or 1)
				else:
					rate = get_bom_item_rate(arg, self)

					if not rate:
						if self.rm_cost_as_per == "Price List":
							frappe.msgprint(_("Price not found for item {0} in price list {1}")
								.format(arg["item_code"], self.buying_price_list), alert=True)
						else:
							frappe.msgprint(_("{0} not found for item {1}")
								.format(self.rm_cost_as_per, arg["item_code"]), alert=True)
		return flt(rate) * flt(self.plc_conversion_rate or 1) / (self.conversion_rate or 1)
	def get_bom_unitcost(self, bom_no):
		bom = frappe.db.sql("""SELECT name, base_total_cost/quantity as unit_cost from `tabMapped BOM`
			where is_active = 1 and name = %s""", bom_no, as_dict=1)
		return bom and bom[0]['unit_cost'] or 0
	def on_cancel(self):
		frappe.db.set(self, "is_active", 0)
		frappe.db.set(self, "is_default", 0)
		self.manage_default_bom()
	def on_update_after_submit(self):
		self.manage_default_bom()
		self.check_propogation()
	def set_bom_level(self, update=False):
		levels = []

		self.bom_level = 0
		for row in self.items:
			if row.mapped_bom and row.is_map_item:
				levels.append(frappe.get_cached_value("Mapped BOM", row.mapped_bom, "bom_level") or 0)

		if levels:
			self.bom_level = max(levels) + 1

		if update:
			self.db_set("bom_level", self.bom_level)
	def manage_default_bom(self):
		# """ Uncheck others if current one is selected as default or
		# 	check the current one as default if it the only bom for the selected item,
		# 	update default bom in item master
		# """
		# if self.is_default and self.is_active:
		# 	from frappe.model.utils import set_default
		# 	set_default(self, "item")
		# 	item = frappe.get_doc("Item", self.item)
		# 	if item.default_bom != self.name:
		# 		frappe.db.set_value('Item', self.item, 'default_bom', self.name)
		# elif not frappe.db.exists(dict(doctype='BOM', docstatus=1, item=self.item, is_default=1)) \
		# 	and self.is_active:
		# 	frappe.db.set(self, "is_default", 1)
		# else:
		# 	frappe.db.set(self, "is_default", 0)
		# 	item = frappe.get_doc("Item", self.item)
		# 	if item.default_bom == self.name:
		# 		frappe.db.set_value('Item', self.item, 'default_bom', None)
		# """ Uncheck others if current one is selected as default or
		# 	check the current one as default if it the only doc for the selected item
		# """
		if self.is_default and self.is_active:
			from frappe.model.utils import set_default
			set_default(self, "item")
			frappe.db.sql("""UPDATE `tabMapped BOM`
				set is_default=0
				where item = %s and name !=%s""",
				(self.item,self.name))
		elif not frappe.db.exists(dict(doctype='Mapped BOM',item=self.item,is_default=1)) \
			and self.is_active:
			frappe.db.set(self, "is_default", 1)
		else:
			frappe.db.set(self, "is_default", 0)
	def update_exploded_items(self, save=True):
		""" Update Flat BOM, following will be correct data"""
		self.get_exploded_items()
		self.add_exploded_items(save=save)

	def get_exploded_items(self):
		""" Get all raw materials including items from child bom"""
		self.cur_exploded_items = {}
		for d in self.get('items'):
			if d.mapped_bom:
				self.get_child_exploded_items(d.mapped_bom, d.stock_qty)
			else:
				self.add_to_cur_exploded_items(frappe._dict({
					'item_code'		: d.item_code,
					'item_name'		: d.item_name,
					'operation'		: d.operation,
					'source_warehouse': d.source_warehouse,
					'description'	: d.description,
					'image'			: d.image,
					'stock_uom'		: d.stock_uom,
					'stock_qty'		: flt(d.stock_qty),
					'rate'			: flt(d.base_rate) / (flt(d.conversion_factor) or 1.0),
					'include_item_in_manufacturing': d.include_item_in_manufacturing,
					'sourced_by_supplier': d.sourced_by_supplier
				}))

	def company_currency(self):
		return erpnext.get_company_currency(self.company)

	def add_to_cur_exploded_items(self, args):
		if self.cur_exploded_items.get(args.item_code):
			self.cur_exploded_items[args.item_code]["stock_qty"] += args.stock_qty
		else:
			self.cur_exploded_items[args.item_code] = args

	def get_child_exploded_items(self, mapped_bom, stock_qty):
		""" Add all items from Flat BOM of child BOM"""
		# Did not use qty_consumed_per_unit in the query, as it leads to rounding loss
		child_fb_items = frappe.db.sql("""
			SELECT
				bom_item.item_code,
				bom_item.item_name,
				bom_item.description,
				bom_item.source_warehouse,
				bom_item.operation,
				bom_item.stock_uom,
				bom_item.stock_qty,
				bom_item.rate,
				bom_item.include_item_in_manufacturing,
				bom_item.sourced_by_supplier,
				bom_item.stock_qty / ifnull(bom.quantity, 1) AS qty_consumed_per_unit
			FROM `tabBOM Explosion Item` bom_item, `tabMapped BOM` bom
			WHERE
				bom_item.parent = bom.name
				AND bom.name = %s
				AND bom.docstatus = 1
		""", mapped_bom, as_dict = 1)

		for d in child_fb_items:
			self.add_to_cur_exploded_items(frappe._dict({
				'item_code'				: d['item_code'],
				'item_name'				: d['item_name'],
				'source_warehouse'		: d['source_warehouse'],
				'operation'				: d['operation'],
				'description'			: d['description'],
				'stock_uom'				: d['stock_uom'],
				'stock_qty'				: d['qty_consumed_per_unit'] * stock_qty,
				'rate'					: flt(d['rate']),
				'include_item_in_manufacturing': d.get('include_item_in_manufacturing', 0),
				'sourced_by_supplier': d.get('sourced_by_supplier', 0)
			}))

	def add_exploded_items(self, save=True):
		"Add items to Flat BOM table"
		self.set('exploded_items', [])

		if save:
			frappe.db.sql("""DELETE from `tabBOM Explosion Item` where parent=%s""", self.name)

		for d in sorted(self.cur_exploded_items, key=itemgetter(0)):
			ch = self.append('exploded_items', {})
			for i in self.cur_exploded_items[d].keys():
				ch.set(i, self.cur_exploded_items[d][i])
			ch.amount = flt(ch.stock_qty) * flt(ch.rate)
			ch.qty_consumed_per_unit = flt(ch.stock_qty) / flt(self.quantity)
			ch.docstatus = self.docstatus

			if save:
				ch.db_insert()
	def calculate_cost(self, update_hour_rate = False):
		"""Calculate bom totals"""
		self.calculate_op_cost(update_hour_rate)
		self.calculate_rm_cost()
		self.calculate_sm_cost()
		self.total_cost = self.operating_cost + self.raw_material_cost - self.scrap_material_cost
		self.base_total_cost = self.base_operating_cost + self.base_raw_material_cost - self.base_scrap_material_cost
	def update_parent_cost(self):
		if self.total_cost:
			cost = self.total_cost / self.quantity

			frappe.db.sql("""UPDATE `tabMapped BOM Item` set rate=%s, amount=stock_qty*%s
				where mapped_bom = %s and docstatus < 2 and parenttype='Mapped BOM'""",
				(cost, cost, self.name))
	def update_neww_bom(self, old_bom, new_bom, rate):
		for d in self.get("items"):
			if d.mapped_bom != old_bom: continue

			d.mapped_bom = new_bom
			d.rate = rate
			d.amount = (d.stock_qty or d.qty) * rate

	def replace_bom(self):
		self.validate_bom()

		unit_cost = get_new_bom_unit_cost(self.name)
		self.update_new_bom(unit_cost)

		frappe.cache().delete_key('bom_children')
		bom_list = self.get_parent_boms(self.name)

		with click.progressbar(bom_list) as bom_list:
			pass
		for bom in bom_list:
			try:
				bom_obj = frappe.get_cached_doc('Mapped BOM', bom)
				# this is only used for versioning and we do not want
				# to make separate db calls by using load_doc_before_save
				# which proves to be expensive while doing bulk replace
				bom_obj._doc_before_save = bom_obj
				bom_obj.update_neww_bom(self.old_reference_bom, self.name, unit_cost)
				bom_obj.update_exploded_items()
				bom_obj.calculate_cost()
				bom_obj.update_parent_cost()
				bom_obj.db_update()
				# if bom_obj.meta.get('track_changes') and not bom_obj.flags.ignore_version:
				bom_obj.save_version()
			except Exception:
				frappe.log_error(frappe.get_traceback())
		frappe.db.set_value("Mapped BOM",{'name':self.name},'update_status','Completed')
		frappe.db.commit()
		frappe.msgprint("Mapped BOM Updated Successfully")

	def validate_bom(self):
		if cstr(self.name) == cstr(self.old_reference_bom):
			frappe.throw(_("Current Mapped BOM and New Mapped BOM can not be same"))

		if frappe.db.get_value("Mapped BOM", self.name, "item") \
			!= frappe.db.get_value("Mapped BOM", self.old_reference_bom, "item"):
				frappe.throw(_("The selected Mapped BOMs are not for the same item"))

	
	def update_new_bom(self, unit_cost):
		frappe.db.sql("""UPDATE `tabMapped BOM Item` set mapped_bom=%s,
			rate=%s, amount=stock_qty*%s where mapped_bom = %s and docstatus < 2 and parenttype='Mapped BOM'""",
			(self.name, unit_cost, unit_cost, self.old_reference_bom))

	def get_parent_boms(self, bom, bom_list=None):
		if bom_list is None:
			bom_list = []
		data = frappe.db.sql("""SELECT DISTINCT parent FROM `tabMapped BOM Item`
			WHERE mapped_bom = %s AND docstatus < 2 AND parenttype='Mapped BOM'""", bom)

		for d in data:
			if self.name == d[0]:
				frappe.throw(_("BOM recursion: {0} cannot be child of {1}").format(bom, self.name))

			bom_list.append(d[0])
			self.get_parent_boms(d[0], bom_list)

		return list(set(bom_list))
	@frappe.whitelist()
	def check_propogation(self):
		if self.old_reference_bom and self.name:
			old_bom_data = get_bom_data(self.old_reference_bom)
			old_item_dict = {row.get("item_code"):row for row in old_bom_data}
			new_bom_data = get_bom_data(self.name)
			new_item_dict = {row.get("item_code") for row in new_bom_data}
			final_dict = dict()
			new_item_list = list()
			flag = 0
			for line in new_bom_data:
				if line.is_map_item:
					if line.item_code in old_item_dict:
						if line.qty == old_item_dict.get(line.item_code).get("qty"):
							final_dict.update(line)
							old_item_dict.pop(line.item_code)
						else:
							final_dict.update(line)
							flag=1
							# old_item_dict.pop(line.item_code)
					else:
						new_item_list.append(line)
						final_dict.update(line)
						flag=1
				else :
					if line.item_code in old_item_dict:
						if line.qty == old_item_dict.get(line.item_code).get('qty'):
							old_item_dict.pop(line.item_code)
						else:
							new_item_list.append(line)
							# old_item_dict.pop(line.item_code)
					else:
						new_item_list.append(line)
			for row in old_item_dict:
				if old_item_dict.get(row).get("is_map_item"):
					flag =1
			
			if old_item_dict or len(new_item_list)>0:
				frappe.db.set_value("Mapped BOM",{'name':self.name},'check_propogation_to_descendent_bom',1)
				frappe.db.commit()
				if self.propogate_to_descendent_bom ==0:
					frappe.db.set_value("Mapped BOM",{'name':self.name},'propogate_update_to_descendent_bom_status','Need To Run Propogate Update To Descendent BOMs')
					frappe.db.commit()
				self.reload()

def get_new_bom_unit_cost(bom):
		new_bom_unitcost = frappe.db.sql("""SELECT `total_cost`/`quantity`
			FROM `tabMapped BOM` WHERE name = %s""", bom)

		return flt(new_bom_unitcost[0][0]) if new_bom_unitcost else 0
def validate_bom_no(item, bom_no):
	"""Validate BOM No of sub-contracted items"""
	bom = frappe.get_doc("Mapped BOM", bom_no)
	if not bom.is_active:
		frappe.throw(_("BOM {0} must be active").format(bom_no))
	if bom.docstatus != 1:
		if not getattr(frappe.flags, "in_test", False):
			frappe.throw(_("BOM {0} must be submitted").format(bom_no))
	if item:
		rm_item_exists = False
		for d in bom.items:
			if (d.item_code.lower() == item.lower()):
				rm_item_exists = True
		for d in bom.scrap_items:
			if (d.item_code.lower() == item.lower()):
				rm_item_exists = True
		if bom.item.lower() == item.lower() or \
			bom.item.lower() == cstr(frappe.db.get_value("Item", item, "variant_of")).lower():
 				rm_item_exists = True
		if not rm_item_exists:
			frappe.throw(_("BOM {0} does not belong to Item {1}").format(bom_no, item))

def get_bom_item_rate(args, bom_doc):
		if bom_doc.rm_cost_as_per == 'Valuation Rate':
			rate = get_valuation_rate(args) * (args.get("conversion_factor") or 1)
		elif bom_doc.rm_cost_as_per == 'Last Purchase Rate':
			rate = ( flt(args.get('last_purchase_rate')) \
				or frappe.db.get_value("Item", args['item_code'], "last_purchase_rate")) \
					* (args.get("conversion_factor") or 1)
		elif bom_doc.rm_cost_as_per == "Price List":
			if not bom_doc.buying_price_list:
				frappe.throw(_("Please select Price List"))
			bom_args = frappe._dict({
				"doctype": "Mapped BOM",
				"price_list": bom_doc.buying_price_list,
				"qty": args.get("qty") or 1,
				"uom": args.get("uom") or args.get("stock_uom"),
				"stock_uom": args.get("stock_uom"),
				"transaction_type": "buying",
				"company": bom_doc.company,
				"currency": bom_doc.currency,
				"conversion_rate": 1, # Passed conversion rate as 1 purposefully, as conversion rate is applied at the end of the function
				"conversion_factor": args.get("conversion_factor") or 1,
				"plc_conversion_rate": 1,
				"ignore_party": True,
				"ignore_conversion_rate": True
			})
			item_doc = frappe.get_cached_doc("Item", args.get("item_code"))
			price_list_data = get_price_list_rate(bom_args, item_doc)
			rate = price_list_data.price_list_rate

		return rate
def get_valuation_rate(args):
	""" Get weighted average of valuation rate from all warehouses """

	total_qty, total_value, valuation_rate = 0.0, 0.0, 0.0
	item_bins = frappe.db.sql("""
		SELECT
			bin.actual_qty, bin.stock_value
		from
			`tabBin` bin, `tabWarehouse` warehouse
		where
			bin.item_code=%(item)s
			and bin.warehouse = warehouse.name
			and warehouse.company=%(company)s""",
		{"item": args['item_code'], "company": args['company']}, as_dict=1)

	for d in item_bins:
		total_qty += flt(d.actual_qty)
		total_value += flt(d.stock_value)

	if total_qty:
		valuation_rate =  total_value / total_qty

	if valuation_rate <= 0:
		last_valuation_rate = frappe.db.sql("""SELECT valuation_rate
			from `tabStock Ledger Entry`
			where item_code = %s and valuation_rate > 0 and is_cancelled = 0
			order by posting_date desc, posting_time desc, creation desc limit 1""", args['item_code'])

		valuation_rate = flt(last_valuation_rate[0][0]) if last_valuation_rate else 0

	if not valuation_rate:
		valuation_rate = frappe.db.get_value("Item", args['item_code'], "valuation_rate")

	return flt(valuation_rate)
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
		return bom_no,'Yes',item_doc.stock_uom
	else:
		bom_no = frappe.db.get_value("BOM",{'item':item_code,'is_default' :1,'is_active' : 1},'name')
		return bom_no,'No',item_doc.stock_uom

@frappe.whitelist()
def get_mapped_bom_query(item_code):
	mapped_bom_query = frappe.db.sql("""SELECT name from `tabMapped BOM` where item = '{0}'""".format(item_code),as_dict=1)
	mapped_bom_list = [item.name for item in mapped_bom_query]
	return mapped_bom_list

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_items(doctype, txt, searchfield, start, page_len, filters):
	return frappe.db.sql(""" SELECT name FROM `tabItem` where is_map_item = '{0}' """.format(filters.get("is_map_item")))
@frappe.whitelist()
def enqueue_replace_bom(args):
	if isinstance(args, string_types):
		args = json.loads(args)
		frappe.db.set_value("Mapped BOM",{'name':args.get("new_bom")},'update_status','In Process')
		frappe.db.commit()


	# replace_bom(args)
	frappe.enqueue("instrument.instrument.doctype.mapped_bom.mapped_bom.replace_bom", args=args, timeout=40000)
	frappe.msgprint(_("Queued for replacing the BOM. It may take a few minutes."))

@frappe.whitelist()
def replace_bom(args):
	frappe.db.auto_commit_on_many_writes = 1
	args = frappe._dict(args)

	doc = frappe.get_doc("Mapped BOM",args.new_bom)
	doc.update_status = 'In Process'
	doc.old_reference_bom = args.current_bom
	doc.name = args.new_bom
	doc.replace_bom()

	frappe.db.auto_commit_on_many_writes = 0

@frappe.whitelist()
def propogate_update_to_descendent(current_bom,new_bom):
	if current_bom and new_bom:
		old_bom_data = get_bom_data(current_bom)
		old_item_dict = {row.get("item_code"):row for row in old_bom_data}
		new_bom_data = get_bom_data(new_bom)
		new_item_dict = {row.get("item_code") for row in new_bom_data}
		final_dict = dict()
		new_item_list = list()
		flag = 0
		for line in new_bom_data:
			if line.is_map_item:
				if line.item_code in old_item_dict:
					if line.qty == old_item_dict.get(line.item_code).get("qty"):
						final_dict.update(line)
						old_item_dict.pop(line.item_code)
					else:
						final_dict.update(line)
						flag=1
						old_item_dict.pop(line.item_code)
				else:
					final_dict.update(line)
					flag=1
			else :
				if line.item_code in old_item_dict:
					if line.qty == old_item_dict.get(line.item_code).get('qty'):
						old_item_dict.pop(line.item_code)
					else:
						new_item_list.append(line)
						old_item_dict.pop(line.item_code)
				else:
					new_item_list.append(line)
		for row in old_item_dict:
			if old_item_dict.get(row).get("is_map_item"):
				flag =1
		if flag ==1 :
			create_bom_creation_tool(current_bom,new_bom)
		else:
			create_standard_bom(current_bom,new_item_list,old_item_dict,new_bom)
		frappe.db.set_value("Mapped BOM",new_bom,'propogate_update_to_descendent_bom_status','Completed')
		frappe.db.commit()

def create_bom_creation_tool(current_bom,bom):
	if current_bom:
		bom_creation_docs = frappe.get_all("BOM Creation Tool",{'mapped_bom':current_bom})
		
		if len(bom_creation_docs) == 0 :
			frappe.throw("BOM Creation Tool is not Found for Mapped BOM {0}".format(current_bom))
		else:
			for d in bom_creation_docs:
				old_doc = frappe.get_doc("BOM Creation Tool",d.get("name"))
				if old_doc.docstatus == 1 :
					new_doc = frappe.copy_doc(old_doc, ignore_no_copy=False)
					new_doc.mapped_bom = bom
					new_doc.review_item_mapping = ''
					new_doc.save()
					frappe.db.set_value("Mapped BOM",{'name':bom},'propogate_to_descendent_bom',1)
					frappe.db.commit()
					frappe.msgprint("BOM Creation Tool Created For Mapped BOM <b>{0}</b>".format(bom))
				else:
					old_doc.mapped_bom = bom
					old_doc.save()
					frappe.db.set_value("Mapped BOM",{'name':bom},'propogate_to_descendent_bom',1)
					frappe.db.commit()
					frappe.msgprint("BOM Creation Tool Updated For Mapped BOM <b>{0}</b>".format(bom))

		# bom_creation_data ,check_exists = get_map_item_attributes(bom)
		# bom_creation_tool = frappe.new_doc("BOM Creation Tool")
		# if bom_creation_tool:
		# 	bom_creation_tool.mapped_bom = bom
		# 	if check_exists == False:
		# 		for line in bom_creation_data:
		# 			for row in line.get("attribute_list"):
		# 				bom_creation_tool.append('attribute_table',{
		# 					'mapped_bom':line.get("parent"),
		# 					'mapped_item':row.get("mapped_item"),
		# 					'attribute':row.get("attribute")
		# 					})
		# 	else:
		# 		for row in bom_creation_data:
		# 			for line in bom_creation_data:
		# 				bom_creation_tool.append('attribute_table',{
		# 					'mapped_bom':line.get("parent"),
		# 					'mapped_item':row.get("mapped_item"),
		# 					'attribute':row.get("attribute"),
		# 					'value':row.get("value")
		# 					})
		# 	bom_creation_tool.save()
		# 	frappe.db.set_value("Mapped BOM",{'name':bom},'propogate_to_descendent_bom',1)
		# 	frappe.db.commit()
		# 	frappe.msgprint("BOM Creation Tool Created For Mapped BOM <b>{0}</b>".format(bom))
def create_standard_bom(mapped_bom,item_list,old_item_dict,new_bomm):
	bom_data = get_bom_list(mapped_bom)
	for bom in bom_data:
		old_bom = frappe.get_doc("BOM",bom.get("name"))
		new_bom = frappe.copy_doc(old_bom, ignore_no_copy=False)
		new_item_dict = {row.item_code :row for row in new_bom.items}
		if len(item_list) > 0:
			for row in item_list:
				if row.item_code in new_item_dict:
					for line in new_bom.items:
						if line.item_code == row.item_code:
							line.qty = row.qty
				else:
					new_bom.append('items',row)
		if old_item_dict:
			for row in new_bom.items:
				if row.item_code in old_item_dict:
					new_bom.items.remove(row)
		new_bom.save()
		frappe.db.set_value("Mapped BOM",{'name':new_bomm},'propogate_to_descendent_bom',1)
		frappe.db.commit()
		frappe.msgprint("New Version Created For BOM <b>{0}</b>".format(bom.get("name")))

def get_bom_data(bom):
	old_bom_data = frappe.db.sql("""SELECT * from `tabMapped BOM Item` where parent = '{0}'""".format(bom),as_dict=1)
	return old_bom_data
def get_bom_list(bom):
	if bom:
		bom_list = frappe.db.sql("""SELECT name from `tabBOM` where mapped_bom = '{0}' and docstatus = 1 """.format(bom),as_dict=1)
		return bom_list


@frappe.whitelist()
def get_bom_diff(bom1, bom2):
	from frappe.model import table_fields

	if bom1 == bom2:
		frappe.throw(_("Mapped BOM 1 {0} and Mapped BOM 2 {1} should not be same")
			.format(frappe.bold(bom1), frappe.bold(bom2)))

	doc1 = frappe.get_doc('Mapped BOM', bom1)
	doc2 = frappe.get_doc('Mapped BOM', bom2)

	out = get_diff(doc1, doc2)
	out.row_changed = []
	out.added = []
	out.removed = []

	meta = doc1.meta

	identifiers = {
		'operations': 'operation',
		'items': 'item_code',
		'scrap_items': 'item_code',
		'exploded_items': 'item_code',
		'deleted_items' : 'item_code'
	}

	for df in meta.fields:
		old_value, new_value = doc1.get(df.fieldname), doc2.get(df.fieldname)

		if df.fieldtype in table_fields:
			identifier = identifiers[df.fieldname]
			# make maps
			old_row_by_identifier, new_row_by_identifier = {}, {}
			for d in old_value:
				old_row_by_identifier[d.get(identifier)] = d
			for d in new_value:
				new_row_by_identifier[d.get(identifier)] = d

			# check rows for additions, changes
			for i, d in enumerate(new_value):
				if d.get(identifier) in old_row_by_identifier:
					diff = get_diff(old_row_by_identifier[d.get(identifier)], d, for_child=True)
					if diff and diff.changed:
						out.row_changed.append((df.fieldname, i, d.get(identifier), diff.changed))
				else:
					out.added.append([df.fieldname, d.as_dict()])

			# check for deletions
			for d in old_value:
				if not d.get(identifier) in new_row_by_identifier:
					out.removed.append([df.fieldname, d.as_dict()])

	return out

@frappe.whitelist()
def get_children(doctype, parent=None, is_root=False, **filters):
	if not parent or parent=="Mapped BOM":
		frappe.msgprint(_('Please select a Mapped BOM'))
		return

	if parent:
		frappe.form_dict.parent = parent

	if frappe.form_dict.parent:
		name_string = frappe.form_dict.parent
		result = name_string.startswith('Map')
		if result == True:
			bom_doc = frappe.get_cached_doc("Mapped BOM", frappe.form_dict.parent)
			frappe.has_permission("Mapped BOM", doc=bom_doc, throw=True)

			bom_items = frappe.get_all('Mapped BOM Item',
				fields=['item_code', 'mapped_bom as value','stock_qty','is_map_item'],
				filters=[['parent', '=', frappe.form_dict.parent]],
				order_by='idx')
			# print("///////////////////////bom_items",bom_items)
			bom_items_for_std_bom = frappe.get_all('Mapped BOM Item',
				fields=['item_code', 'bom_no as value','stock_qty','is_map_item'],
				filters=[['parent', '=', frappe.form_dict.parent]],
				order_by='idx')
			for row in bom_items:
				for col in bom_items_for_std_bom:
					if row.item_code == col.item_code:
						if col.value:
							row['value'] = col.value
			item_names = tuple(d.get('item_code') for d in bom_items)

			items = frappe.get_list('Item',
				fields=['image', 'description', 'name', 'stock_uom', 'item_name', 'is_sub_contracted_item'],
				filters=[['name', 'in', item_names]]) # to get only required item dicts

			for bom_item in bom_items:
				# extend bom_item dict with respective item dict
				bom_item.update(
					# returns an item dict from items list which matches with item_code
					next(item for item in items if item.get('name')
						== bom_item.get('item_code'))
				)

				bom_item.parent_bom_qty = bom_doc.quantity
				bom_item.expandable = 0 if bom_item.value in ('', None)  else 1
				bom_item.image = frappe.db.escape(bom_item.image)
		else:
			bom_doc = frappe.get_cached_doc("BOM", frappe.form_dict.parent)
			frappe.has_permission("BOM", doc=bom_doc, throw=True)

			bom_items = frappe.get_all('BOM Item',
				fields=['item_code', 'bom_no as value','stock_qty'],
				filters=[['parent', '=', frappe.form_dict.parent]],
				order_by='idx')
			
			item_names = tuple(d.get('item_code') for d in bom_items)

			items = frappe.get_list('Item',
				fields=['image', 'description', 'name', 'stock_uom', 'item_name', 'is_sub_contracted_item'],
				filters=[['name', 'in', item_names]]) # to get only required item dicts

			for bom_item in bom_items:
				# extend bom_item dict with respective item dict
				bom_item.update(
					# returns an item dict from items list which matches with item_code
					next(item for item in items if item.get('name')
						== bom_item.get('item_code'))
				)

				bom_item.parent_bom_qty = bom_doc.quantity
				bom_item.expandable = 0 if bom_item.value in ('', None)  else 1
				bom_item.image = frappe.db.escape(bom_item.image)
		return bom_items
@frappe.whitelist()
def check_bc_doc(mapped_bom,mapped_item):
	if mapped_item and mapped_bom:
		item_mappings = frappe.db.sql("""SELECT item_code from `tabItem Mapping` where mapped_item = '{0}'""".format(mapped_item),as_dict=1)
		item_mappings_list = [row.item_code for row in item_mappings]
		check_existing = frappe.db.sql("""SELECT standard_item_code from `tabBOM Creation Tool` where mapped_bom = '{0}' and mapped_item = '{1}'""".format(mapped_bom,mapped_item),as_dict=1)
		if len(check_existing) > 0:
			for row in check_existing:
				if row.standard_item_code in item_mappings_list:
					item_mappings_list.remove(row.standard_item_code)
		if len(item_mappings_list) == 0:
			return True
	# check_bc_doc = frappe.db.get_all("BOM Creation Tool",{'mapped_bom':mapped_bom,'docstatus':0})
	# if len(check_bc_doc) > 0 :
	# 	return True

@frappe.whitelist()
def create_bom_tree_for_item_mapping(mapped_item,mapped_bom):
	bct_doc_list = []
	if mapped_item and mapped_bom:
		item_mappings = frappe.db.sql("""SELECT item_code from `tabItem Mapping` where mapped_item = '{0}'""".format(mapped_item),as_dict=1)
		item_mappings_list = [row.item_code for row in item_mappings]
		check_existing = frappe.db.sql("""SELECT standard_item_code from `tabBOM Creation Tool` where mapped_bom = '{0}' and mapped_item = '{1}'""".format(mapped_bom,mapped_item),as_dict=1)
		if len(check_existing) > 0:
			for row in check_existing:
				if row.standard_item_code in item_mappings_list:
					item_mappings_list.remove(row.standard_item_code)

		if len(item_mappings_list) > 0:
			for row in item_mappings_list:
				bc_doc = frappe.new_doc("BOM Creation Tool")
				if bc_doc:
					bc_doc.mapped_item = mapped_item
					bc_doc.standard_item_code = row
					bc_doc.mapped_bom = mapped_bom
					bc_doc.save()
					frappe.msgprint("BOM Creation Tool Created For Item Mapping<b>{0}</b>".format(row))

