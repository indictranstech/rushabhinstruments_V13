# Copyright (c) 2022, instrument and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _, msgprint
from frappe.utils import (
	add_days,
	ceil,
	cint,
	comma_and,
	flt,
	get_link_to_form,
	getdate,
	now_datetime,
	nowdate,today
)
from datetime import date,timedelta
from erpnext.manufacturing.doctype.bom.bom import get_children, validate_bom_no
import datetime
class ProductionPlanningWithLeadTime(Document):
	@frappe.whitelist()
	def get_open_sales_orders(self):
		""" Pull sales orders  which are pending to deliver based on criteria selected"""
		self.sales_order_table = ''
		open_so = get_sales_orders(self)

		if open_so:
			self.add_so_in_table(open_so)
		else:
			frappe.msgprint(_("Sales orders are not available for production"))
		
	@frappe.whitelist()
	def add_so_in_table(self, open_so):
		""" Add sales orders in the table"""
		self.set('sales_order_table', [])
		for data in open_so:
			bom_data = frappe.db.sql("""SELECT name,makeup_days from `tabBOM` where item = '{0}' and is_active = 1 and is_default =1 and docstatus = 1""".format(data.get("item_code")),as_dict=1)
			dn_date = data.get('delivery_date')
			today_date = date.today()
			# Calculate Days to Deliver
			days_to_deliver = (dn_date - today_date)
			self.append('sales_order_table', {
				'sales_order': data.get("name"),
				'item':data.get('item_code'),
				'delivery_date':data.get('delivery_date'),
				'qty':data.get('qty'),
				'bom':bom_data[0].get('name'),
				'makeup_days':bom_data[0].get('makeup_days'),
				'days_to_deliver' : days_to_deliver.days
			})
		return self.sales_order_table
	@frappe.whitelist()
	def sort_so_data(self):
		self.sorted_sales_order_table = ''
		if self.sales_order_table:
			so_data = frappe.db.sql("""SELECT * from `tabSales Order Table` where parent = '{0}'""".format(self.name),as_dict=1)
			sorted_so_data = sorted(so_data, key = lambda x: (x["delivery_date"],x["priority"]))
			# sorted_so_data = sorted(so_data, key = lambda x: x["priority"])
			count = 1
			for row in sorted_so_data:
				row.update({'idx':count})
				self.append('sorted_sales_order_table',row)
				count = count + 1
		return self.sorted_sales_order_table
	@frappe.whitelist()
	def work_order_planning(self):
		# fetch warehouse list from Rushabh settings
		warehouse_list = get_warehouses()
		# Get On hand stock
		ohs = get_ohs(warehouse_list)
		# Get Planned Stock
		planned_data = self.get_planned_data()
		fg_data = frappe.db.sql("""SELECT * from `tabSales Order Table` where parent = '{0}'""".format(self.name),as_dict=1)
		if fg_data:
			fg_data = sorted(fg_data, key = lambda x: (x["delivery_date"],x["priority"]))
			count = 1
			for row in fg_data:
				qty = flt(row.get("qty")) - flt(ohs.get(row.get("item"))) if flt(ohs.get(row.get("item"))) < flt(row.get("qty")) else 0
				row.update({'planned_qty':qty,'available_stock':ohs.get(row.get('item')),'already_planned_qty':planned_data.get(row.get('item')),'shortage':qty})
				remaining_qty = flt(ohs.get(row.get("item"))) - flt(row.get("qty")) if flt(ohs.get(row.get("item"))) > flt(row.get("qty")) else 0
				ohs.update({row.get('item'):remaining_qty})
				planned_allocate = flt(qty) - flt(planned_data.get(row.get("item"))) if flt(planned_data.get(row.get("item"))) < flt(qty) else 0
				row.update({'planned_qty':planned_allocate,'shortage':planned_allocate})
				remainingg_qty = flt(planned_data.get(row.get("item"))) - flt(qty) if flt(planned_data.get(row.get("item"))) > flt(qty) else 0
				planned_data.update({row.get('item'):remainingg_qty})
				operation_time = frappe.db.sql("""SELECT sum(time_in_mins) as operation_time from `tabBOM Operation` where parent = '{0}'""".format(row.get('bom')),as_dict=1)
				total_operation_time_in_mins = flt(operation_time[0].get('operation_time'))*row.get('qty')
				total_operation_time_in_days = ceil(total_operation_time_in_mins/480)
				# Calculate date_to_be_ready 
				date_to_be_ready = (row.get('delivery_date')-timedelta(total_operation_time_in_days)-timedelta(row.get('makeup_days')))
				row.update({'idx':count,'total_operation_time':total_operation_time_in_days,'date_to_be_ready':date_to_be_ready})
				self.append('fg_items_table',row)
				count = count + 1
			return self.fg_items_table
	@frappe.whitelist()
	def sub_assembly_items(self):
		warehouse_list = get_warehouses()
		# Get On hand stock
		ohs = get_ohs(warehouse_list)
		# Get Planned Stock
		planned_data = self.get_planned_data()
		if self.fg_items_table:
			for row in self.fg_items_table:
				bom_data = []
				if row.get('planned_qty') > 0:
					get_sub_assembly_item(row.get("bom"), bom_data, row.get("planned_qty"))
					bom_data = sorted(bom_data, key = lambda x: x["bom_level"],reverse=1)
					for item in bom_data:
						final_row = dict()
						qty = flt(item.get("stock_qty")) - flt(ohs.get(item.get("production_item"))) if flt(ohs.get(item.get("production_item"))) < flt(item.get("stock_qty")) else 0
						final_row.update({'qty':qty,'available_stock':ohs.get(item.get('production_item')),'alreaady_planned_qty':planned_data.get(item.get('production_item')),'shortage':qty,'fg_item':item.get('parent_item_code'),'item':item.get('production_item'),'original_qty':item.get('stock_qty'),'bom':item.get('bom_no'),'sales_order':row.get('sales_order')})
						remaining_qty = flt(ohs.get(item.get("production_item"))) - flt(item.get("stock_qty")) if flt(ohs.get(item.get("production_item"))) > flt(item.get("stock_qty")) else 0
						ohs.update({item.get('production_item'):remaining_qty})
						planned_allocate = flt(qty) - flt(planned_data.get(item.get("production_item"))) if flt(planned_data.get(item.get("production_item"))) < flt(qty) else 0
						final_row.update({'qty':planned_allocate,'shortage':planned_allocate})
						remainingg_qty = flt(planned_data.get(item.get("production_item"))) - flt(qty) if flt(planned_data.get(item.get("production_item"))) > flt(qty) else 0
						planned_data.update({item.get('production_item'):remainingg_qty})
						operation_time = frappe.db.sql("""SELECT sum(time_in_mins) as operation_time from `tabBOM Operation` where parent = '{0}'""".format(item.get('bom_no')),as_dict=1)
						total_operation_time_in_mins = flt(operation_time[0].get('operation_time'))*final_row.get('qty')
						total_operation_time_in_days = ceil(total_operation_time_in_mins/480)
						makeup_days = frappe.db.get_value("BOM",{'name':item.get('bom_no')},'makeup_days')
						date_to_be_ready = datetime.datetime.strptime(row.get('date_to_be_ready'), '%Y-%m-%d')
						date_to_be_ready = date_to_be_ready.date()
						date_to_be_ready = (date_to_be_ready-timedelta(total_operation_time_in_days)-timedelta(makeup_days))
						final_row.update({'total_operation_time':total_operation_time_in_days,'date_to_be_ready':date_to_be_ready})
						self.append('sub_assembly_items_table',final_row)
			return self.sub_assembly_items_table
						
	@frappe.whitelist()
	def get_raw_materials(self):
		warehouse_list = get_warehouses()
		# Get On hand stock
		ohs = get_ohs(warehouse_list)
		if self.sub_assembly_items_table:
			for row in self.sub_assembly_items_table:
				raw_data = []
				get_raw_items(row.bom,raw_data,row.qty)
				remaining_dict = dict()
				for item in raw_data:
					lead_time = frappe.db.get_value("Item",{'name':item.get('item')},'lead_time_days')
					item.update({'date_to_be_ready':row.date_to_be_ready,'available_stock':ohs.get(item.get('item')),'lead_time':lead_time,'original_qty':item.get('qty')})
					rm_readiness_days = frappe.db.get_single_value("Rushabh Settings",'rm_readiness_days')
					date_to_be_ready = datetime.datetime.strptime(row.get('date_to_be_ready'), '%Y-%m-%d')
					date_to_be_ready = date_to_be_ready.date()
					required_date = (date_to_be_ready-timedelta(rm_readiness_days))
					today_date = date.today()
					# Calculate Order in days
					order_in_days = (required_date - today_date)
					item.update({'order_in_days':order_in_days.days})
					# Allocate from available_stock
					qty = flt(item.get("qty")) - flt(ohs.get(item.get("item"))) if flt(ohs.get(item.get("item"))) < flt(item.get("qty")) else 0
					item.update({'shortage':qty,'qty':qty})
					remaining_qty = flt(ohs.get(item.get("item"))) - flt(item.get("qty")) if flt(ohs.get(item.get("item"))) > flt(item.get("qty")) else 0
					ohs.update({item.get('item'):remaining_qty})
					# Allocate from planned_po nd mr of type Purchase
					if item.get('item') not in remaining_dict:
						on_order_stock = get_on_order_stock(self,required_date)
						
						qty = flt(item.get("qty")) - flt(on_order_stock.get(item.get("item"))) if flt(on_order_stock.get(item.get("item"))) < flt(item.get("qty")) else 0
						remaining_qty = flt(on_order_stock.get(item.get('item'))) - item.get('qty') 
						remaining_dict[item.get('item')] = remaining_qty if remaining_qty > 0 else 0
						item.update({'qty':qty,'on_order_stock':on_order_stock.get(item.get("item")),'shortage':qty})
						if item.get('qty')>0:
							latest_date_availability = required_date if required_date > today_date else lead_time
							item.update({'latest_date_availability':latest_date_availability})
					else:
						virtual_stock = remaining_dict.get(item.get('item'))
						qty = flt(item.get("qty")) - flt(virtual_stock) if flt(virtual_stock) < flt(item.get("qty")) else 0
						remaining_qty = virtual_stock - item.get('qty')

						remaining_dict[item.get('item')] = remaining_qty if remaining_qty > 0 else 0
						item.update({'qty':qty,'on_order_stock':virtual_stock,'shortage':qty,'latest_date_availability':required_date})
						if item.get('qty')>0:
							latest_date_availability = required_date if required_date > today_date else lead_time
							item.update({'latest_date_availability':latest_date_availability})
					if item.get('order_in_days') > 0:
						item.update({'readiness_status':'#228B22'})
					elif item.get('order_in_days') == 0 :
						item.update({'readiness_status':'#FF8000'})
					else:
						item.update({'readiness_status':'#CD3700'})
					self.append('raw_materials_table',item)
			return self.raw_materials_table
	@frappe.whitelist()
	def prepare_final_work_orders(self):
		if self.fg_items_table:
			for row in self.fg_items_table:
				if row.qty > 0:
					pass

	def get_planned_data(self):
		# Get planned qty from material request for which production plan not in place and work order not in place
		planned_mr = frappe.db.sql("""SELECT mri.item_code,sum(mri.qty) as qty from `tabMaterial Request` mr join `tabMaterial Request Item` mri on mri.parent = mr.name where mr.transaction_date < '{0}' and mr.transaction_date >= '{1}' and not exists(SELECT pp.name from `tabProduction Plan` pp join `tabProduction Plan Material Request` pp_item on pp_item.parent = pp.name where pp_item.material_request = mr.name) and not exists(SELECT wo.name from `tabWork Order` wo where wo.material_request = mr.name)""".format(self.to_date,self.from_date),as_dict=1)
		# Manipulate in order o show in dict format
		planned_data_dict = {item.item_code : item.qty for item in planned_mr}
		# Get planned qty from production plan for which work order not in place
		planned_pp = frappe.db.sql("""SELECT pp_item.item_code,sum(pp_item.planned_qty) as planned_qty from `tabProduction Plan` pp join `tabProduction Plan Item` pp_item on pp_item.parent = pp.name where pp.posting_date < {0} and pp.posting_date >= '{1}' and not exists(SELECT wo.name from `tabWork Order` wo where wo.production_plan = pp.name)""".format(self.to_date,self.from_date),as_dict=1)
		# update planned_data_dict
		if planned_pp:
			for row in planned_pp:
				if row.get('item_code') in planned_data_dict:
					qty = flt(planned_data_dict.get(row.get('item_code'))) + row.get('planned_qty')
					planned_data_dict.update({row.get('item_code'):qty})
				else:
					planned_data_dict.update({row.get('item_code'):row.get('planned_qty')})
		# Get planned qty from work order
		planned_wo = frappe.db.sql("""SELECT wo.production_item,wo.qty from `tabWork Order` wo where wo.planned_start_date < '{0}' and wo.planned_start_date >= '{1}'""".format(self.to_date,self.from_date),as_dict=1)
		# update planned_data_dict
		if planned_wo:
			for row in planned_wo:
				if row.get('production_item') in planned_data_dict:
					qty = flt(planned_data_dict.get(row.get('production_item'))) + row.get('qty')
					planned_data_dict.update({row.get('production_item'):qty})
				else:
					planned_data_dict.update({row.get('production_item'):row.get('qty')})
		return planned_data_dict
@frappe.whitelist()
def get_raw_items(bom,raw_data,qty):
	doc = frappe.get_doc("BOM",{'name':bom})
	if doc:
		for row in doc.items:
			stock_qty = (row.qty*qty)
			if not row.bom_no:
				raw_data.append({
					'item':row.item_code,
					'qty':stock_qty
				})
		return raw_data
@frappe.whitelist()
def get_sub_assembly_item(bom_no, bom_data, to_produce_qty, indent=0):
	data = get_children('BOM', parent = bom_no)
	for d in data:
		if d.expandable:
			parent_item_code = frappe.get_cached_value("BOM", bom_no, "item")
			stock_qty = (d.stock_qty / d.parent_bom_qty) * flt(to_produce_qty)
			bom_data.append(frappe._dict({
				'parent_item_code': parent_item_code,
				'description': d.description,
				'production_item': d.item_code,
				'item_name': d.item_name,
				'stock_uom': d.stock_uom,
				'uom': d.stock_uom,
				'bom_no': d.value,
				'is_sub_contracted_item': d.is_sub_contracted_item,
				'bom_level': indent,
				'indent': indent,
				'stock_qty': stock_qty
			}))

			if d.value:
				get_sub_assembly_item(d.value, bom_data, stock_qty, indent=indent+1)
def get_on_order_stock(self,required_date):
	planned_po = frappe.db.sql("""SELECT poi.item_code,(poi.qty-poi.received_qty) as qty from `tabPurchase Order` po join `tabPurchase Order Item` poi on poi.parent = po.name where poi.schedule_date < '{0}' and qty > 0""".format(required_date),as_dict=1)
	# Manipulate in order o show in dict format
	on_order_stock = {item.item_code : item.qty for item in planned_po}
	planned_mr = frappe.db.sql("""SELECT mri.item_code,mri.qty from `tabMaterial Request` mr join `tabMaterial Request Item` mri on mri.parent = mr.name where mr.schedule_date <= '{0}' and mr.material_request_type = 'Purchase' and not exists (SELECT po.name from `tabPurchase Order` po join `tabPurchase Order Item` poi on poi.parent = po.name where poi.material_request = mr.name)""".format(required_date),as_dict=1)
	if planned_mr:
		for row in planned_mr:
			if row.get('item_code') in on_order_stock:
				qty = flt(on_order_stock.get(row.get('item_code'))) + row.get('qty')
				on_order_stock.update({row.get('item_code'):qty})
			else:
				on_order_stock.update({row.get('item_code'):row.get('qty')})
	return on_order_stock
# fetch warehouse from Rushabh settings
def get_warehouses():
	# warehouse list
	fg_warehouse = frappe.db.sql("SELECT warehouse from `tabWarehouse Table`", as_dict = 1)
	from_warehouses = []

	if fg_warehouse:
		for row in fg_warehouse:
			warehouse_list = frappe.db.get_descendants('Warehouse', row.warehouse)
			if warehouse_list:
				for item in warehouse_list:
					from_warehouses.append(item)
			else:
				from_warehouses.append(row.warehouse)
		fg_warehouse_ll = ["'" + row + "'" for row in from_warehouses]
		fg_warehouse_list = ','.join(fg_warehouse_ll)
	else:
	    fg_warehouse_list = "' '"
	return fg_warehouse_list

def get_ohs(fg_warehouse_list):
	current_stock = frappe.db.sql("""SELECT item_code,sum(actual_qty) as qty from `tabBin` where warehouse in ({0}) group by item_code """.format(fg_warehouse_list),as_dict=1)
	ohs_dict = {item.item_code : item.qty for item in current_stock}
	return ohs_dict
def get_sales_orders(self):
	so_filter = item_filter = ""
	bom_item = "bom.item = so_item.item_code"

	date_field_mapper = {
		'from_date': ('>=', 'so.transaction_date'),
		'to_date': ('<=', 'so.transaction_date'),
		'from_delivery_date': ('>=', 'so_item.delivery_date'),
		'to_delivery_date': ('<=', 'so_item.delivery_date')
	}

	for field, value in date_field_mapper.items():
		if self.get(field):
			so_filter += f" and {value[1]} {value[0]} %({field})s"

	for field in ['customer']:
		if self.get(field):
			so_field = field
			so_filter += f" and so.{so_field} = %({field})s"

	if self.item and frappe.db.exists('Item', self.item):
		bom_item = self.get_bom_item() or bom_item
		item_filter += " and so_item.item_code = %(item_code)s"

	open_so = frappe.db.sql(f"""
		select distinct so.name, so.transaction_date, so.customer, date(so_item.delivery_date) as delivery_date,so_item.item_code,so_item.qty
		from `tabSales Order` so, `tabSales Order Item` so_item
		where so_item.parent = so.name
			and so.docstatus = 1 and so.status not in ("Stopped", "Closed") {so_filter} {item_filter}
			and (exists (select name from `tabBOM` bom where {bom_item}
					and bom.is_active = 1)
				or exists (select name from `tabPacked Item` pi
					where pi.parent = so.name and pi.parent_item = so_item.item_code
						and exists (select name from `tabBOM` bom where bom.item=pi.item_code
							and bom.is_active = 1)))
		""", self.as_dict(), as_dict=1)
	return open_so
def get_bom_item(self):
	"""Check if Item or if its Template has a BOM."""
	bom_item = None
	has_bom = frappe.db.exists({'doctype': 'BOM', 'item': self.item, 'docstatus': 1})
	if not has_bom:
		template_item = frappe.db.get_value('Item', self.item, ['variant_of'])
		bom_item = "bom.item = {0}".format(frappe.db.escape(template_item)) if template_item else bom_item
	return bom_item
