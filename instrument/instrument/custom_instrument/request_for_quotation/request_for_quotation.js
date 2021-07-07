// Copyright (c) 2021, instrument and contributors
// For license information, please see license.txt

frappe.ui.form.on('Request for Quotation', {
	// refresh: function(frm) {

	// }
});


frappe.ui.form.on('Request for Quotation Supplier', {
    send_email: function(frm, cdt, cdn) {
		let row = locals[cdt][cdn]
		if (row.send_email){
			frappe.model.set_value(cdt,cdn,'without_url_email', 0)
		}
    },

    without_url_email: function(frm, cdt, cdn) {
		let row = locals[cdt][cdn]
		if (row.without_url_email){
			frappe.model.set_value(cdt,cdn,'send_email', 0)
		}
    }

});