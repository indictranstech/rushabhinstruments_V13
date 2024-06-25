import frappe
import json
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
from datetime import date,timedelta
#Authenticate and Login to ERPNext With an API

@frappe.whitelist( allow_guest=True )
def login(usr, pwd):
    try:
        login_manager = frappe.auth.LoginManager()
        login_manager.authenticate(user=usr, pwd=pwd)
        login_manager.post_login()
    except frappe.exceptions.AuthenticationError:
        frappe.clear_messages()
        frappe.local.response["message"] = {
            "success_key":0,
            "message":"Authentication Error!"
        }

        return

    api_generate = generate_keys(frappe.session.user)
    user = frappe.get_doc('User', frappe.session.user)

    frappe.response["message"] = {
        "success_key":1,
        "message":"Authentication success",
        "sid":frappe.session.sid,
        "api_key":user.api_key,
        "api_secret":api_generate,
        "username":user.username,
        "email":user.email
    }



def generate_keys(user):
    user_details = frappe.get_doc('User', user)
    api_secret = frappe.generate_hash(length=15)

    if not user_details.api_key:
        api_key = frappe.generate_hash(length=15)
        user_details.api_key = api_key

    user_details.api_secret = api_secret
    user_details.save()

    return api_secret



@frappe.whitelist(allow_guest=True)
def item_details_api():
    return frappe.db.sql(f"""select a.item_code,a.item_name,a.item_group,a.is_sales_item,a.weight_uom,a.description,a.stock_uom,a.end_of_life,a.lead_time_days,b.default_warehouse,a.is_stock_item  from `tabItem` a left join `tabItem Default` b ON a.item_code = b.parent""", as_dict=True)


@frappe.whitelist(allow_guest=True)
def sales_order_api():
    return frappe.db.sql(f"""select a.name,a.customer,a.order_type,a.transaction_date,a.delivery_date,a.woocommerce_order_id,a.company,a.currency,a.selling_price_list,b.item_code,b.item_name,b.uom,
    b.qty,b.rate,b.amount,b.description,b.conversion_factor,b.base_rate,b.base_amount
    from `tabSales Order` a left join `tabSales Order Item` b
    ON a.name = b.parent """, as_dict=True)

@frappe.whitelist(allow_guest=True)
def sales_invoice_api():
    return frappe.db.sql(f""" select a.name,a.customer,a.company,a.posting_date,a.posting_time,a.due_date,a.woocommerce_order_id,a.currency,a.selling_price_list,a.debit_to,a.base_net_total,a.base_grand_total,a.grand_total,
    b.parenttype,b.item_code,b.item_name,b.uom,b.qty,b.rate,b.amount,b.description,b.conversion_factor,b.income_account,b.base_rate,b.base_amount,
    c.parenttype,c.payment_amount,c.invoice_portion,c.due_date
    from `tabSales Invoice` a left join `tabSales Invoice Item` b ON a.name = b.parent
    left join `tabPayment Schedule` c ON a.name = b.parent and a.name=c.parent""", as_dict=True)

@frappe.whitelist(allow_guest=True)
def delivery_note_api(woocommerce_order_id=None):
    data = frappe.db.sql(f""" select a.name,a.company,a.customer,a.posting_date,a.woocommerce_order_id,a.posting_time,a.currency,a.selling_price_list,a.base_net_total,a.base_grand_total,a.grand_total,
    b.item_code,b.item_name,b.uom,b.qty,b.rate,b.amount,b.description,b.conversion_factor,b.base_rate,b.base_amount,b.batch_no,b.serial_no,b.against_sales_order,b.against_sales_invoice,a.total_taxes_and_charges
    from `tabDelivery Note` a left join `tabDelivery Note Item` b ON a.name = b.parent where a.woocommerce_order_id='{woocommerce_order_id}' """,  as_dict=True)
    return(data)

@frappe.whitelist(allow_guest=True)
def delivery_note_details(woocommerce_order_id=None):
    data = frappe.db.sql(f""" select a.name,a.company,a.customer,a.posting_date,a.woocommerce_order_id,a.posting_time,a.currency,a.selling_price_list,a.base_net_total,a.base_grand_total,a.grand_total,
    b.item_code,b.item_name,b.uom,b.qty,b.rate,b.amount,b.description,b.conversion_factor,b.base_rate,b.base_amount,b.batch_no,b.serial_no,b.against_sales_order,b.against_sales_invoice,a.total_taxes_and_charges
    from `tabDelivery Note` a left join `tabDelivery Note Item` b ON a.name = b.parent """,  as_dict=True)
    return(data)

#Get purticular delivery Note from Woocommerce id
@frappe.whitelist(allow_guest=True)
def get_deliver_note(data=None):
    data = json.loads(frappe.request.data)
    if frappe.db.get_value("Delivery Note", {"woocommerce_order_id":data.get("woocommerce_order_id")}, "name"):
        details = frappe.db.sql("""select a.name,a.company,a.customer,a.posting_date,a.woocommerce_order_id,a.posting_time,a.currency,a.selling_price_list,a.base_net_total,a.base_grand_total,a.grand_total,
    b.item_code,b.item_name,b.uom,b.qty,b.rate,b.amount,b.description,b.conversion_factor,b.base_rate,b.base_amount,b.batch_no,b.serial_no,b.against_sales_order,b.against_sales_invoice,a.total_taxes_and_charges
    from `tabDelivery Note` a left join `tabDelivery Note Item` b ON a.name = b.parent where woocommerce_order_id='{0}' """.format(data.get("woocommerce_order_id")), as_dict=1)
        return {"status":200, "data":details}
    else:
        return {"status":200, "data":""}

@frappe.whitelist(allow_guest=True)
def customer_api():
    return frappe.db.sql(f""" Select a.name,a.customer_name,a.creation,a.modified,a.woocommerce_customer_id,a.customer_group,a.territory,a.tax_id,d.address_line1,d.address_line2,d.city,d.state,d.country,d.county,d.pincode,d.email_id,d.phone from
    (Select * from `tabCustomer`)a
    left join
    (Select * from
    ((Select name,address_line1,address_line2,city,state,country,county,pincode,email_id,phone From `tabAddress`)b
    left join
    (Select parent,link_name,link_doctype From `tabDynamic Link` where link_doctype="Customer" and parenttype="Address")c
    ON b.name=c.parent))d ON a.name=d.link_name""", as_dict=True)

@frappe.whitelist(allow_guest=True)
def item_wise_stock_api():
    return frappe.db.sql(f""" select warehouse, modified as date,item_code, sum(actual_qty), stock_uom,valuation_rate,stock_value from `tabBin` """, as_dict=True)

@frappe.whitelist(allow_guest=True)
def item_wise_production_api():
    return frappe.db.sql(f""" select `tabWork Order`.name as work_order,`tabWork Order`.status,production_item,`tabWork Order`.item_name,`tabWork Order`.qty as qty_for_manufacture,`tabWork Order`.material_transferred_for_manufacturing,`tabWork Order`.produced_qty,`tabWork Order`.sales_order,
`tabWork Order`.wip_warehouse,`tabWork Order`.fg_warehouse,`tabWork Order`.planned_start_date,`tabWork Order`.planned_end_date,`tabWork Order`.actual_start_date,`tabWork Order`.actual_end_date,`tabItem`.lead_time_days
 from `tabWork Order` LEFT JOIN `tabItem` ON `tabWork Order`.production_item=`tabItem`.item_code where `tabWork Order`.docstatus=1; """, as_dict=True)

@frappe.whitelist(allow_guest=True)
def customer_list():
    return frappe.db.sql(f""" Select name as customer_code, customer_name,customer_group,territory,mobile_no from `tabCustomer` """, as_dict=True)

#Get all delivery notes by a particular date, date arguement format is yyyy-mm-dd
@frappe.whitelist(allow_guest=True)
def delivery_note_on_date(posting_date=None):
    if posting_date:
        data = frappe.db.sql(f""" select a.name,a.company,a.customer,a.posting_date,a.woocommerce_order_id,a.posting_time,a.currency,a.selling_price_list,a.base_net_total,a.base_grand_total,a.grand_total,
        b.item_code,b.item_name,b.uom,b.qty,b.rate,b.amount,b.description,b.conversion_factor,b.base_rate,b.base_amount,b.batch_no,b.serial_no,b.against_sales_order,b.against_sales_invoice,a.total_taxes_and_charges
        from `tabDelivery Note` a left join `tabDelivery Note Item` b ON a.name = b.parent where a.posting_date='{posting_date}' """,  as_dict=True)
        return(data)



@frappe.whitelist(allow_guest=True)
def create_payment_entry(data=None):
    data=json.loads(frappe.request.data)
    total_amount=outstanding_amount=total_allocated_amount=unallocated_amount=allocated_amount=0.0
    try:
        pe_doc = frappe.new_doc("Payment Entry")
        pe_doc.company = "Rushabh Instruments, LLC"
        pe_doc.payment_type = "Receive"
        pe_doc.party_type = "Customer"
        pe_doc.party = data.get("party")
        pe_doc.party_name = frappe.db.get_value("Customer", data.get("party"), "customer_name")
        pe_doc.posting_date = today()
        pe_doc.paid_to = "TD Bank - RI"
        pe_doc.paid_amount = data.get("paid_amount")
        pe_doc.received_amount =  data.get("paid_amount")
        pe_doc.reference_no = "RU23456"
        pe_doc.reference_date = today()
        for idx, row in enumerate(data.get("references")):
            if frappe.db.get_value("Sales Order", row.get("reference_name"), "name"):
                ref_doc = frappe.get_doc("Sales Order", row.get("reference_name"))
                total_amount=flt(ref_doc.base_grand_total)
                outstanding_amount=flt(ref_doc.base_grand_total) - flt(ref_doc.advance_paid)
                if idx == 0:
                    unallocated_amount=flt(data.get("paid_amount"))+flt(data.get("credit_card_processing_amount"))

                if unallocated_amount > outstanding_amount:
                    allocated_amount=outstanding_amount
                else:
                    allocated_amount=unallocated_amount

                total_allocated_amount+=allocated_amount

                if  total_allocated_amount < (flt(data.get("paid_amount"))+flt(data.get("credit_card_processing_amount"))):
                    unallocated_amount=flt(data.get("paid_amount"))+flt(data.get("credit_card_processing_amount"))-total_allocated_amount

                row["reference_doctype"] = ref_doc.doctype
                row["total_amount"]=total_amount
                row["outstanding_amount"]=outstanding_amount 
                row["allocated_amount"] = allocated_amount 
                pe_doc.append("references", row)
            else:
                invoices = frappe.get_all("Sales Invoice", {"web_invoice_number":row.get("reference_name")}, "name")
                for idx, inv in enumerate(invoices):
                    ref_doc = frappe.get_doc("Sales Invoice", inv.get("name"))
                    total_amount=flt(ref_doc.base_rounded_total)
                    outstanding_amount=flt(ref_doc.outstanding_amount)

                    if idx == 0:
                        unallocated_amount=flt(data.get("paid_amount"))+flt(data.get("credit_card_processing_amount"))

                    if unallocated_amount > outstanding_amount:
                        allocated_amount=outstanding_amount
                    else:
                        allocated_amount=unallocated_amount
                    total_allocated_amount+=allocated_amount
                    if total_allocated_amount < (flt(data.get("paid_amount"))+flt(data.get("credit_card_processing_amount"))):
                        unallocated_amount=flt(data.get("paid_amount"))+flt(data.get("credit_card_processing_amount"))-total_allocated_amount

                    inv["reference_doctype"] = ref_doc.doctype
                    inv["total_amount"] = total_amount
                    inv["outstanding_amount"] = outstanding_amount 
                    inv["allocated_amount"] = allocated_amount
                    inv["due_date"] =  ref_doc.due_date
                    inv["reference_name"] = ref_doc.name
                    pe_doc.append("references", inv)
        pe_doc.append("deductions", {
            "account":"Credit Card Processing Fee - RI",
            "cost_center":"Main - RI",
            "amount": data.get("credit_card_processing_amount")
        })
        pe_doc.save(ignore_permissions=True)
        pe_doc.submit()
        frappe.db.commit()
        return {"payment_enrty_name":pe_doc.name}
    except Exception as e:
        return {"error":e}
