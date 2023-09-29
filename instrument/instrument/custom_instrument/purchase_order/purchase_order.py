from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.desk.form.load import get_attachments
from zipfile import ZipFile
import os, shutil
from frappe.utils import call_hook_method, cint, cstr, encode, get_files_path, get_hook_method, random_string, strip
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
from dateutil.relativedelta import relativedelta
from frappe.utils import (
	cint,
	date_diff,
	flt,
	get_datetime,
	get_link_to_form,
	getdate,
	nowdate,
	time_diff_in_hours,
)
import datetime
from datetime import date,timedelta
from erpnext.buying.doctype.purchase_order.purchase_order import make_purchase_receipt
def on_submit(doc, method = None):
	prepare_zip_attachment_for_po(doc, method)
	file_att = []
	file_att = [frappe.attach_print(doc.doctype, doc.name, file_name=doc.name)]
	attachments = frappe.db.sql(""" SELECT file_name  FROM tabFile 
				WHERE attached_to_name = '{0}'""".format(doc.name),as_dict=1)
	
	if attachments:
		for row in attachments:
			_file = frappe.get_doc("File", {"file_name": row.file_name})
			content = _file.get_content()
			if not content:
				return
			attachment_list = {'fname':row.file_name,'fcontent':content}
			file_att.append(attachment_list)
	sender = frappe.db.get_value("Email Setting",{"email_name": "Purchase Order Email"},"email_id")
	recipient = doc.contact_email
	rushabh_sett = frappe.get_single("Rushabh Settings")
	if recipient:
		message = "Purchase Order : " + rushabh_sett.url + '/app/purchase-order/{0}'.format(doc.name) + " " + "You can check attachments here" + " " 
		for row in attachments:
			file_url_email = frappe.db.get_value("File",{'file_name':row.get('file_name')},'file_url')
			message+= rushabh_sett.url + file_url_email
			message+= " " + ","

		frappe.sendmail(
			sender = sender,
			recipients = recipient,
			subject = "Purchase Order : {0}".format(doc.name),
			message = message
			# message = "Purchase Order : " + "https://uatrushabhinstruments.indictranstech.com/app/purchase-order/{0}".format(doc.name) +" "+ "URL :"+ "localhost:8000{0}".format(file_url_email),
			# attachments = file_att,
			)
	

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_engineering_revisions_for_filter(doctype, txt, searchfield, start, page_len, filters):
	return frappe.db.sql(""" SELECT name FROM `tabEngineering Revision` where item_code = '{0}' """.format(filters.get("item_code")))

def after_insert(doc,method):
	pdf_data=frappe.attach_print('Purchase Order',doc.name, print_format='Purchase Order Print')
	
	_file = frappe.get_doc({
	"doctype": "File",
	"file_name": pdf_data.get('fname'),
	"attached_to_doctype": "Purchase Order",
	"attached_to_name": doc.name,
	"is_private": 1,
	"content": pdf_data.get('fcontent')
	})
	_file.save()

	p_file = frappe.get_doc({
	"doctype": "File",
	"file_name": pdf_data.get('fname'),
	# "attached_to_doctype": "Purchase Order",
	# "attached_to_name": doc.name,
	"is_private": 0,
	"content": pdf_data.get('fcontent'),
	"email_log_check":1
	})
	p_file.save()
def validate(doc,method):
	if doc.items:
		for item in doc.items:
			engineering_revision = frappe.db.get_value("Item",{'item_code':item.item_code},'engineering_revision')
			item.default_engineering_revision = engineering_revision
	frappe.db.sql("""delete from `tabFile` where attached_to_doctype='Purchase Order' and attached_to_name=%s""",
		(doc.name))
	if not doc.get("__islocal"):
		# frappe.db.sql("""DELETE from `tabFile` where attached_to_doctype='Purchase Order' and attached_to_name=%s""",
		# 	(doc.name))
		pdf_data=frappe.attach_print('Purchase Order',doc.name, print_format='Purchase Order Print')
		
		_file = frappe.get_doc({
		"doctype": "File",
		"file_name": pdf_data.get('fname'),
		"attached_to_doctype": "Purchase Order",
		"attached_to_name": doc.name,
		"is_private": 1,
		"content": pdf_data.get('fcontent')
		})
		_file.save()

		p_file = frappe.get_doc({
		"doctype": "File",
		"file_name": pdf_data.get('fname'),
		# "attached_to_doctype": "Purchase Order",
		# "attached_to_name": doc.name,
		"is_private": 0,
		"content": pdf_data.get('fcontent'),
		"email_log_check":1
		})
		p_file.save()

# def attach_purchasing_docs(doc, method):
# 	for row in doc.items:
# 		if row.item_code and row.engineering_revision:
# 			purchasing_package = frappe.db.sql("""SELECT purchasing_package_name from `tabPurchasing Package Table` a join `tabEngineering Revision` b on a.parent = b.name where b.name = '{0}'""".format(row.engineering_revision),as_dict=1,debug=1)
# 			purchasing_package_list = [item.purchasing_package_name for item in purchasing_package]
# 			er_doc = frappe.get_doc("Engineering Revision",row.engineering_revision)
# 			if er_doc:
# 				for i in er_doc.other_engineering_revision:
# 					if i.revision:
# 						er_purchasing_package = frappe.db.sql("""SELECT purchasing_package_name from `tabPurchasing Package Table` a join `tabEngineering Revision` b on a.parent = b.name where b.name = '{0}'""".format(i.revision),as_dict=1,debug=1)
# 						if er_purchasing_package:
# 							for p in er_purchasing_package:
# 								purchasing_package_list.append(p.purchasing_package_name)
# 					else:
# 						if i.purchase_package_name:
# 							purchasing_package_list.append(i.purchase_package_name)
# 			for col in purchasing_package_list:
# 				package_doc = frappe.get_doc("Package Document",col)
# 				"""Copy attachments from `package document`"""
# 				from frappe.desk.form.load import get_attachments
# 				attachments = get_attachments(package_doc.doctype, package_doc.name)

# 				#loop through attachments
# 				# for attach_item in get_attachments(package_doc.doctype, package_doc.name):
# 					# save attachments to new doc
# 					# _file = frappe.get_doc({
# 					# 	"doctype": "File",
# 					# 	"file_url": attach_item.file_url,
# 					# 	"file_name": attach_item.file_name,
# 					# 	"attached_to_name": doc.name,
# 					# 	"attached_to_doctype": doc.doctype,
# 					# 	"folder": "Home"})
# 					# _file.save()
# 				# path = os.getcwd()
# 				# file = open("currentsite.txt","r")
# 				# sitename = file.read()
# 				file_path = os.path.realpath(get_files_path(is_private=1))
# 				full_path = file_path+ "/"+row.engineering_revision+"_"+doc.name+".zip"
# 				# full_path = path+"/"+sitename+"private/files/"+row.engineering_revision+"_"+doc.name+".zip"
# 				file_name = row.engineering_revision+"_"+doc.name+".zip"
# 				file_url = '/private/files/'+file_name
# 				if len(attachments) > 0 :
# 					with ZipFile(full_path,'w') as zip:
# 						for i in attachments:
# 							file_doc = frappe.get_doc("File",{'file_url':i.file_url})
# 							full_file_path = file_doc.get_full_path()
# 							zip.write(full_file_path)
# 					file_doc = frappe.new_doc("File")
# 					file_doc.file_name =file_name
# 					file_doc.folder = "Home/Attachments"
# 					file_doc.attached_to_doctype = doc.doctype
# 					file_doc.attached_to_name = doc.name
# 					file_doc.file_url = file_url
# 					file_doc.insert(ignore_permissions=True)
# 					frappe.db.commit()
# 					doc.reload()
	# for row in doc.items:
	# 	if row.item_code and row.engineering_revision:
	# 		purchasing_package = frappe.db.sql("""SELECT purchasing_package_name from `tabPurchasing Package Table` a join `tabEngineering Revision` b on a.parent = b.name where b.name = '{0}'""".format(row.engineering_revision),as_dict=1,debug=1)
	# 		purchasing_package_list = [item.purchasing_package_name for item in purchasing_package]
	# 		for row in purchasing_package_list:
	# 			package_doc = frappe.get_doc("Package Document",row)
	# 			"""Copy attachments from `package doc`"""
	# 			from frappe.desk.form.load import get_attachments

	# 			#loop through attachments
	# 			for attach_item in get_attachments(package_doc.doctype, package_doc.name):

	# 				#save attachments to new doc
	# 				_file = frappe.get_doc({
	# 					"doctype": "File",
	# 					"file_url": attach_item.file_url,
	# 					"file_name": attach_item.file_name,
	# 					"attached_to_name": doc.name,
	# 					"attached_to_doctype": doc.doctype,
	# 					"folder": "Home/Attachments"})
	# 				_file.save()



#Create ZIP File and Attach

def prepare_zip_attachment_for_po(doc, method):
	all_files = []
	for row in doc.items:
		if not row.engineering_revision:
			row.engineering_revision=frappe.db.get_value("Engineering Revision", {"item_code":row.item_code, "is_default":True, "is_active":True}, "name")
		if row.item_code and row.engineering_revision:
			engineering_revision_doc(row, all_files)
	if all_files:
		create_zip_file(row, all_files)
		doc.reload()

def engineering_revision_doc(row, all_files): 
	purchasing_package_list = []
	purchasing_package = frappe.db.sql("""SELECT purchasing_package_name from `tabPurchasing Package Table` a join `tabEngineering Revision` b on a.parent = b.name where b.name = '{0}'""".format(row.get("engineering_revision")),as_dict=1,debug=False)
	purchasing_package_list = [item.get('purchasing_package_name') for item in purchasing_package]

	# file_path = os.path.realpath(get_files_path(is_private=1))
	file_path = get_files_path(is_private=1)
	full_path = file_path+ "/"+row.get("item_code")
	os.mkdir(full_path)
	all_files.append(full_path)

	for col in purchasing_package_list:
		package_doc = frappe.get_doc("Package Document",col)
		from frappe.desk.form.load import get_attachments
		attachments = get_attachments(package_doc.doctype, package_doc.name)
		create_folder_with_file(attachments, full_path)

	er_doc = frappe.get_doc("Engineering Revision",row.get("engineering_revision"))
	other_dict={}
	for i in er_doc.other_engineering_revision:
		if i.revision and not i.exclude_purchasing_package:
			other_dict["item_code"]=i.item_code
			other_dict["parent"]=row.get("parent")
			other_dict["engineering_revision"]=i.revision
		elif i.purchase_package_name and not i.exclude_purchasing_package:
			other_dict["item_code"]=i.item_code
			other_dict["parent"]=row.get("parent")
			other_dict["engineering_revision"]="_".join(i.purchase_package_name.split("_")[0:2])
		else:
			if not i.exclude_purchasing_package:
				other_dict["item_code"]=i.item_code
				other_dict["parent"]=row.get("parent")
				other_dict["engineering_revision"]=frappe.db.get_value("Engineering Revision", {"item_code":i.item_code, "is_default":True, "is_active":True}, "name")
		engineering_revision_doc(other_dict, all_files)


def create_folder_with_file(attachments, full_path):
	for i in attachments:
		file_doc = frappe.get_doc("File",{'file_url':i.file_url})
		with open(full_path+f"/{i.file_name}","wb") as f:
			try:
				f.write(file_doc.get_content())
			except Exception as e:
				print(e)

def create_zip_file(row, all_files):
	file_path = get_files_path(is_private=1)
	zip_full_path = file_path+ "/"+row.engineering_revision+"_"+row.parent+".zip"
	file_name = row.engineering_revision+"_"+row.parent+".zip"
	file_url = '/private/files/'+file_name
	p_file_url = '/files/' + file_name

	with ZipFile(zip_full_path,'w') as zip:
		for full_path in all_files:
			for dirname, subdirs, files in os.walk(full_path):
				zip.write(dirname)
				for filename in files:
					zip.write(os.path.join(dirname, filename))
			shutil.rmtree(full_path)
	file_doc = frappe.new_doc("File")
	file_doc.file_name =file_name
	file_doc.folder = "Home/Attachments"
	file_doc.attached_to_doctype = row.parenttype
	file_doc.attached_to_name = row.parent
	file_doc.file_url = file_url
	file_doc.insert(ignore_permissions=True)
	frappe.db.commit()

	p_file_doc = frappe.copy_doc(file_doc)
	p_file_doc.is_private = 0
	p_file_doc.attached_to_doctype = ''
	p_file_doc.attached_to_name = ''
	p_file_doc.email_log_check = 1
	p_file_doc.insert(ignore_permissions=True)
	frappe.db.commit()

	update_to_p_file = frappe.get_doc("File",p_file_doc.name)
	update_to_p_file.is_private = 0
	update_to_p_file.save(ignore_permissions=1)

	# p_file_doc = frappe.new_doc("File")
	# p_file_doc.file_name =file_name
	# p_file_doc.is_private =0
	# p_file_doc.email_log_check=1
	# p_file_doc.folder = "Home/Attachments"
	# # p_file_doc.attached_to_doctype = row.parenttype
	# # p_file_doc.attached_to_name = row.parent
	# # p_file_doc.file_url = p_file_url
	# p_file_doc.insert(ignore_permissions=True)
	# frappe.db.commit()

@frappe.whitelist()
def set_min_order_qty(doc):
	doc = json.loads(doc)
	min_order_qty_list = []
	if doc:
		if doc.get("items"):
			for row in doc.get("items"):
				min_order_qty = frappe.db.get_value("Item",{'item_code':row.get("item_code")},'min_order_qty')
				if row.get('qty') < min_order_qty:
					row['qty'] = min_order_qty
					min_order_qty_list.append({'item_code':row.get('item_code'),'qty':min_order_qty})
		return min_order_qty_list

# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

import json

import frappe
from frappe import _, msgprint
from frappe.desk.notifications import clear_doctype_notifications
from frappe.model.mapper import get_mapped_doc
from frappe.utils import cint, cstr, flt

from erpnext.accounts.doctype.sales_invoice.sales_invoice import (
	unlink_inter_company_doc,
	update_linked_doc,
	validate_inter_company_party,
)
from erpnext.accounts.doctype.tax_withholding_category.tax_withholding_category import (
	get_party_tax_withholding_details,
)
from erpnext.accounts.party import get_party_account_currency
from erpnext.buying.utils import check_on_hold_or_closed_status, validate_for_items
from erpnext.controllers.buying_controller import BuyingController
from erpnext.setup.doctype.item_group.item_group import get_item_group_defaults
from erpnext.stock.doctype.item.item import get_item_defaults, get_last_purchase_details
from erpnext.stock.stock_balance import get_ordered_qty, update_bin_qty
from erpnext.stock.utils import get_bin

form_grid_templates = {"items": "templates/form_grid/item_grid.html"}


class PurchaseOrder(BuyingController):
	def __init__(self, *args, **kwargs):
		super(PurchaseOrder, self).__init__(*args, **kwargs)
		self.status_updater = [
			{
				"source_dt": "Purchase Order Item",
				"target_dt": "Material Request Item",
				"join_field": "material_request_item",
				"target_field": "ordered_qty",
				"target_parent_dt": "Material Request",
				"target_parent_field": "per_ordered",
				"target_ref_field": "stock_qty",
				"source_field": "stock_qty",
				"percent_join_field": "material_request",
			}
		]

	def onload(self):
		supplier_tds = frappe.db.get_value("Supplier", self.supplier, "tax_withholding_category")
		self.set_onload("supplier_tds", supplier_tds)

	def validate(self):
		super(PurchaseOrder, self).validate()

		self.set_status()

		# apply tax withholding only if checked and applicable
		self.set_tax_withholding()

		self.validate_supplier()
		self.validate_schedule_date()
		validate_for_items(self)
		self.check_on_hold_or_closed_status()

		self.validate_uom_is_integer("uom", "qty")
		self.validate_uom_is_integer("stock_uom", "stock_qty")

		self.validate_with_previous_doc()
		self.validate_for_subcontracting()
		self.validate_minimum_order_qty()
		self.validate_bom_for_subcontracting_items()
		self.create_raw_materials_supplied("supplied_items")
		self.set_received_qty_for_drop_ship_items()
		validate_inter_company_party(
			self.doctype, self.supplier, self.company, self.inter_company_order_reference
		)
		self.reset_default_field_value("set_warehouse", "items", "warehouse")

	def validate_with_previous_doc(self):
		super(PurchaseOrder, self).validate_with_previous_doc(
			{
				"Supplier Quotation": {
					"ref_dn_field": "supplier_quotation",
					"compare_fields": [["supplier", "="], ["company", "="], ["currency", "="]],
				},
				"Supplier Quotation Item": {
					"ref_dn_field": "supplier_quotation_item",
					"compare_fields": [
						["project", "="],
						["item_code", "="],
						["uom", "="],
						["conversion_factor", "="],
					],
					"is_child_table": True,
				},
				"Material Request": {
					"ref_dn_field": "material_request",
					"compare_fields": [["company", "="]],
				},
				"Material Request Item": {
					"ref_dn_field": "material_request_item",
					"compare_fields": [["project", "="], ["item_code", "="]],
					"is_child_table": True,
				},
			}
		)

		if cint(frappe.db.get_single_value("Buying Settings", "maintain_same_rate")):
			self.validate_rate_with_reference_doc(
				[["Supplier Quotation", "supplier_quotation", "supplier_quotation_item"]]
			)

	def set_tax_withholding(self):
		if not self.apply_tds:
			return

		tax_withholding_details = get_party_tax_withholding_details(self, self.tax_withholding_category)

		if not tax_withholding_details:
			return

		accounts = []
		for d in self.taxes:
			if d.account_head == tax_withholding_details.get("account_head"):
				d.update(tax_withholding_details)
			accounts.append(d.account_head)

		if not accounts or tax_withholding_details.get("account_head") not in accounts:
			self.append("taxes", tax_withholding_details)

		to_remove = [
			d
			for d in self.taxes
			if not d.tax_amount and d.account_head == tax_withholding_details.get("account_head")
		]

		for d in to_remove:
			self.remove(d)

		# calculate totals again after applying TDS
		self.calculate_taxes_and_totals()

	def validate_supplier(self):
		prevent_po = frappe.db.get_value("Supplier", self.supplier, "prevent_pos")
		if prevent_po:
			standing = frappe.db.get_value("Supplier Scorecard", self.supplier, "status")
			if standing:
				frappe.throw(
					_("Purchase Orders are not allowed for {0} due to a scorecard standing of {1}.").format(
						self.supplier, standing
					)
				)

		warn_po = frappe.db.get_value("Supplier", self.supplier, "warn_pos")
		if warn_po:
			standing = frappe.db.get_value("Supplier Scorecard", self.supplier, "status")
			frappe.msgprint(
				_(
					"{0} currently has a {1} Supplier Scorecard standing, and Purchase Orders to this supplier should be issued with caution."
				).format(self.supplier, standing),
				title=_("Caution"),
				indicator="orange",
			)

		self.party_account_currency = get_party_account_currency("Supplier", self.supplier, self.company)

	def validate_minimum_order_qty(self):
		if not self.get("items"):
			return
		items = list(set(d.item_code for d in self.get("items")))

		itemwise_min_order_qty = frappe._dict(
			frappe.db.sql(
				"""select name, min_order_qty
			from tabItem where name in ({0})""".format(
					", ".join(["%s"] * len(items))
				),
				items,
			)
		)

		itemwise_qty = frappe._dict()
		for d in self.get("items"):
			itemwise_qty.setdefault(d.item_code, 0)
			itemwise_qty[d.item_code] += flt(d.stock_qty)

		for item_code, qty in itemwise_qty.items():
			if flt(qty) < flt(itemwise_min_order_qty.get(item_code)):
				frappe.msgprint(
					_(
						"Item {0}: Ordered qty {1} cannot be less than minimum order qty {2} (defined in Item)."
					).format(item_code, qty, itemwise_min_order_qty.get(item_code))
				)

	def validate_bom_for_subcontracting_items(self):
		if self.is_subcontracted == "Yes":
			for item in self.items:
				if not item.bom:
					frappe.throw(
						_("BOM is not specified for subcontracting item {0} at row {1}").format(
							item.item_code, item.idx
						)
					)

	def get_schedule_dates(self):
		for d in self.get("items"):
			if d.material_request_item and not d.schedule_date:
				d.schedule_date = frappe.db.get_value(
					"Material Request Item", d.material_request_item, "schedule_date"
				)

	@frappe.whitelist()
	def get_last_purchase_rate(self):
		"""get last purchase rates for all items"""

		conversion_rate = flt(self.get("conversion_rate")) or 1.0
		for d in self.get("items"):
			if d.item_code:
				last_purchase_details = get_last_purchase_details(d.item_code, self.name)
				if last_purchase_details:
					d.base_price_list_rate = last_purchase_details["base_price_list_rate"] * (
						flt(d.conversion_factor) or 1.0
					)
					d.discount_percentage = last_purchase_details["discount_percentage"]
					d.base_rate = last_purchase_details["base_rate"] * (flt(d.conversion_factor) or 1.0)
					d.price_list_rate = d.base_price_list_rate / conversion_rate
					d.rate = d.base_rate / conversion_rate
					d.last_purchase_rate = d.rate
				else:

					item_last_purchase_rate = frappe.get_cached_value("Item", d.item_code, "last_purchase_rate")
					if item_last_purchase_rate:
						d.base_price_list_rate = (
							d.base_rate
						) = d.price_list_rate = d.rate = d.last_purchase_rate = item_last_purchase_rate

	# Check for Closed status
	def check_on_hold_or_closed_status(self):
		check_list = []
		for d in self.get("items"):
			if (
				d.meta.get_field("material_request")
				and d.material_request
				and d.material_request not in check_list
			):
				check_list.append(d.material_request)
				check_on_hold_or_closed_status("Material Request", d.material_request)

	def update_requested_qty(self):
		material_request_map = {}
		for d in self.get("items"):
			if d.material_request_item:
				material_request_map.setdefault(d.material_request, []).append(d.material_request_item)

		for mr, mr_item_rows in material_request_map.items():
			if mr and mr_item_rows:
				mr_obj = frappe.get_doc("Material Request", mr)

				if mr_obj.status in ["Stopped", "Cancelled"]:
					frappe.throw(
						_("Material Request {0} is cancelled or stopped").format(mr), frappe.InvalidStatusError
					)

				mr_obj.update_requested_qty(mr_item_rows)

	def update_ordered_qty(self, po_item_rows=None):
		"""update requested qty (before ordered_qty is updated)"""
		item_wh_list = []
		for d in self.get("items"):
			if (
				(not po_item_rows or d.name in po_item_rows)
				and [d.item_code, d.warehouse] not in item_wh_list
				and frappe.get_cached_value("Item", d.item_code, "is_stock_item")
				and d.warehouse
				and not d.delivered_by_supplier
			):
				item_wh_list.append([d.item_code, d.warehouse])
		for item_code, warehouse in item_wh_list:
			update_bin_qty(item_code, warehouse, {"ordered_qty": get_ordered_qty(item_code, warehouse)})

	def check_modified_date(self):
		mod_db = frappe.db.sql("select modified from `tabPurchase Order` where name = %s", self.name)
		date_diff = frappe.db.sql("select '%s' - '%s' " % (mod_db[0][0], cstr(self.modified)))

		if date_diff and date_diff[0][0]:
			msgprint(
				_("{0} {1} has been modified. Please refresh.").format(self.doctype, self.name),
				raise_exception=True,
			)

	def update_status(self, status):
		self.check_modified_date()
		self.set_status(update=True, status=status)
		self.update_requested_qty()
		self.update_ordered_qty()
		if self.is_subcontracted == "Yes":
			self.update_reserved_qty_for_subcontract()

		self.notify_update()
		clear_doctype_notifications(self)

	def on_submit(self):
		super(PurchaseOrder, self).on_submit()

		if self.is_against_so():
			self.update_status_updater()

		self.update_prevdoc_status()
		self.update_requested_qty()
		self.update_ordered_qty()
		self.validate_budget()

		if self.is_subcontracted == "Yes":
			self.update_reserved_qty_for_subcontract()

		frappe.get_doc("Authorization Control").validate_approving_authority(
			self.doctype, self.company, self.base_grand_total
		)

		self.update_blanket_order()

		update_linked_doc(self.doctype, self.name, self.inter_company_order_reference)

	def on_cancel(self):
		super(PurchaseOrder, self).on_cancel()

		if self.is_against_so():
			self.update_status_updater()

		if self.has_drop_ship_item():
			self.update_delivered_qty_in_sales_order()

		if self.is_subcontracted == "Yes":
			self.update_reserved_qty_for_subcontract()

		self.check_on_hold_or_closed_status()

		frappe.db.set(self, "status", "Cancelled")

		self.update_prevdoc_status()

		# Must be called after updating ordered qty in Material Request
		# bin uses Material Request Items to recalculate & update
		self.update_requested_qty()
		self.update_ordered_qty()

		self.update_blanket_order()

		unlink_inter_company_doc(self.doctype, self.name, self.inter_company_order_reference)

	def on_update(self):
		pass

	def update_status_updater(self):
		self.status_updater.append(
			{
				"source_dt": "Purchase Order Item",
				"target_dt": "Sales Order Item",
				"target_field": "ordered_qty",
				"target_parent_dt": "Sales Order",
				"target_parent_field": "",
				"join_field": "sales_order_item",
				"target_ref_field": "stock_qty",
				"source_field": "stock_qty",
			}
		)
		self.status_updater.append(
			{
				"source_dt": "Purchase Order Item",
				"target_dt": "Packed Item",
				"target_field": "ordered_qty",
				"target_parent_dt": "Sales Order",
				"target_parent_field": "",
				"join_field": "sales_order_packed_item",
				"target_ref_field": "qty",
				"source_field": "stock_qty",
			}
		)

	def update_delivered_qty_in_sales_order(self):
		"""Update delivered qty in Sales Order for drop ship"""
		sales_orders_to_update = []
		for item in self.items:
			if item.sales_order and item.delivered_by_supplier == 1:
				if item.sales_order not in sales_orders_to_update:
					sales_orders_to_update.append(item.sales_order)

		for so_name in sales_orders_to_update:
			so = frappe.get_doc("Sales Order", so_name)
			so.update_delivery_status()
			so.set_status(update=True)
			so.notify_update()

	def has_drop_ship_item(self):
		return any(d.delivered_by_supplier for d in self.items)

	def is_against_so(self):
		return any(d.sales_order for d in self.items if d.sales_order)

	def set_received_qty_for_drop_ship_items(self):
		for item in self.items:
			if item.delivered_by_supplier == 1:
				item.received_qty = item.qty

	def update_reserved_qty_for_subcontract(self):
		for d in self.supplied_items:
			if d.rm_item_code:
				stock_bin = get_bin(d.rm_item_code, d.reserve_warehouse)
				stock_bin.update_reserved_qty_for_sub_contracting()

	def update_receiving_percentage(self):
		total_qty, received_qty = 0.0, 0.0
		for item in self.items:
			received_qty += item.received_qty
			total_qty += item.qty
		if total_qty:
			self.db_set("per_received", flt(received_qty / total_qty) * 100, update_modified=False)
		else:
			self.db_set("per_received", 0, update_modified=False)


def item_last_purchase_rate(name, conversion_rate, item_code, conversion_factor=1.0):
	"""get last purchase rate for an item"""

	conversion_rate = flt(conversion_rate) or 1.0

	last_purchase_details = get_last_purchase_details(item_code, name)
	if last_purchase_details:
		last_purchase_rate = (
			last_purchase_details["base_net_rate"] * (flt(conversion_factor) or 1.0)
		) / conversion_rate
		return last_purchase_rate
	else:
		item_last_purchase_rate = frappe.get_cached_value("Item", item_code, "last_purchase_rate")
		if item_last_purchase_rate:
			return item_last_purchase_rate


@frappe.whitelist()
def close_or_unclose_purchase_orders(names, status):
	if not frappe.has_permission("Purchase Order", "write"):
		frappe.throw(_("Not permitted"), frappe.PermissionError)

	names = json.loads(names)
	for name in names:
		po = frappe.get_doc("Purchase Order", name)
		if po.docstatus == 1:
			if status == "Closed":
				if po.status not in ("Cancelled", "Closed") and (po.per_received < 100 or po.per_billed < 100):
					po.update_status(status)
			else:
				if po.status == "Closed":
					po.update_status("Draft")
			po.update_blanket_order()

	frappe.local.message_log = []


def set_missing_values(source, target):
	target.run_method("set_missing_values")
	target.run_method("calculate_taxes_and_totals")


@frappe.whitelist()
def make_purchase_receipt(source_name, target_doc=None):
	def update_item(obj, target, source_parent):
		target.qty = flt(obj.qty) - flt(obj.received_qty)
		target.stock_qty = (flt(obj.qty) - flt(obj.received_qty)) * flt(obj.conversion_factor)
		target.amount = (flt(obj.qty) - flt(obj.received_qty)) * flt(obj.rate)
		target.base_amount = (
			(flt(obj.qty) - flt(obj.received_qty)) * flt(obj.rate) * flt(source_parent.conversion_rate)
		)

	doc = get_mapped_doc(
		"Purchase Order",
		source_name,
		{
			"Purchase Order": {
				"doctype": "Purchase Receipt",
				"field_map": {"supplier_warehouse": "supplier_warehouse"},
				"validation": {
					"docstatus": ["=", 1],
				},
			},
			"Purchase Order Item": {
				"doctype": "Purchase Receipt Item",
				"field_map": {
					"name": "purchase_order_item",
					"parent": "purchase_order",
					"bom": "bom",
					"material_request": "material_request",
					"material_request_item": "material_request_item",
				},
				"postprocess": update_item,
				"condition": lambda doc: abs(doc.received_qty) < abs(doc.qty)
				and doc.delivered_by_supplier != 1,
			},
			"Purchase Taxes and Charges": {"doctype": "Purchase Taxes and Charges", "add_if_empty": True},
		},
		target_doc,
		set_missing_values,
	)

	doc.set_onload("ignore_price_list", True)

	return doc


@frappe.whitelist()
def make_purchase_invoice(source_name, target_doc=None):
	return get_mapped_purchase_invoice(source_name, target_doc)


@frappe.whitelist()
def make_purchase_invoice_from_portal(purchase_order_name):
	doc = get_mapped_purchase_invoice(purchase_order_name, ignore_permissions=True)
	if doc.contact_email != frappe.session.user:
		frappe.throw(_("Not Permitted"), frappe.PermissionError)
	doc.save()
	frappe.db.commit()
	frappe.response["type"] = "redirect"
	frappe.response.location = "/purchase-invoices/" + doc.name


def get_mapped_purchase_invoice(source_name, target_doc=None, ignore_permissions=False):
	def postprocess(source, target):
		target.flags.ignore_permissions = ignore_permissions
		set_missing_values(source, target)
		# Get the advance paid Journal Entries in Purchase Invoice Advance
		if target.get("allocate_advances_automatically"):
			target.set_advances()

		target.set_payment_schedule()

	def update_item(obj, target, source_parent):
		target.amount = flt(obj.amount) - flt(obj.billed_amt)
		target.base_amount = target.amount * flt(source_parent.conversion_rate)
		target.qty = (
			target.amount / flt(obj.rate) if (flt(obj.rate) and flt(obj.billed_amt)) else flt(obj.qty)
		)

		item = get_item_defaults(target.item_code, source_parent.company)
		item_group = get_item_group_defaults(target.item_code, source_parent.company)
		target.cost_center = (
			obj.cost_center
			or frappe.db.get_value("Project", obj.project, "cost_center")
			or item.get("buying_cost_center")
			or item_group.get("buying_cost_center")
		)

	fields = {
		"Purchase Order": {
			"doctype": "Purchase Invoice",
			"field_map": {
				"party_account_currency": "party_account_currency",
				"supplier_warehouse": "supplier_warehouse",
			},
			"field_no_map": ["payment_terms_template"],
			"validation": {
				"docstatus": ["=", 1],
			},
		},
		"Purchase Order Item": {
			"doctype": "Purchase Invoice Item",
			"field_map": {
				"name": "po_detail",
				"parent": "purchase_order",
			},
			"postprocess": update_item,
			"condition": lambda doc: (doc.base_amount == 0 or abs(doc.billed_amt) < abs(doc.amount)),
		},
		"Purchase Taxes and Charges": {"doctype": "Purchase Taxes and Charges", "add_if_empty": True},
	}

	doc = get_mapped_doc(
		"Purchase Order",
		source_name,
		fields,
		target_doc,
		postprocess,
		ignore_permissions=ignore_permissions,
	)
	doc.set_onload("ignore_price_list", True)

	return doc


@frappe.whitelist()
def make_rm_stock_entry(purchase_order, rm_items):
	rm_items_list = rm_items

	if isinstance(rm_items, str):
		rm_items_list = json.loads(rm_items)
	elif not rm_items:
		frappe.throw(_("No Items available for transfer"))

	if rm_items_list:
		fg_items = list(set(d["item_code"] for d in rm_items_list))
	else:
		frappe.throw(_("No Items selected for transfer"))

	if purchase_order:
		purchase_order = frappe.get_doc("Purchase Order", purchase_order)

	if fg_items:
		items = tuple(set(d["rm_item_code"] for d in rm_items_list))
		item_wh = get_item_details(items)

		stock_entry = frappe.new_doc("Stock Entry")
		stock_entry.purpose = "Send to Subcontractor"
		stock_entry.purchase_order = purchase_order.name
		stock_entry.supplier = purchase_order.supplier
		stock_entry.supplier_name = purchase_order.supplier_name
		stock_entry.supplier_address = purchase_order.supplier_address
		stock_entry.address_display = purchase_order.address_display
		stock_entry.company = purchase_order.company
		stock_entry.to_warehouse = purchase_order.supplier_warehouse
		stock_entry.set_stock_entry_type()

		for item_code in fg_items:
			for rm_item_data in rm_items_list:
				if rm_item_data["item_code"] == item_code:
					rm_item_code = rm_item_data["rm_item_code"]
					items_dict = {
						rm_item_code: {
							"po_detail": rm_item_data.get("name"),
							"item_name": rm_item_data["item_name"],
							"description": item_wh.get(rm_item_code, {}).get("description", ""),
							"qty": rm_item_data["qty"],
							"from_warehouse": rm_item_data["warehouse"],
							"stock_uom": rm_item_data["stock_uom"],
							"serial_no": rm_item_data.get("serial_no"),
							"batch_no": rm_item_data.get("batch_no"),
							"main_item_code": rm_item_data["item_code"],
							"allow_alternative_item": item_wh.get(rm_item_code, {}).get("allow_alternative_item"),
						}
					}
					stock_entry.add_to_stock_entry_detail(items_dict)
		return stock_entry.as_dict()
	else:
		frappe.throw(_("No Items selected for transfer"))
	return purchase_order.name


def get_item_details(items):
	item_details = {}
	for d in frappe.db.sql(
		"""select item_code, description, allow_alternative_item from `tabItem`
		where name in ({0})""".format(
			", ".join(["%s"] * len(items))
		),
		items,
		as_dict=1,
	):
		item_details[d.item_code] = d

	return item_details


def get_list_context(context=None):
	from erpnext.controllers.website_list_for_contact import get_list_context

	list_context = get_list_context(context)
	list_context.update(
		{
			"show_sidebar": True,
			"show_search": True,
			"no_breadcrumbs": True,
			"title": _("Purchase Orders"),
		}
	)
	return list_context


@frappe.whitelist()
def update_status(status, name):
	po = frappe.get_doc("Purchase Order", name)
	po.update_status(status)
	po.update_delivered_qty_in_sales_order()


@frappe.whitelist()
def make_inter_company_sales_order(source_name, target_doc=None):
	from erpnext.accounts.doctype.sales_invoice.sales_invoice import make_inter_company_transaction

	return make_inter_company_transaction("Purchase Order", source_name, target_doc)


@frappe.whitelist()
def get_materials_from_supplier(purchase_order, po_details):
	if isinstance(po_details, str):
		po_details = json.loads(po_details)

	doc = frappe.get_cached_doc("Purchase Order", purchase_order)
	doc.initialized_fields()
	doc.purchase_orders = [doc.name]
	doc.get_available_materials()

	if not doc.available_materials:
		frappe.throw(
			_("Materials are already received against the purchase order {0}").format(purchase_order)
		)

	return make_return_stock_entry_for_subcontract(doc.available_materials, doc, po_details)


def make_return_stock_entry_for_subcontract(available_materials, po_doc, po_details):
	ste_doc = frappe.new_doc("Stock Entry")
	ste_doc.purpose = "Material Transfer"
	ste_doc.purchase_order = po_doc.name
	ste_doc.company = po_doc.company
	ste_doc.is_return = 1

	for key, value in available_materials.items():
		if not value.qty:
			continue

		if value.batch_no:
			for batch_no, qty in value.batch_no.items():
				if qty > 0:
					add_items_in_ste(ste_doc, value, value.qty, po_details, batch_no)
		else:
			add_items_in_ste(ste_doc, value, value.qty, po_details)

	ste_doc.set_stock_entry_type()
	ste_doc.calculate_rate_and_amount()

	return ste_doc


def add_items_in_ste(ste_doc, row, qty, po_details, batch_no=None):
	item = ste_doc.append("items", row.item_details)

	po_detail = list(set(row.po_details).intersection(po_details))
	item.update(
		{
			"qty": qty,
			"batch_no": batch_no,
			"basic_rate": row.item_details["rate"],
			"po_detail": po_detail[0] if po_detail else "",
			"s_warehouse": row.item_details["t_warehouse"],
			"t_warehouse": row.item_details["s_warehouse"],
			"item_code": row.item_details["rm_item_code"],
			"subcontracted_item": row.item_details["main_item_code"],
			"serial_no": "\n".join(row.serial_no) if row.serial_no else "",
		}
	)


@frappe.whitelist()
def make_consolidated_pick_list(source_name, target_doc=None):
	from frappe.model.mapper import get_mapped_doc
	target_doc = get_mapped_doc("Purchase Order", source_name, {
			"Purchase Order": {
				"doctype": "Consolidated Pick List",
				"field_map": {
					"name": "purchase_order"
				},
			}
		})
	return target_doc


@frappe.whitelist()
def log_for_email_expiry():
	rushabh_sett = frappe.get_single("Rushabh Settings")
	if rushabh_sett.expiry_days:
		p_files = frappe.db.sql("""SELECT name from `tabFile` where email_log_check =1""",as_dict=1)
		if p_files:
			for row in p_files:
				file_doc =frappe.get_doc("File",row.get('name'))
				if file_doc:
					today_date = date.today()
					file_creation_date = file_doc.creation
					expir_days = (today_date - file_creation_date.date())
					if expir_days.days > rushabh_sett.expiry_days:
						frappe.db.sql("""delete from `tabFile` where name=%s""",(row.get('name')))


@frappe.whitelist()
def create_bulk_pr(data):
	data = json.loads(data)
	data = data.get('purchase_order_data')
	try:
		for row in data:
			if row.get('name'):
				po_doc = frappe.get_doc("Purchase Order",row.get('name'))
				if po_doc.docstatus == 1:
					pr = make_purchase_receipt(po_doc.name)
				else:
					frappe.throw("Please Submit Purchase Order {0}".format(row.get('name')))
	except Exception as e:
		raise e

@frappe.whitelist()
def make_purchase_receipt(source_name, target_doc=None, ignore_permissions=True):
	def update_item(obj, target, source_parent):
		target.qty = flt(obj.qty) - flt(obj.received_qty)
		target.stock_qty = (flt(obj.qty) - flt(obj.received_qty)) * flt(obj.conversion_factor)
		target.amount = (flt(obj.qty) - flt(obj.received_qty)) * flt(obj.rate)
		target.base_amount = (
			(flt(obj.qty) - flt(obj.received_qty)) * flt(obj.rate) * flt(source_parent.conversion_rate)
		)

	doc = get_mapped_doc(
		"Purchase Order",
		source_name,
		{
			"Purchase Order": {
				"doctype": "Purchase Receipt",
				"field_map": {"supplier_warehouse": "supplier_warehouse"},
				"validation": {
					"docstatus": ["=", 1],
				},
			},
			"Purchase Order Item": {
				"doctype": "Purchase Receipt Item",
				"field_map": {
					"name": "purchase_order_item",
					"parent": "purchase_order",
					"bom": "bom",
					"material_request": "material_request",
					"material_request_item": "material_request_item",
				},
				"postprocess": update_item,
				"condition": lambda doc: abs(doc.received_qty) < abs(doc.qty)
				and doc.delivered_by_supplier != 1,
			},
			"Purchase Taxes and Charges": {"doctype": "Purchase Taxes and Charges", "add_if_empty": True},
		},
		target_doc,
		set_missing_values,
	)

	doc.set_onload("ignore_price_list", True)
	doc.insert(ignore_permissions=True)
	frappe.msgprint("PR Created {0}".format(doc.name))
	