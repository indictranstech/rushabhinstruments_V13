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
		if(frm.doc.items){
			cur_frm.fields_dict["items"].$wrapper.find('.grid-body .rows').find(".grid-row").each(function(i, item) {
				let d = locals[cur_frm.fields_dict["items"].grid.doctype][$(item).attr('data-name')];
				if(d["engineering_revision"] != d["default_engineering_revision"]){
					$(item).find('.grid-static-col').css({'background-color': '#FF0000'});
				}
				else{
					$(item).find('.grid-static-col').css({'background-color': '#FFFFFF'});
				}
			});
		}
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