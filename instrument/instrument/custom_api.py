import frappe

@frappe.whitelist(allow_guest=True)
def item_details_api():
	return frappe.db.sql(f"""select a.item_code,a.item_name,a.item_group,a.weight_uom,a.description,a.stock_uom,a.end_of_life,a.lead_time_days,b.default_warehouse  from `tabItem` a left join `tabItem Default` b ON a.item_code = b.parent""", as_dict=True)


@frappe.whitelist(allow_guest=True)
def sales_order_api():
	return frappe.db.sql(f"""select a.customer,a.order_type,a.transaction_date,a.delivery_date,a.company,a.currency,a.selling_price_list,b.item_code,b.item_name,b.uom,
	b.qty,b.rate,b.amount,b.description,b.conversion_factor,b.base_rate,b.base_amount
	from `tabSales Order` a left join `tabSales Order Item` b
	ON a.name = b.parent """, as_dict=True)

@frappe.whitelist()
def sales_invoice_api():
	return frappe.db.sql(f""" select a.customer,a.company,a.posting_date,a.posting_time,a.due_date,a.currency,a.selling_price_list,a.debit_to,a.base_net_total,a.base_grand_total,a.grand_total,
	b.parenttype,b.item_code,b.item_name,b.uom,b.qty,b.rate,b.amount,b.description,b.conversion_factor,b.income_account,b.base_rate,b.base_amount,
	c.parenttype,c.payment_amount,c.invoice_portion,c.due_date
	from `tabSales Invoice` a left join `tabSales Invoice Item` b ON a.name = b.parent
	left join `tabPayment Schedule` c ON a.name = b.parent and a.name=c.parent""", as_dict=True)

@frappe.whitelist()
def delivery_note_api():
	return frappe.db.sql(f""" select a.customer,a.company,a.posting_date,a.posting_time,a.currency,a.selling_price_list,a.base_net_total,a.base_grand_total,a.grand_total,
	b.item_code,b.item_name,b.uom,b.qty,b.rate,b.amount,b.description,b.conversion_factor,b.base_rate,b.base_amount,b.against_sales_order,b.against_sales_invoice,a.total_taxes_and_charges,
	c.account_head,c.description,c.rate,c.tax_amount
	from `tabDelivery Note` a left join `tabDelivery Note Item` b ON a.name = b.parent left join `tabSales Taxes and Charges` c ON a.name=c.parent""", as_dict=True)

@frappe.whitelist()
def customer_api():
	return frappe.db.sql(f""" Select a.name,a.customer_name,a.customer_group,a.territory,a.tax_id,d.address_line1,d.address_line2,d.city,d.state,d.country,d.county,d.pincode,d.email_id,d.phone from
	(Select * from `tabCustomer`)a
	left join
	(Select * from
	((Select name,address_line1,address_line2,city,state,country,county,pincode,email_id,phone From `tabAddress`)b
	left join
	(Select parent,link_name,link_doctype From `tabDynamic Link` where link_doctype="Customer" and parenttype="Address")c
	ON b.name=c.parent))d ON a.name=d.link_name""", as_dict=True)

@frappe.whitelist()
def item_wise_stock_api():
	return frappe.db.sql(f""" select warehouse,modified as date,item_code,actual_qty,stock_uom,valuation_rate,stock_value from `tabBin` """, as_dict=True)

@frappe.whitelist()
def item_wise_production_api():
	return frappe.db.sql(f""" select name as work_order,status,production_item,item_name,qty as qty_for_manufacture,material_transferred_for_manufacturing,produced_qty,sales_order,
wip_warehouse,fg_warehouse,planned_start_date,planned_end_date,actual_start_date,actual_end_date
from `tabWork Order` where docstatus=1; """, as_dict=True)


