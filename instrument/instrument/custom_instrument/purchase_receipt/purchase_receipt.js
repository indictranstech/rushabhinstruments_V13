frappe.ui.form.on("Purchase Receipt", {
	refresh:function(frm){
		if(frm.doc.__islocal){
			frm.set_value("apply_putaway_rule",1)

		}
		//Filter Engineering Revision
		frm.set_query("engineering_revision", "items", function(doc, cdt, cdn) {
			const row = locals[cdt][cdn];
			return {
				query: "instrument.instrument.custom_instrument.purchase_order.purchase_order.get_engineering_revisions_for_filter",
				filters:{ 'item_code': row.item_code }
			}
		});	
		// //Filter Accepted warehouse
		// frm.set_query("warehouse", "items", function(doc, cdt, cdn) {
		// 	const row = locals[cdt][cdn];
		// 	return {
		// 		query: "instrument.instrument.custom_instrument.purchase_receipt.purchase_receipt.get_warehouse_for_query",
		// 		filters:{ 'parent': row.item_code }
		// 	}
		// });	
	}
})
frappe.ui.form.on('Purchase Receipt Item', {	
	item_code: function(frm, cdt, cdn){
		var row = locals[cdt][cdn]
		if(row.item_code && row.purchase_order_item){
			frappe.call({
				"method" :"instrument.instrument.custom_instrument.purchase_receipt.purchase_receipt.get_engineering_revision",
				"args" : {
					item_code : row.item_code,
					purchase_order_item : row.purchase_order_item
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