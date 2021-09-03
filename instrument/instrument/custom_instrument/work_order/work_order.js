frappe.ui.form.on('Work Order', {
	refresh: function(frm) {
		console.log("--------------")
		//Filter Engineering Revision
		frm.set_query("engineering_revision", "required_items", function(doc, cdt, cdn) {
			const row = locals[cdt][cdn];
			return {
				query: "instrument.instrument.custom_instrument.work_order.work_order.get_engineering_revisions_for_filter",
				filters:{ 'item_code': row.item_code }
			}
		});	
		if(frm.doc.required_items){
			frm.doc.required_items.forEach(function(row){
				if(row['item_code']){
					frappe.call({
						"method" :"instrument.instrument.custom_instrument.work_order.work_order.get_engineering_revision",
						"args" : {
							item_code : row['item_code']
						},
						callback:function(r){
							if(r.message){
								frappe.model.set_value(row.doctype, row.name, 'engineering_revision', r.message)
							}
						}
					})
				}

			})
		}
		
	}
});
