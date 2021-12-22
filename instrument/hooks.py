from . import __version__ as app_version

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
	"Material Request" : "instrument/custom_instrument/material_request/material_request.js"
 
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
doctype_tree_js = {"BOM" : "instrument/custom_instrument/bom/bom_tree.js"}
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
		"validate" : "instrument.instrument.custom_instrument.purchase_order.purchase_order.validate"
	},
	"Purchase Receipt" :{
		"on_submit" : "instrument.instrument.custom_instrument.purchase_receipt.purchase_receipt.on_submit",
		"validate" : "instrument.instrument.custom_instrument.purchase_receipt.purchase_receipt.validate"
	},
	"Purchase Invoice" :{
		"on_submit" : "instrument.instrument.custom_instrument.purchase_invoice.purchase_invoice.on_submit"
	},
	"Request for Quotation" :{
		"on_submit" : "instrument.instrument.custom_instrument.request_for_quotation.request_for_quotation.on_submit",
		"validate" : "instrument.instrument.custom_instrument.request_for_quotation.request_for_quotation.validate"
	},
	"Supplier Quotation" :{
		"on_submit" : "instrument.instrument.custom_instrument.supplier_quotation.supplier_quotation.on_submit"
	},
	"Sales Order" :{
		"on_submit" : "instrument.instrument.custom_instrument.sales_order.sales_order.on_submit"
	},
	"Sales Invoice" :{
		"on_submit" : "instrument.instrument.custom_instrument.sales_invoice.sales_invoice.on_submit"
	},
	"Delivery Note" :{
		"on_submit" : "instrument.instrument.custom_instrument.delivery_note.delivery_note.on_submit"
	},
	"Blanket Order" :{
		"on_submit" : "instrument.instrument.custom_instrument.blanket_order.blanket_order.on_submit"
	},
	"Serial No" : {
	"autoname" : "instrument.instrument.custom_instrument.serial_no.serial_no.autoname"
	},
	"BOM" : {
	"validate" :  "instrument.instrument.custom_instrument.bom.bom.validate",
	"on_update" : "instrument.instrument.custom_instrument.bom.bom.validate"
	},
	"Work Order" : {
	"after_insert" : "instrument.instrument.custom_instrument.work_order.work_order.check_stock",
	"on_update_after_submit" : "instrument.instrument.custom_instrument.work_order.work_order.check_stock",
	"on_update" : "instrument.instrument.custom_instrument.work_order.work_order.check_stock",
	"validate" : ["instrument.instrument.custom_instrument.work_order.work_order.add_bom_level","instrument.instrument.custom_instrument.work_order.work_order.validate"],
	"on_submit" : "instrument.instrument.custom_instrument.work_order.work_order.on_submit"
	},
	"Item" : {
	"validate" :"instrument.instrument.custom_instrument.item.item.validate"
	},
	"Production Plan":{
	"on_update" : "instrument.instrument.custom_instrument.production_plan.production_plan.on_update",
	"validate" : "instrument.instrument.custom_instrument.production_plan.production_plan.validate"

	},
	"Batch" : {
	"autoname" : "instrument.instrument.custom_instrument.batch.batch.autoname"
	},
	"Stock Entry" : {
	"validate" : "instrument.instrument.custom_instrument.stock_entry.stock_entry.validate"
 	},
 	"Item Attribute" : {
 	"validate" : "instrument.instrument.custom_instrument.item_attribute.item_attribute.validate",
 	"after_insert" : "instrument.instrument.custom_instrument.item_attribute.item_attribute.after_insert"
 	},
 	"Material Request":{
 	"validate":"instrument.instrument.custom_instrument.material_request.material_request.validate"
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

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

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
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "instrument.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
override_doctype_dashboards = {
	"Item":  "instrument.instrument.custom_instrument.item.item_dashboard.get_data"
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

