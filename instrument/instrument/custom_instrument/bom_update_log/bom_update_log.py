from frappe.model.document import Document
import frappe
import json
# import click
# from frappe import _


def validate(doc, method=None):
	frappe.db.set_value("BOM", doc.new_bom, "update_status", doc.status)
	frappe.db.commit()

