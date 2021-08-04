frappe.ui.form.on("Purchase Receipt", {
	refresh:function(frm){
		//Filter Accepted warehouse
		frm.set_query("warehouse", "items", function(doc, cdt, cdn) {
			const row = locals[cdt][cdn];
			return {
				query: "instrument.instrument.custom_instrument.purchase_receipt.purchase_receipt.get_warehouse_for_query",
				filters:{ 'parent': row.item_code }
			}
		});	
	}
})