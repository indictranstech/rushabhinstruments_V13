# from __future__ import unicode_literals
from . import __version__ as app_version
# import frappe
# from frappe import _, msgprint
# from frappe.utils import cint, cstr, flt

app_name = "instrument"
app_title = "instrument"
app_publisher = "instrument"
app_description = "instrument"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "test@gmail.com"
app_license = "MIT"

# Includes in <head>
# ------------------

fixtures = ['Custom Field', 'Property Setter', 'Print Format', 'Role', 'Letter Head', 'Print Style', 'Print Settings', 'Email Template']

doctype_js = {
	
	"Purchase Order": "instrument/custom_instrument/purchase_order/purchase_order.js",
	"Purchase Receipt": "instrument/custom_instrument/purchase_receipt/purchase_receipt.js",
	"Purchase Invoice": "instrument/custom_instrument/purchase_invoice/purchase_invoice.js",
	"Request for Quotation": "instrument/custom_instrument/request_for_quotation/request_for_quotation.js",
	"Supplier Quotation": "instrument/custom_instrument/supplier_quotation/supplier_quotation.js",
	"Sales Order": "instrument/custom_instrument/sales_order/sales_order.js",
	"Sales Invoice": "instrument/custom_instrument/sales_invoice/sales_invoice.js",
	"Delivery Note": "instrument/custom_instrument/delivery_note/delivery_note.js",
	"Work Order": "instrument/custom_instrument/work_order/work_order.js",
	"Stock Entry": "instrument/custom_instrument/stock_entry/stock_entry.js",
	"Item": "instrument/custom_instrument/item/item.js",
	"BOM":"instrument/custom_instrument/bom/bom.js",
	"Job Card" : "instrument/custom_instrument/job_card/job_card.js",
	"Material Request" : "instrument/custom_instrument/material_request/material_request.js",
	"Production Plan" : "instrument/custom_instrument/production_plan/production_plan.js",
	"Task" : "instrument/custom_instrument/task/task.js"
 
}

# include js, css files in header of desk.html
# app_include_css = "/assets/instrument/css/instrument.css"
# app_include_js = "/assets/instrument/js/instrument.js"

# include js, css files in header of web template
# web_include_css = "/assets/instrument/css/instrument.css"
# web_include_js = "/assets/instrument/js/instrument.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "instrument/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
doctype_list_js = {"Work Order" : "instrument/custom_instrument/work_order/work_order_list.js"}
doctype_tree_js = {"BOM" : "instrument/custom_instrument/bom/bom_tree.js","Task":"instrument/custom_instrument/task/task_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------
doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
   "Purchase Order" :{
		"on_submit" : "instrument.instrument.custom_instrument.purchase_order.purchase_order.on_submit",
		"validate" : "instrument.instrument.custom_instrument.purchase_order.purchase_order.validate",
		"after_insert":"instrument.instrument.custom_instrument.purchase_order.purchase_order.after_insert"
	},
	"Purchase Receipt" :{
		"on_submit" : "instrument.instrument.custom_instrument.purchase_receipt.purchase_receipt.on_submit",
		"validate" : "instrument.instrument.custom_instrument.purchase_receipt.purchase_receipt.validate",
		"after_insert":"instrument.instrument.custom_instrument.purchase_receipt.purchase_receipt.after_insert"
	},
	"Purchase Invoice" :{
		"on_submit" : "instrument.instrument.custom_instrument.purchase_invoice.purchase_invoice.on_submit",
		"validate":"instrument.instrument.custom_instrument.purchase_invoice.purchase_invoice.validate",
		"after_insert":"instrument.instrument.custom_instrument.purchase_invoice.purchase_invoice.after_insert"
	},
	"Request for Quotation" :{
		"on_submit" : "instrument.instrument.custom_instrument.request_for_quotation.request_for_quotation.on_submit",
		"validate" : "instrument.instrument.custom_instrument.request_for_quotation.request_for_quotation.validate",
		"after_insert":"instrument.instrument.custom_instrument.request_for_quotation.request_for_quotation.after_insert"
	},
	"Supplier Quotation" :{
		"on_submit" : "instrument.instrument.custom_instrument.supplier_quotation.supplier_quotation.on_submit"
	},
	"Sales Order" :{
		"on_submit" : "instrument.instrument.custom_instrument.sales_order.sales_order.on_submit",
		"validate":"instrument.instrument.custom_instrument.sales_order.sales_order.validate",
		"after_insert":"instrument.instrument.custom_instrument.sales_order.sales_order.after_insert"
	},
	"Sales Invoice" :{
		"on_submit" : "instrument.instrument.custom_instrument.sales_invoice.sales_invoice.on_submit",
		"validate":"instrument.instrument.custom_instrument.sales_invoice.sales_invoice.validate",
		"after_insert":"instrument.instrument.custom_instrument.sales_invoice.sales_invoice.after_insert"
	},
	"Delivery Note" :{
		"on_submit" : "instrument.instrument.custom_instrument.delivery_note.delivery_note.on_submit",
		"validate":"instrument.instrument.custom_instrument.delivery_note.delivery_note.validate",
		"after_insert":"instrument.instrument.custom_instrument.delivery_note.delivery_note.after_insert"
	},
	"Blanket Order" :{
		"on_submit" : "instrument.instrument.custom_instrument.blanket_order.blanket_order.on_submit"
	},
	"Serial No" : {
	"autoname" : "instrument.instrument.custom_instrument.serial_no.serial_no.autoname"
	},
	"BOM" : {
	"validate" :  "instrument.instrument.custom_instrument.bom.bom.validate",
	"on_update" : "instrument.instrument.custom_instrument.bom.bom.validate",
	"on_submit" : "instrument.instrument.custom_instrument.bom.bom.disable_old_boms",
	"on_update_after_submit": "instrument.instrument.custom_instrument.bom.bom.disable_old_boms"
	},
	"Work Order" : {
	"after_insert" : ["instrument.instrument.custom_instrument.work_order.work_order.check_stock","instrument.instrument.custom_instrument.work_order.work_order.after_insert"],
	"on_update_after_submit" : ["instrument.instrument.custom_instrument.work_order.work_order.check_stock","instrument.instrument.custom_instrument.work_order.work_order.disable_bom"],
	"on_update" : ["instrument.instrument.custom_instrument.work_order.work_order.check_stock","instrument.instrument.custom_instrument.work_order.work_order.disable_bom"],
	"validate" : ["instrument.instrument.custom_instrument.work_order.work_order.add_bom_level","instrument.instrument.custom_instrument.work_order.work_order.validate","instrument.instrument.custom_instrument.work_order.work_order.label_img"],
	"on_submit" :"instrument.instrument.custom_instrument.work_order.work_order.on_submit",
	"on_cancel":"instrument.instrument.custom_instrument.work_order.work_order.disable_bom",
	"on_change":"instrument.instrument.custom_instrument.work_order.work_order.disable_bom"
	},
	"Item" : {
	"validate" :["instrument.instrument.custom_instrument.item.item.validate","instrument.instrument.custom_instrument.item.item.label_img"],
	"on_update":"instrument.instrument.custom_instrument.item.item.disable_old_boms",
	"after_insert":"instrument.instrument.custom_instrument.item.item.after_insert"
	},
	"Production Plan":{
	# "on_update" : "instrument.instrument.custom_instrument.production_plan.production_plan.on_update",
	"validate" : "instrument.instrument.custom_instrument.production_plan.production_plan.validate",
	"after_insert":"instrument.instrument.custom_instrument.production_plan.production_plan.after_insert"

	},
	"Batch" : {
	"autoname" : "instrument.instrument.custom_instrument.batch.batch.autoname",
	"validate" : ["instrument.instrument.custom_instrument.batch.batch.label_img","instrument.instrument.custom_instrument.batch.batch.validate"],
	"after_insert":["instrument.instrument.custom_instrument.batch.batch.after_insert"]
	},
	"Stock Entry" : {
	"validate" : ["instrument.instrument.custom_instrument.stock_entry.stock_entry.validate","instrument.instrument.custom_instrument.stock_entry.stock_entry.label_img"],
	"on_submit":["instrument.instrument.custom_instrument.stock_entry.stock_entry.on_submit"],
	"on_cancel":["instrument.instrument.custom_instrument.stock_entry.stock_entry.on_cancel"],
	"after_insert":"instrument.instrument.custom_instrument.stock_entry.stock_entry.after_insert"
 	},
 	"Item Attribute" : {
 	"validate" : "instrument.instrument.custom_instrument.item_attribute.item_attribute.validate",
 	"after_insert" : "instrument.instrument.custom_instrument.item_attribute.item_attribute.after_insert"
 	},
 	"Material Request":{
 	"validate":"instrument.instrument.custom_instrument.material_request.material_request.validate",
 	"after_insert":"instrument.instrument.custom_instrument.material_request.material_request.after_insert"
 	},
 	"Job Card":{
 	"validate":["instrument.instrument.custom_instrument.job_card.job_card.label_img","instrument.instrument.custom_instrument.job_card.job_card.validate"],
 	"after_insert":"instrument.instrument.custom_instrument.job_card.job_card.after_insert"
 	},
 	"Pick List":{
 	"validate":["instrument.instrument.custom_instrument.pick_list.pick_list.label_img","instrument.instrument.custom_instrument.pick_list.pick_list.validate"],
 	"after_insert":"instrument.instrument.custom_instrument.pick_list.pick_list.after_insert"
 	},
 	"Work Order Pick List":{
 	"validate":"instrument.instrument.custom_instrument.work_order_pick_list.work_order_pick_list.label_img"
 	},
 	"Payment Entry":{
 	"validate":"instrument.instrument.custom_instrument.payment_entry.payment_entry.validate",
 	"after_insert":"instrument.instrument.custom_instrument.payment_entry.payment_entry.after_insert"
 	}
}

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "instrument.install.before_install"
# after_install = "instrument.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "instrument.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

override_doctype_class = {
	"Purchase Order": "instrument.instrument.custom_instrument.purchase_order.purchase_order.PurchaseOrder"
}

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------

scheduler_events = {
# 	"all": [
# 		"instrument.tasks.all"
# 	],
	"daily": [
		"instrument.instrument.custom_instrument.blanket_order.blanket_order.generate_po_against_blanket_order_reminder"
	],
# 	"hourly": [
# 		"instrument.tasks.hourly"
# 	],
# 	"weekly": [
# 		"instrument.tasks.weekly"
# 	]
# 	"monthly": [
# 		"instrument.tasks.monthly"
# 	]
}

# Testing
# -------

# before_tests = "instrument.install.before_tests"

# Overriding Methods
# ------------------------------
#
override_whitelisted_methods = {
	"erpnext.manufacturing.doctype.work_order.work_order.stop_unstop": "instrument.instrument.custom_instrument.work_order.work_order.stop_unstop"
}
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
override_doctype_dashboards = {
	"Item":  "instrument.instrument.custom_instrument.item.item_dashboard.get_data",
	"Sales Order" : "instrument.instrument.custom_instrument.sales_order.sales_order_dashboard.get_data"
}

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]


# User Data Protection
# --------------------

user_data_fields = [
	{
		"doctype": "{doctype_1}",
		"filter_by": "{filter_by}",
		"redact_fields": ["{field_1}", "{field_2}"],
		"partial": 1,
	},
	{
		"doctype": "{doctype_2}",
		"filter_by": "{filter_by}",
		"partial": 1,
	},
	{
		"doctype": "{doctype_3}",
		"strict": False,
	},
	{
		"doctype": "{doctype_4}"
	}
]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"instrument.auth.validate"
# ]

# from erpnext.buying.doctype.purchase_order.purchase_order import PurchaseOrder

# def validate_minimum_order_qty(self):
# 	if not self.get("items"):
# 		return
# 	items = list(set(d.item_code for d in self.get("items")))

# 	itemwise_min_order_qty = frappe._dict(
# 		frappe.db.sql(
# 			"""select name, min_order_qty
# 		from tabItem where name in ({0})""".format(
# 				", ".join(["%s"] * len(items))
# 			),
# 			items,
# 		)
# 	)

# 	itemwise_qty = frappe._dict()
# 	for d in self.get("items"):
# 		itemwise_qty.setdefault(d.item_code, 0)
# 		itemwise_qty[d.item_code] += flt(d.stock_qty)

# 	for item_code, qty in itemwise_qty.items():
# 		if flt(qty) < flt(itemwise_min_order_qty.get(item_code)):
# 			frappe.msgprint(
# 				_(
# 					"Item {0}: Ordered qty {1} cannot be less than minimum order qty {2} (defined in Item)."
# 				).format(item_code, qty, itemwise_min_order_qty.get(item_code))
# 			)
# PurchaseOrder.validate_minimum_order_qty = validate_minimum_order_qty