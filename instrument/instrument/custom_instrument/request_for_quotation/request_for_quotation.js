// Copyright (c) 2021, instrument and contributors
// For license information, please see license.txt

frappe.ui.form.on('Request for Quotation', {
	refresh: function(frm) {
		frm.set_query("engineering_revision", "items", function(doc, cdt, cdn) {
			const row = locals[cdt][cdn];
			return {
				query: "instrument.instrument.custom_instrument.request_for_quotation.request_for_quotation.get_engineering_revisions_for_filter",
				filters:{ 'item_code': row.item_code }
			}
		});	
	}
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
frappe.ui.form.on('Request for Quotation Item', {
    item_code: function(frm, cdt, cdn) {
		var row = locals[cdt][cdn]
		if(row.item_code){
			frappe.call({
				"method" :"instrument.instrument.custom_instrument.request_for_quotation.request_for_quotation.get_engineering_revision",
				"args" : {
					item_code : row.item_code,
				},
				callback:function(r){
					if(r.message){
						frappe.model.set_value(row.doctype, row.name, 'engineering_revision', r.message)
					}
				}
			})
		}
    }
});