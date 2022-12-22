frappe.ui.form.on("Batch", {
	refresh:function(frm){
		cur_frm.add_custom_button(__('Print Label'),function(){
			frappe.msgprint("-----------------")
			frappe.call({
				'method':'instrument.instrument.custom_instrument.batch.batch.print_label',
				'args':{
					batch_name:frm.doc.name,
					part_no : frm.doc.item
				},
				callback:function(r){
					
				}
			})
		})
	}
})