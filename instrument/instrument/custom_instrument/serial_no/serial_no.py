# import frappe
# from frappe.model.naming import make_autoname
# from frappe.utils import nowdate, cstr, flt, cint, now, getdate,get_datetime,time_diff_in_seconds,add_to_date,time_diff_in_seconds,add_days,today
# # import time,datetime
# # from datetime import date 
# from datetime import datetime   
# def autoname(doc, method):
# 	# add week number and year in name
# 	now = datetime.now()
# 	week_no = datetime.date(now).isocalendar()[1]
# 	doc.name = make_autoname('SN-' + str(week_no) + '-' + str(datetime.date(now).isocalendar()[0])[2:4] + '-' + '.#####')
# 	return doc.name

import frappe
from frappe.model.naming import make_autoname
from frappe.utils import nowdate, cstr, flt, cint, now, getdate,get_datetime,time_diff_in_seconds,add_to_date,time_diff_in_seconds,add_days,today
from datetime import datetime


def autoname(doc, method):
	if doc.item_code:
		now = datetime.now()
		currentMonth = datetime.now().month
		currentMonth = '{:02d}'.format(currentMonth)
		currentYear = datetime.now().year
		
		engineering_revision = frappe.db.get_value("Item",{'item_code':doc.item_code},'engineering_revision')
		# get_naming_prefix(doc,naming_series)
		if doc.purchase_document_type == 'Purchase Receipt':
			if doc.purchase_document_no:
				pr_doc = frappe.get_doc("Purchase Receipt",doc.purchase_document_no)
				for item in pr_doc.items:
					if item.item_code == doc.item_code:
						naming_series = frappe.db.get_value("Item",{'item_code':doc.item_code},'serial_no_series')
						naming_prefix = get_naming_prefix(doc,item.engineering_revision,currentYear,naming_series)

						doc.name = make_autoname(naming_prefix+'-'+".#####")
						doc.serial_no = doc.name
						return doc.name
		elif doc.purchase_document_type == 'Stock Entry':
			if doc.purchase_document_no:
				se_doc = frappe.get_doc("Stock Entry",doc.purchase_document_no)
				for item in se_doc.items:
					if item.item_code == doc.item_code:
						naming_series = frappe.db.get_value("Item",{'item_code':doc.item_code},'serial_no_series')
						naming_prefix = get_naming_prefix(doc,item.engineering_revision,currentYear,naming_series)

						doc.name = make_autoname(naming_prefix+'-'+".#####")
						doc.serial_no = doc.name
						return doc.name
		elif engineering_revision:
			naming_series = frappe.db.get_value("Item",{'item_code':doc.item_code},'serial_no_series')
			naming_prefix = get_naming_prefix(doc,engineering_revision,currentYear,naming_series)

			doc.name = make_autoname(naming_prefix+'-'+".#####")
			doc.serial_no = doc.name
			return doc.name
		else:
			doc.name = make_autoname('SN' + '-'+str(currentYear) +'-'+str(currentMonth) + '-' + '.#####')
			doc.serial_no = doc.name
			return doc.name

def get_naming_prefix(doc,engineering_revision,currentYear,naming_series):
	now = datetime.now()
	week_no = datetime.date(now).isocalendar()[1]
	naming_series = naming_series.split('-')
	naming_series = naming_series[0]
	new_naming = naming_series
	if 'ENG' in naming_series:
		new_naming = naming_series.replace('ENG',str(engineering_revision))
	if 'YYYY' in naming_series:
		new_naming = new_naming.replace('YYYY',str(currentYear))
	if 'WW' in naming_series:
		new_naming = new_naming.replace('WW',str(week_no))
	return new_naming