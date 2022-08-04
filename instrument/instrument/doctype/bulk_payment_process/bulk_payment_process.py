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
from frappe.utils import (
	add_days,
	ceil,
	cint,
	comma_and,
	flt,
	get_link_to_form,
	getdate,
	now_datetime,
	nowdate,today,formatdate, get_first_day, get_last_day 
)
from frappe import _, msgprint
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
		final_payment_dict = dict()
		for item in self.items:
			print("==========final_payment_dict",final_payment_dict)
			if item.supplier in final_payment_dict:
				final_payment_dict.get(item.supplier).append(item)
			else:
				items = []
				items.append(item)
				final_payment_dict[item.supplier]=items
		print("================",final_payment_dict)
		pe_list = []
		for supplier in final_payment_dict:
			amount =0
			pe_doc = frappe.new_doc('Payment Entry')
			pe_doc.payment_type ='Pay'
			pe_doc.mode_of_payment = self.mode_of_payment
			pe_doc.paid_from = self.payment_account
			pe_doc.paid_from_account_currency = self.account_currency
			pe_doc.party_type ='Supplier'
			pe_doc.party = supplier
			pe_doc.source_exchange_rate = 1
			pe_doc.bulk_payment_process = self.name
			pe_doc.reference_no = self.reference_no
			pe_doc.reference_date = self.reference_date
			for row in final_payment_dict.get(supplier):
				print("===========row========",row)
				amount = amount + row.amount
				total_discount=self.check_discount(row.invoice_no)
				amount = amount - total_discount
				print("************", total_discount)
				pe_doc.append('references',{
					'reference_doctype':'Purchase Invoice',
					'reference_name':row.invoice_no,
					'grand_total':row.invoice_amount,
					'outstanding_amount':row.outstanding_amount,
					'allocated_amount':row.amount,
					'discount':total_discount
					})
			pe_doc.paid_amount = amount
			pe_doc.received_amount = amount
			pe_doc.save()
			pe_list.append(pe_doc.name)
			pe_doc.submit()
		self.show_list_created_message("Payment Entry", pe_list)
		self.payment_completed=1
	def check_discount(self,invoice_no):
		total_discount = 0
		doc=frappe.get_doc("Purchase Invoice",invoice_no)
		if doc:
			has_payment_schedule = hasattr(doc, "payment_schedule") and doc.payment_schedule
			if hasattr(doc, "payment_schedule") and doc.payment_schedule:
				for term in doc.payment_schedule:
					if not term.discounted_amount and term.discount and getdate(nowdate()) <= term.discount_date:
						if term.discount_type == "Percentage":
							discount_amount = flt(doc.get("grand_total")) * (term.discount / 100)
						else:
							discount_amount = term.discount

						discount_amount_in_foreign_currency = discount_amount * doc.get("conversion_rate", 1)

						
						# received_amount -= discount_amount
						# paid_amount -= discount_amount_in_foreign_currency

						total_discount += discount_amount

				if total_discount:
					money = frappe.utils.fmt_money(total_discount, currency=doc.get("currency"))
					frappe.msgprint(_("Discount of {} applied as per Payment Term").format(money), alert=1)

			return total_discount
	
	def show_list_created_message(self, doctype, doc_list=None):
		if not doc_list:
			return

		frappe.flags.mute_messages = False
		if doc_list:
			doc_list = [get_link_to_form(doctype, p) for p in doc_list]
			msgprint(_("Payment Entry {0} created").format(comma_and(doc_list)))

	@frappe.whitelist()
	# def get_invoices_with_filters(upto_due_date=None, from_invoice_date=None, to_invoice_date=None, supplier_group=None, order_by=None, sort_by=None):
	def get_invoices_with_filters(self):
		if self.upto_due_date and self.from_invoice_date and self.to_invoice_date:
			purchase_invoice_list = frappe.db.sql("""SELECT * from `tabPurchase Invoice` pi where pi.outstanding_amount != 0 and pi.docstatus = 1 and pi.due_date <= '{0}' and pi.posting_date between '{1}' and '{2}' order by {3} {4}""".format(self.upto_due_date,self.from_invoice_date,self.to_invoice_date,self.order_by,self.sort_as),as_dict=1,debug=1)
		elif self.upto_due_date and not(self.from_invoice_date and self.to_invoice_date):
			purchase_invoice_list = frappe.db.sql("""SELECT * from `tabPurchase Invoice` pi where pi.outstanding_amount != 0 and pi.docstatus = 1 and pi.due_date <= '{0}' order by {1} {2}""".format(self.upto_due_date,self.order_by,self.sort_as),as_dict=1,debug=1)
		elif not self.upto_due_date and (self.from_invoice_date and self.to_invoice_date):
			purchase_invoice_list = frappe.db.sql("""SELECT * from `tabPurchase Invoice` pi where pi.outstanding_amount != 0 and pi.docstatus = 1 and pi.posting_date between '{0}' and '{1}' order by {2} {3}""".format(self.from_invoice_date,self.to_invoice_date,self.order_by,self.sort_as),as_dict=1,debug=1)
		else :
			purchase_invoice_list = frappe.db.sql("""SELECT * from `tabPurchase Invoice` pi where pi.outstanding_amount != 0 and pi.docstatus = 1  order by {0} {1}""".format(self.order_by,self.sort_as),as_dict=1,debug=1)
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