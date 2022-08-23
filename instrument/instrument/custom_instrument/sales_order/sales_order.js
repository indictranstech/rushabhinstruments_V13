frappe.ui.form.on('Sales Order', {
	refresh: function(frm) {
		setTimeout(() => {
		 	frm.remove_custom_button('Pick List', 'Create');
		 }, 10);

		frm.trigger("add_consolidated_pick_list_button")		
	},


	add_consolidated_pick_list_button: function(frm){
		frm.call({
			method: "instrument.instrument.custom_instrument.sales_order.sales_order.get_fg_item_for_consolidated_pick_list",
			"args" : {
				doc : frm.doc
			},
			callback: function(r){
				if (r.message){
					frm.trigger("add_consolidated_button")
				}
			}
		})
	},

	add_consolidated_button: function(frm) { 
		frm.add_custom_button(__('Consolidated Pick List'), function() {
			frappe.model.open_mapped_doc({
				method: "instrument.instrument.custom_instrument.sales_order.sales_order.make_consolidated_pick_list",
				frm: cur_frm
			})
		}, __('Create'));
	}						
});
