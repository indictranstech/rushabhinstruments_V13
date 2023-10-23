// Copyright (c) 2022, instrument and contributors
// For license information, please see license.txt

frappe.ui.form.on('Production Planning With Lead Time', {
	sales_order_table_on_form_rendered:function(frm, cdt, cdn){
		// hide delete, insert above and insert below fields inside sales_order_table
		frm.fields_dict['sales_order_table'].grid.wrapper.find('.grid-delete-row').hide();
		frm.fields_dict['sales_order_table'].grid.wrapper.find('.grid-insert-row-below').hide();
		frm.fields_dict['sales_order_table'].grid.wrapper.find('.grid-insert-row').hide();
	},
	sorted_sales_order_table_on_form_rendered:function(frm, cdt, cdn){
		// hide delete, insert above and insert below fields inside sorted_sales_order_table
		frm.fields_dict['sorted_sales_order_table'].grid.wrapper.find('.grid-delete-row').hide();
		frm.fields_dict['sorted_sales_order_table'].grid.wrapper.find('.grid-insert-row-below').hide();
		frm.fields_dict['sorted_sales_order_table'].grid.wrapper.find('.grid-insert-row').hide();
	},
	fg_items_table_on_form_rendered:function(frm, cdt, cdn){
		// hide delete, insert above and insert below fields inside sorted_sales_order_table
		frm.fields_dict['fg_items_table'].grid.wrapper.find('.grid-delete-row').hide();
		frm.fields_dict['fg_items_table'].grid.wrapper.find('.grid-insert-row-below').hide();
		frm.fields_dict['fg_items_table'].grid.wrapper.find('.grid-insert-row').hide();
	},
	refresh:function(frm){
		frm.fields_dict['sales_order_table'].grid.wrapper.find('.grid-insert-row').hide();
		frm.fields_dict['sales_order_table'].grid.wrapper.find('.grid-insert-row-below').hide();
		frm.fields_dict['sales_order_table'].grid.wrapper.find('.grid-add-row').hide();

		frm.fields_dict['sorted_sales_order_table'].grid.wrapper.find('.grid-insert-row').hide();
		frm.fields_dict['sorted_sales_order_table'].grid.wrapper.find('.grid-insert-row-below').hide();
		frm.fields_dict['sorted_sales_order_table'].grid.wrapper.find('.grid-add-row').hide();

		frm.fields_dict['fg_items_table'].grid.wrapper.find('.grid-insert-row').hide();
		frm.fields_dict['fg_items_table'].grid.wrapper.find('.grid-insert-row-below').hide();
		frm.fields_dict['fg_items_table'].grid.wrapper.find('.grid-add-row').hide();

		if(frm.doc.docstatus == 1) {
			cur_frm.add_custom_button(__('Create Material Request'),function(){
				frappe.call({
					method: "make_material_request",
					freeze : true,
					freeze_message: __("Creating Material Requests..."),
					doc: frm.doc,
					callback: function(r) {

					}
				});
			},__("Menu"))
			cur_frm.add_custom_button(__('Create Work Orders'),function(){
				frappe.call({
					method: "create_work_order",
					freeze : true,
					freeze_message: __("Creating Work Orders..."),
					doc: frm.doc,
					callback: function(r) {

					}
				});
			},__("Menu"))
		}
	},
	validate:function(frm){
		frm.set_value("status","Draft")

	},
	get_sales_orders: function(frm) {
		frm.doc.sales_order_table = ''
		frappe.call({
			method: "get_open_sales_orders",
			doc: frm.doc,
			freeze: true,
			callback: function(r) {
				refresh_field("sales_order_table");
			}
		});
	},
	sort_so_data:function(frm){
		frm.doc.sorted_sales_order_table = ''
		frappe.call({
			method: "sort_so_data",
			doc: frm.doc,
			freeze: true,
			callback: function(r) {
				refresh_field("sorted_sales_order_table");
			}
		});
	},
	work_order_planning:function(frm){
		frm.doc.fg_items_table = ''
		frappe.call({
			method: "work_order_planning",
			doc: frm.doc,
			freeze: true,
			freeze_message: __("Fetching FG items..."),
			callback: function(r) {
				refresh_field("fg_items_table");
			}
		});
	},
	get_subassembly_items:function(frm){
		frm.doc.sub_assembly_items_table = ''
		frappe.call({
			method: "sub_assembly_items",
			doc: frm.doc,
			freeze: true,
			freeze_message: __("Fetching SFG items..."),
			callback: function(r) {
				refresh_field("sub_assembly_items_table");
			}
		});
	},
	get_raw_materials:function(frm){
		frm.doc.raw_materials_table = ''
		frappe.call({
			method: "get_raw_materials",
			doc: frm.doc,
			freeze: true,
			freeze_message: __("Fetching Raw items..."),
			callback: function(r) {
				refresh_field("raw_materials_table");
				cur_frm.save()
			}
		});
	},
	refresh_latest_date_availability:function(frm){
		frm.doc.raw_materials_table = ''
		frappe.call({
			method: "get_raw_materials",
			doc: frm.doc,
			freeze: true,
			freeze_message: __("Refresh Latest Date Availability For Raw items..."),
			callback: function(r) {
				refresh_field("raw_materials_table");
				cur_frm.save()
			}
		});
	},
	download_raw_materials:function(frm){
		if (!(frm.doc.__islocal==1)){
			frappe.call({
				method: "download_raw_material",
				doc: frm.doc,
				callback: function(r) {
					if (r.message){
						var w = window.open(
							frappe.urllib.get_full_url(
							"/api/method/instrument.instrument.doctype.production_planning_with_lead_time.production_planning_with_lead_time.download_xlsx?"+"fname="+ encodeURIComponent(r.message)));		
							if(!w)
								frappe.msgprint(__("Please enable pop-ups")); return;
					}	
				}
			})
		}
	},
	prepare_final_work_orders:function(frm){
		frm.doc.final_work_orders = ''
		frappe.call({
			method: "prepare_final_work_orders",
			doc: frm.doc,
			freeze: true,
			freeze_message: __("Preparing Work Orders For FG items..."),
			callback: function(r) {
				refresh_field("final_work_orders");
			}
		});
	}
});
