# Copyright (c) 2022, instrument and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
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
class ProductionPlanningWithLeadTime(Document):
	@frappe.whitelist()
	def get_open_sales_orders(self):
		print("============called")
		""" Pull sales orders  which are pending to deliver based on criteria selected"""
		open_so = get_sales_orders(self)

		if open_so:
			self.add_so_in_table(open_so)
		else:
			frappe.msgprint(_("Sales orders are not available for production"))
	@frappe.whitelist()
	def add_so_in_table(self, open_so):
		""" Add sales orders in the table"""
		self.set('sales_order_table', [])

		for data in open_so:
			print("===========data",data.get('name'))
			bom_data = frappe.db.sql("""SELECT name,makeup_days from `tabBOM` where item = '{0}' and is_active = 1 and is_default =1 and docstatus = 1""".format(data.get("item_code")),as_dict=1)
			# bom_data = frappe.db.sql("BOM",{'is_active':1,'is_default':1,'item':data.get("item_code"),'docstatus':1},['name','makeup_days'])
			print("-----------bom_data",bom_data,data.get('delivery_date').date())
			self.append('sales_order_table', {
				'sales_order': data.get("name"),
				'item':data.get('item_code'),
				'delivery_date':data.get('delivery_date').date(),
				'qty':data.get('qty'),
				'bom':bom_data[0].get('name'),
				'makeup_days':bom_data[0].get('makeup_days')
			})
def get_sales_orders(self):
	so_filter = item_filter = ""
	bom_item = "bom.item = so_item.item_code"
	company = frappe.db.get_single_value("Global Defaults",'default_company')
	print("=========company",company)
	date_field_mapper = {
		'from_date': ('>=', 'so.transaction_date'),
		'to_date': ('<=', 'so.transaction_date'),
		'from_delivery_date': ('>=', 'so_item.delivery_date'),
		'to_delivery_date': ('<=', 'so_item.delivery_date')
	}

	for field, value in date_field_mapper.items():
		if self.get(field):
			so_filter += f" and {value[1]} {value[0]} %({field})s"

	for field in ['customer']:
		if self.get(field):
			so_field = field
			so_filter += f" and so.{so_field} = %({field})s"

	if self.item and frappe.db.exists('Item', self.item):
		bom_item = self.get_bom_item() or bom_item
		item_filter += " and so_item.item_code = %(item_code)s"

	open_so = frappe.db.sql(f"""
		select distinct so.name, so.transaction_date, so.customer, date(so_item.delivery_date) as delivery_date,so_item.item_code,so_item.qty
		from `tabSales Order` so, `tabSales Order Item` so_item
		where so_item.parent = so.name
			and so.docstatus = 1 and so.status not in ("Stopped", "Closed")
			and so.company = '{company}' {so_filter} {item_filter}
			and (exists (select name from `tabBOM` bom where {bom_item}
					and bom.is_active = 1)
				or exists (select name from `tabPacked Item` pi
					where pi.parent = so.name and pi.parent_item = so_item.item_code
						and exists (select name from `tabBOM` bom where bom.item=pi.item_code
							and bom.is_active = 1)))
		""", self.as_dict(), as_dict=1,debug=1)
	print("------------open_so",open_so)
	return open_so
def get_bom_item(self):
	"""Check if Item or if its Template has a BOM."""
	bom_item = None
	has_bom = frappe.db.exists({'doctype': 'BOM', 'item': self.item, 'docstatus': 1})
	if not has_bom:
		template_item = frappe.db.get_value('Item', self.item, ['variant_of'])
		bom_item = "bom.item = {0}".format(frappe.db.escape(template_item)) if template_item else bom_item
	return bom_item
