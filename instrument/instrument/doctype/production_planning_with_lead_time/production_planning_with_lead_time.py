# Copyright (c) 2022, instrument and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class ProductionPlanningWithLeadTime(Document):
	@frappe.whitelist()
	def get_open_sales_orders(self):
		""" Pull sales orders  which are pending to deliver based on criteria selected"""
		open_so = get_sales_orders(self)

		if open_so:
			self.add_so_in_table(open_so)
		else:
			frappe.msgprint(_("Sales orders are not available for production"))
def get_sales_orders(self):
	so_filter = item_filter = ""
	bom_item = "bom.item = so_item.item_code"

	date_field_mapper = {
		'from_date': ('>=', 'so.transaction_date'),
		'to_date': ('<=', 'so.transaction_date'),
		'from_delivery_date': ('>=', 'so_item.delivery_date'),
		'to_delivery_date': ('<=', 'so_item.delivery_date')
	}

	for field, value in date_field_mapper.items():
		if self.get(field):
			so_filter += f" and {value[1]} {value[0]} %({field})s"

	for field in ['customer', 'project', 'sales_order_status']:
		if self.get(field):
			so_field = 'status' if field == 'sales_order_status' else field
			so_filter += f" and so.{so_field} = %({field})s"

	if self.item_code and frappe.db.exists('Item', self.item_code):
		bom_item = self.get_bom_item() or bom_item
		item_filter += " and so_item.item_code = %(item_code)s"

	open_so = frappe.db.sql(f"""
		select distinct so.name, so.transaction_date, so.customer, so.base_grand_total
		from `tabSales Order` so, `tabSales Order Item` so_item
		where so_item.parent = so.name
			and so.docstatus = 1 and so.status not in ("Stopped", "Closed")
			and so.company = %(company)s
			and so_item.qty > so_item.work_order_qty {so_filter} {item_filter}
			and (exists (select name from `tabBOM` bom where {bom_item}
					and bom.is_active = 1)
				or exists (select name from `tabPacked Item` pi
					where pi.parent = so.name and pi.parent_item = so_item.item_code
						and exists (select name from `tabBOM` bom where bom.item=pi.item_code
							and bom.is_active = 1)))
		""", self.as_dict(), as_dict=1)

	return open_so
def add_so_in_table(self, open_so):
	""" Add sales orders in the table"""
	self.set('sales_orders', [])

	for data in open_so:
		self.append('sales_orders', {
			'sales_order': data.name,
			'sales_order_date': data.transaction_date,
			'customer': data.customer,
			'grand_total': data.base_grand_total
		})