from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from datetime import date, timedelta, datetime


@frappe.whitelist()
def blanket_order_daily_remainder():
    sender = "shubhangi.r@indictranstech.com"
    recipient = "shubhngirut27@gmail.com"
    Blanket_Orders = frappe.db.sql("select name,from_date,to_date,updated_date,frequency from `tabBlanket Order`",as_dict=1)
    print("Blanket_Order_Data...$$$$$$$$",Blanket_Orders)
    date_todate = datetime.today()
    date_today = date_todate.date()
    blanket_order_list = []
    if Blanket_Orders:
        for row in Blanket_Orders:
            if not row.updated_date == None:
                if not row.frequency == None:
                    print("dates value3333333333",row.updated_date + timedelta(days=row.frequency))
                    print("todayssssssssssssssssssssssssss",date_today)
                    if date_today == row.updated_date + timedelta(days=row.frequency):
                        blanket_order_list.append(row)
                        # update updated date
            else:
                if row.from_date:
                    if not row.frequency == None:
                        if date_today == row.from_date + timedelta(days=row.frequency):
                            blanket_order_list.append(row)
                            # update updated date

    print("blanket_list",blanket_order_list)
    list1 = []
    for i in blanket_order_list:
        #blanket = frappe.db.sql(""" SELECT *  FROM tabBlanket Order 
        #       WHERE name = '{0}'""".format(i.name),as_dict=1)
        blanket = frappe.get_doc("Blanket Order", {"name": i.name})
        # blanket1 = frappe.get_doc("Blanket Order",i.name)
        # list1 = []
        for t in blanket.get("items"):
            list1.append({  'blanket_order':i.name,
                            'item_code':t.item_code,
                            'qty':t.qty
                        })
    print("tested,,,,,,,,,,,,,,,,,",list1)
    message = "Dear Team,"+"<br>"+"Following Blanket Order are due"+"<br>"+"<br>"
    print("messsssssssssssssssssssssssssssssssssssss",message)
    message = message + "<table class ='table table-bordered'><tr><th style='text-align: center'>Blanket Order</th><th style='text-align: center'>Item Code</th><th style='text-align: center'>Quantity</th></tr>"
    for record in list1:
        message = message + "<tr>"\
        "<td>"+record.blanket_order+"</td>"\
        "<td style='text-align: center'>"+record.item_code+"</td>"\
        "<td style='text-align: center'>"+record.qty+"</td>"\
        "</tr>"
    message =message + "</table>"+"<br>"+"<br>"+"Best Regards,"+"<br>"+"Team Rushabh Instrument"

    frappe.sendmail(
            sender = sender,
            recipients = recipient,
            subject = "Blanket Order Reminder",
            message = message,
            )
    print("shubhangi email triger")

