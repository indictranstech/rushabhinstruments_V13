import frappe
from frappe.model.naming import make_autoname
from frappe.utils import nowdate, cstr, flt, cint, now, getdate,get_datetime,time_diff_in_seconds,add_to_date,time_diff_in_seconds,add_days,today
# import time,datetime
# from datetime import date 
from datetime import datetime   
def autoname(doc, method):
	now = datetime.now()
	week_no = datetime.date(now).isocalendar()[1]
	doc.name = make_autoname('SN-' + str(week_no) + '-' + '.#####')
	return doc.name