import frappe
from frappe import _, bold, msgprint
from frappe.utils import cint, cstr, flt

import erpnext
from erpnext.accounts.utils import get_company_default
from erpnext.controllers.stock_controller import StockController
from erpnext.stock.doctype.batch.batch import get_batch_qty
from erpnext.stock.doctype.serial_no.serial_no import get_serial_nos
from erpnext.stock.utils import get_stock_balance

@frappe.whitelist()
def get_items(item_code,
	posting_date, posting_time, company, warehouse=None, ignore_empty_stock=False
):
	ignore_empty_stock = cint(ignore_empty_stock)
	items = [frappe._dict({"item_code": item_code, "warehouse": warehouse})]

	if not warehouse:
		items = get_items_for_stock_reco(item_code, company)
	res = []
	warehousewise_batch_data = get_warehousewise_batch(item_code, posting_date, company, warehouse)
	for d in items:
		if d.warehouse in warehousewise_batch_data:
			valuation_rate = get_stock_balance(
				d.item_code, d.warehouse, posting_date, posting_time, with_valuation_rate=True
			)[1]

			for row in warehousewise_batch_data.get(d.warehouse):
				if ignore_empty_stock and not row.qty:
					continue

				args = get_item_data(row, row.qty, valuation_rate)
				res.append(args)
		else:
			stock_bal = get_stock_balance(
				d.item_code,
				d.warehouse,
				posting_date,
				posting_time,
				with_valuation_rate=True,
				with_serial_no=cint(d.has_serial_no),
			)
			qty, valuation_rate, serial_no = (
				stock_bal[0],
				stock_bal[1],
				stock_bal[2] if cint(d.has_serial_no) else "",
			)

			if ignore_empty_stock and not stock_bal[0]:
				continue

			args = get_item_data(d, qty, valuation_rate, serial_no)

			res.append(args)

	return res

def get_items_for_stock_reco(item_code, company):
	# lft, rgt = frappe.db.get_value("Warehouse", warehouse, ["lft", "rgt"])
	items = frappe.db.sql(
		f"""
		select
			i.name as item_code, i.item_name, bin.warehouse as warehouse, i.has_serial_no, i.has_batch_no
		from
			tabBin bin, tabItem i
		where
			i.name = bin.item_code
			and IFNULL(i.disabled, 0) = 0
			and i.is_stock_item = 1
			and i.has_variants = 0
			and i.name = '{item_code}'
			and exists(
				select name from `tabWarehouse` where  name = bin.warehouse
			)
	""",
		as_dict=1,
	)

	items += frappe.db.sql(
		"""
		select
			i.name as item_code, i.item_name, id.default_warehouse as warehouse, i.has_serial_no, i.has_batch_no
		from
			tabItem i, `tabItem Default` id
		where
			i.name = id.parent
			and exists(
				select name from `tabWarehouse` where name=id.default_warehouse
			)
			and i.name = %s
			and i.is_stock_item = 1
			and i.has_variants = 0
			and IFNULL(i.disabled, 0) = 0
			and id.company = %s
		group by i.name
	""",
		(item_code, company),
		as_dict=1,
	)

	# remove duplicates
	# check if item-warehouse key extracted from each entry exists in set iw_keys
	# and update iw_keys
	iw_keys = set()
	items = [
		item
		for item in items
		if [
			(item.item_code, item.warehouse) not in iw_keys,
			iw_keys.add((item.item_code, item.warehouse)),
		][0]
	]

	return items

def get_warehousewise_batch(item_code, posting_date, company, warehouse=None):
	from erpnext.stock.report.batch_wise_balance_history.batch_wise_balance_history import execute

	itemwise_batch_data = {}

	filters = frappe._dict(
		{"item_code": item_code, "from_date": posting_date, "to_date": posting_date, "company": company}
	)

	if item_code:
		filters.warehouse = warehouse

	columns, data = execute(filters)
	for row in data:
		itemwise_batch_data.setdefault(row[3], []).append(
			frappe._dict(
				{
					"item_code": row[0],
					"warehouse": row[3],
					"qty": row[8],
					"item_name": row[1],
					"batch_no": row[4],
				}
			)
		)

	return itemwise_batch_data

def get_item_data(row, qty, valuation_rate, serial_no=None):
	return {
		"item_code": row.item_code,
		"warehouse": row.warehouse,
		"qty": qty,
		"item_name": row.item_name,
		"valuation_rate": valuation_rate,
		"current_qty": qty,
		"current_valuation_rate": valuation_rate,
		"current_serial_no": serial_no,
		"serial_no": serial_no,
		"batch_no": row.get("batch_no"),
	}