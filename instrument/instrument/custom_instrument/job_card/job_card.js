frappe.ui.form.on("Job Card", {
	refresh:function(frm){
		//Filter Engineering Revision
		frm.set_query("engineering_revision", "items", function(doc, cdt, cdn) {
			const row = locals[cdt][cdn];
			return {
				query: "instrument.instrument.custom_instrument.bom.bom.get_engineering_revisions_for_filter",
				filters:{ 'item_code': row.item_code }
			}
		});	
	}
});
frappe.ui.form.on('Job Card Item', {
    item_code: function(frm, cdt, cdn) {
		var row = locals[cdt][cdn]
		if(row.item_code){
			frappe.call({
				"method" :"instrument.instrument.custom_instrument.job_card.job_card.get_engineering_revision",
				"args" : {
					item_code : row.item_code,
					work_order : frm.doc.work_order
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