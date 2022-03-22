frappe.ui.form.on('Material Request', {
	setup: function(frm) {
		frm.custom_make_buttons = {
			'Stock Entry': 'Issue Material',
			'Pick List': 'Pick List',
			'Purchase Order': 'Purchase Orders',
			'Request for Quotation': 'Request for Quotation',
			'Supplier Quotation': 'Supplier Quotation',
			'Work Order': 'Work Order',
			'Purchase Receipt': 'Purchase Receipt'
		};
	},
	refresh:function(frm){
		//Hide Pick List,Work Order from Create Button
		setTimeout(() => {
			 	frm.remove_custom_button('Purchase Order', 'Create');
			 	}, 10);
		

     
		if (frm.doc.material_request_type === "Purchase") {
			frm.add_custom_button(__('Purchase Orders'),
				() => frm.events.make_purchase_order(frm), __('Create'));
		}
	},
	make_purchase_order: function(frm) {
		frappe.prompt(
			{
				label: __('For Default Supplier (Optional)'),
				fieldname:'default_supplier',
				fieldtype: 'Link',
				options: 'Supplier',
				description: __('Select a Supplier from the Default Suppliers of the items below. On selection, a Purchase Order will be made against items belonging to the selected Supplier only.'),
				get_query: () => {
					return{
						query: "instrument.instrument.custom_instrument.material_request.material_request.get_default_supplier_query",
						filters: {'doc': frm.doc.name}
					}
				}
			},
			(values) => {
				frappe.model.open_mapped_doc({
					method: "erpnext.stock.doctype.material_request.material_request.make_purchase_order",
					frm: frm,
					args: { default_supplier: values.default_supplier },
					run_link_triggers: true
				});
			},
			__('Enter Supplier'),
			__('Create')
		)
	}

})
frappe.ui.form.on('Material Request Item', {
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