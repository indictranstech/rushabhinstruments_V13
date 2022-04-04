// Copyright (c) 2022, instrument and contributors
// For license information, please see license.txt

frappe.ui.form.on('Production Planning With Lead Time', {
	// refresh: function(frm) {

	// }
	get_sales_orders: function(frm) {
		frappe.msgprint("**************")
		frappe.call({
			method: "get_open_sales_orders",
			doc: frm.doc,
			callback: function(r) {
				refresh_field("sales_orders");
			}
		});
	},
});
