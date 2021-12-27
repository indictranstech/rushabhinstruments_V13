frappe.ui.form.on('Production Plan', {
	refresh:function(frm){
		//Hide Pick List,Work Order from Create Button
		setTimeout(() => {
			 	frm.remove_custom_button('Work Order / Subcontract PO', 'Create');
			 	}, 10);
		if (frm.doc.po_items && frm.doc.status !== "Closed" && frm.doc.docstatus == 1) {
			frm.add_custom_button(__('Work Orders / Subcontract PO'), () => frm.events.create_work_orders(frm),
					__("Create"));
		}
		
	},
	create_work_orders:function(frm){
		frappe.call({
			method : "instrument.instrument.custom_instrument.production_plan.production_plan.make_work_order",
			freeze: true,
			args : {
				doc : frm.doc
			},
			callback:function(r){
				frm.reload_doc();
			}
		})
	}
})