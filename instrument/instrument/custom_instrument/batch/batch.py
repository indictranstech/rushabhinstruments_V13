import frappe
from frappe.model.naming import make_autoname
from frappe.utils import nowdate, cstr, flt, cint, now, getdate,get_datetime,time_diff_in_seconds,add_to_date,time_diff_in_seconds,add_days,today
from datetime import datetime

def autoname(doc, method):
	if doc.item:
		engineering_revision = frappe.db.get_value("Item",{'item_code':doc.item},'engineering_revision')
		if doc.reference_doctype == 'Purchase Receipt':
			if doc.reference_name:
				pr_doc = frappe.get_doc("Purchase Receipt",doc.reference_name)
				for item in pr_doc.items:
					if item.item_code == doc.item:
						doc.name = make_autoname('BN-' + str(item.engineering_revision) + '-' + '.#####')
						return doc.name
		elif doc.reference_doctype == 'Stock Entry':
			if doc.reference_name:
				se_doc = frappe.get_doc("Stock Entry",doc.reference_name)
				for item in se_doc.items:
					if item.item_code == doc.item:
						doc.name = make_autoname('BN-' + str(item.engineering_revision) + '-' + '.#####')
						return doc.name
		elif engineering_revision:
			doc.name = make_autoname('BN-' + str(engineering_revision) + '-' + '.#####')
			return doc.name
		else:
			pass