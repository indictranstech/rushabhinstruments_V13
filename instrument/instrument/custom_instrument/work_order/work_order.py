from __future__ import unicode_literals
import frappe

@frappe.whitelist()
def update_work_order(doc,method):
	final_item_status = []
	for item in doc.required_items:
		if item.transferred_qty == item.required_qty:
			final_item_status.append('Full Qty Available')
		elif item.transferred_qty != 0 and item.transferred_qty < item.required_qty:
			final_item_status.append('Partial Qty Available')
		else : 
			final_item_status.append('Qty Not Available')
	status_list = ['Full Qty Available']
	check =  all(item in status_list for item in final_item_status)
	if check == True:
		frappe.db.set_value("Work Order",doc.name,'item_stock_status','Full Qty Available')
		frappe.db.commit()
		doc.reload()
	status_list_na = ['Partial Qty Available']
	check_na = all(item in status_list_na for item in final_item_status)
	if check_na == True:
		frappe.db.set_value("Work Order",doc.name,'item_stock_status','Partial Qty Available')
		frappe.db.commit()
		doc.reload()

