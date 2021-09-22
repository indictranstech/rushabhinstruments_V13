frappe.ui.form.on("Purchase Order", {
	refresh:function(frm){
		//Filter Engineering Revision
		frm.set_query("engineering_revision", "items", function(doc, cdt, cdn) {
			const row = locals[cdt][cdn];
			return {
				query: "instrument.instrument.custom_instrument.purchase_order.purchase_order.get_engineering_revisions_for_filter",
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
})
frappe.ui.form.on('Purchase Order Item', {
    item_code: function(frm, cdt, cdn) {
		var row = locals[cdt][cdn]
		if(row.item_code){
			frappe.call({
				"method" :"instrument.instrument.custom_instrument.request_for_quotation.request_for_quotation.get_engineering_revision",
				"args" : {
					item_code : row.item_code
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