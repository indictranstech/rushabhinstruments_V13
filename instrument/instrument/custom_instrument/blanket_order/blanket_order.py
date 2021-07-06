from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from datetime import date, timedelta, datetime
from frappe.utils import getdate, get_datetime, flt, nowdate, cstr, today


def on_submit(doc, method):
    for row in doc.items:
        row.updated_date = getdate(nowdate())


def generate_po_against_blanket_order_reminder():
    data = {}
    blanket_orders_name = frappe.db.sql("""SELECT name from `tabBlanket Order` where docstatus=1 and blanket_order_type='Purchasing' """, as_dict=1)

    for name in blanket_orders_name:
        order_name = frappe.get_list("Blanket Order Item", {"parent": name.get("name")}, ["name", "item_code", "item_name", "updated_date", "delivery_quantity", "frequency_in_day", "parent"])
        item_list = {}
        for row in order_name:
            if row.get("frequency_in_day"):
                today_date = row.get("updated_date")+timedelta(days=int(row.get("frequency_in_day")))
            else:
                today_date = row.get("updated_date")
            if getdate(today_date) == getdate(nowdate()):
                frappe.db.set_value("Blanket Order Item", row.get("name"), "updated_date", getdate(nowdate()))
                item_list[row.get("item_name")] = row.get("delivery_quantity")
        email_template = frappe.get_doc("Email Template", "Blanket Order")
        if item_list:
            data["name"]=name.get("name")
            data["item_list"]=item_list
            message = frappe.render_template(email_template.response_html, data)
            try:
                frappe.sendmail(
                    recipients = ["jitendra.r@indictranstech.com"],
                    sender = None,
                    subject = email_template.subject,
                    message = message,
                    delayed=False
                )
            except frappe.OutgoingEmailError:
                pass
        item_list.clear()
   