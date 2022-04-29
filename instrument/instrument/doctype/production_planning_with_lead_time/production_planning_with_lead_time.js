// Copyright (c) 2022, instrument and contributors
// For license information, please see license.txt

frappe.ui.form.on('Production Planning With Lead Time', {
	get_sales_orders: function(frm) {
		frm.doc.sales_orders_table = ''
		frappe.call({
			method: "get_open_sales_orders",
			doc: frm.doc,
			callback: function(r) {
				refresh_field("sales_orders_table");
				frm.save()
			}
		});
	},
	sort_so_data:function(frm){
		frm.doc.sorted_sales_orders_table = ''
		frappe.call({
			method: "sort_so_data",
			doc: frm.doc,
			callback: function(r) {
				refresh_field("sorted_sales_order_table");
				// frm.save()
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
	}
});
