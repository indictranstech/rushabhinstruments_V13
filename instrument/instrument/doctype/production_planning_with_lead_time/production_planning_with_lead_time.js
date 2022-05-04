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

		if(!frm.doc.__islocal) {
			cur_frm.add_custom_button(__('Create Material Request'),function(){
				frappe.call({
					method: "make_material_request",
					doc: frm.doc,
					callback: function(r) {

					}
				});
			},__("Menu"))
			cur_frm.add_custom_button(__('Create Work Orders'),function(){
				frappe.call({
					method: "create_work_order",
					doc: frm.doc,
					callback: function(r) {

					}
				});
			},__("Menu"))
		}
	},
	get_sales_orders: function(frm) {
		frm.doc.sales_order_table = ''
		frappe.call({
			method: "get_open_sales_orders",
			doc: frm.doc,
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
			callback: function(r) {
				refresh_field("fg_items_table");
				// frm.save()
			}
		});
	},
	get_subassembly_items:function(frm){
		frm.doc.sub_assembly_items_table = ''
		frappe.call({
			method: "sub_assembly_items",
			doc: frm.doc,
			callback: function(r) {
				refresh_field("sub_assembly_items_table");
				// frm.save()
			}
		});
	},
	get_raw_materials:function(frm){
		frm.doc.raw_materials_table = ''
		frappe.call({
			method: "get_raw_materials",
			doc: frm.doc,
			callback: function(r) {
				refresh_field("raw_materials_table");
				// frm.save()
			}
		});
	},
	prepare_final_work_orders:function(frm){
		frm.doc.final_work_orders = ''
		frappe.call({
			method: "prepare_final_work_orders",
			doc: frm.doc,
			callback: function(r) {
				refresh_field("final_work_orders");
				// frm.save()
			}
		});
	}
});
