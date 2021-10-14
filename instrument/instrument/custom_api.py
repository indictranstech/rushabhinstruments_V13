import frappe

@frappe.whitelist(allow_guest=True)
def item_details_api():
	return frappe.db.sql(f"""select a.item_code,a.item_name,a.item_group,a.weight_uom,a.description,a.stock_uom,a.end_of_life,b.default_warehouse  from `tabItem` a left join `tabItem Default` b ON a.item_code = b.parent""", as_dict=True)


@frappe.whitelist(allow_guest=True)
def sales_order_api():
	return frappe.db.sql(f"""select a.customer,a.order_type,a.transaction_date,a.delivery_date,a.company,a.currency,a.selling_price_list,b.item_code,b.item_name,b.uom,
	b.qty,b.rate,b.amount,b.description,b.conversion_factor,b.base_rate,b.base_amount
	from `tabSales Order` a left join `tabSales Order Item` b
	ON a.name = b.parent """, as_dict=True)

@frappe.whitelist()
def sales_invoice_api(allow_guest=True):
	return frappe.db.sql(f""" select a.customer,a.company,a.posting_date,a.posting_time,a.due_date,a.currency,a.selling_price_list,a.debit_to,a.base_net_total,a.base_grand_total,a.grand_total,
	b.parenttype,b.item_code,b.item_name,b.uom,b.qty,b.rate,b.amount,b.description,b.conversion_factor,b.income_account,b.base_rate,b.base_amount,
	c.parenttype,c.payment_amount,c.invoice_portion,c.due_date
	from `tabSales Invoice` a left join `tabSales Invoice Item` b ON a.name = b.parent
	left join `tabPayment Schedule` c ON a.name = b.parent and a.name=c.parent""", as_dict=True)
