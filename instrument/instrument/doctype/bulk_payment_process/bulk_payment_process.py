# Copyright (c) 2022, instrument and contributors
# For license information, please see license.txt

# import frappe
# from frappe.model.document import Document

# class BulkPaymentProcess(Document):
# 	pass
# Copyright (c) 2022, Indictrans and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname

class BulkPaymentProcess(Document):
	def autoname(self):
		self.name = make_autoname('SUP-BPP-.YYYY.-')

	def validate(self):
		if self.payment_completed==1:
			frappe.throw(title="Not Allowed", msg="Payment Process already completed. Not allowed to change.")

	@frappe.whitelist()
	def on_update_after_submit(self):
		if self.payment_completed==1:
			frappe.throw(title="Not Allowed", msg="Payment Process already completed. Not allowed to change.")
		# if self.workflow_state:
			# if self.workflow_state=="Approved":
		for item in self.items:
			if item.amount and item.invoice_no:
				pi_doc = frappe.get_doc('Purchase Invoice', item.invoice_no)
				pe_doc = frappe.new_doc('Payment Entry')
				pe_doc.payment_type ='Pay'
				pe_doc.mode_of_payment = self.mode_of_payment
				pe_doc.paid_from = self.payment_account
				pe_doc.paid_from_account_currency = self.account_currency
				pe_doc.party_type ='Supplier'
				pe_doc.party = pi_doc.supplier
				pe_doc.paid_amount = item.amount
				pe_doc.received_amount = item.amount
				pe_doc.source_exchange_rate = 1
				pe_doc.bulk_payment_process = self.name
				pe_doc.reference_no = self.reference_no
				pe_doc.reference_date = self.reference_date
				pe_doc_references = pe_doc.append('references')
				pe_doc_references.reference_doctype = 'Purchase Invoice'
				pe_doc_references.reference_name = item.invoice_no
				pe_doc_references.grand_total = item.invoice_amount
				pe_doc_references.outstanding_amount = item.outstanding_amount
				pe_doc_references.allocated_amount = item.amount
				pe_doc.submit()
				frappe.msgprint('Payment Enrty against '+ item.invoice_no + ' is completed')
		self.payment_completed=1

	@frappe.whitelist()
	# def get_invoices_with_filters(upto_due_date=None, from_invoice_date=None, to_invoice_date=None, supplier_group=None, order_by=None, sort_by=None):
	def get_invoices_with_filters(self):
		if self.upto_due_date and self.from_invoice_date and self.to_invoice_date:
			purchase_invoice_list = frappe.db.sql("""SELECT * from `tabPurchase Invoice` pi where pi.outstanding_amount != 0 and pi.docstatus = 1 and pi.due_date <= '{0}' and pi.posting_date between '{1}' and '{2}' order by {3} {4}""".format(self.upto_due_date,self.from_invoice_date,self.to_invoice_date,self.order_by,self.sort_as),as_dict=1,debug=1)
			if purchase_invoice_list != []:
				for row in purchase_invoice_list:
					supplier_group = frappe.db.get_values("Supplier",{'name':row.supplier},['supplier_group','supplier_name'],as_dict=1)
					self.append('items',{
						'invoice_no':row.name,
						'supplier':row.supplier,
						'supplier_group':supplier_group[0].get('supplier_group'),
						'supplier_name':supplier_group[0].get('supplier_name'),
						'amount':row.outstanding_amount,
						'outstanding_amount':row.outstanding_amount,
						'invoice_amount':row.rounded_total,
						'approve':1
						})
			return purchase_invoice_list
		else:
			frappe.msgprint("Please set the filters")
		# if order_by and sort_by:
		# 	order_by_condition = order_by + " " + sort_by
		# else:
		# 	order_by_condition = ""

		# if upto_due_date and from_invoice_date and to_invoice_date and supplier_group:
		# 	purchase_invoice_list = frappe.db.get_all('Purchase Invoice', filters = [['outstanding_amount','!=', 0],['docstatus','=',1], ['due_date','<=', upto_due_date], ['posting_date','between', [from_invoice_date, to_invoice_date]]], order_by=order_by_condition)
		# 	print("=============purchase_invoice_list",purchase_invoice_list)
		# 	return purchase_invoice_list
		# elif from_invoice_date and to_invoice_date and supplier_group:
		# 	purchase_invoice_list = frappe.db.get_all('Purchase Invoice', filters = [['outstanding_amount','!=', 0],['docstatus','=',1],['posting_date','between', [from_invoice_date, to_invoice_date]]], order_by=order_by_condition)
		# 	print("=============purchase_invoice_list",purchase_invoice_list)
		# 	return purchase_invoice_list
		# elif from_invoice_date and to_invoice_date:
		# 	purchase_invoice_list = frappe.db.get_all('Purchase Invoice', filters = [['outstanding_amount','!=', 0],['docstatus','=',1],['posting_date','between', [from_invoice_date, to_invoice_date]]], order_by=order_by_condition)
		# 	print("=============purchase_invoice_list",purchase_invoice_list)
		# 	return purchase_invoice_list
		# elif upto_due_date and supplier_group:
		# 	purchase_invoice_list = frappe.db.get_all('Purchase Invoice', filters = [['outstanding_amount','!=', 0],['docstatus','=',1], ['due_date','<=', upto_due_date]], order_by=order_by_condition)
		# 	print("=============purchase_invoice_list",purchase_invoice_list)
		# 	return purchase_invoice_list
		# elif upto_due_date:
		# 	purchase_invoice_list = frappe.db.get_all('Purchase Invoice', filters = [['outstanding_amount','!=', 0],['docstatus','=',1], ['due_date','<=', upto_due_date]], order_by=order_by_condition)
		# 	print("=============purchase_invoice_list",purchase_invoice_list)
		# 	return purchase_invoice_list
		# elif supplier_group:
		# 	purchase_invoice_list = frappe.db.get_all('Purchase Invoice', filters = [['outstanding_amount','!=', 0],['docstatus','=',1]], order_by=order_by_condition)
		# 	return purchase_invoice_list
		# else:
		# 	return []