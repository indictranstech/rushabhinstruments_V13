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
		//Hide Pick List,Work Order from Create Button
		setTimeout(() => {
			 	frm.remove_custom_button('Possible Supplier', 'Get Items From');
			 	}, 10);
		// Get items from open Material Requests based on supplier
		frm.add_custom_button(__('Possible Suppliers'), function() {
			// Create a dialog window for the user to pick their supplier
			var dialog = new frappe.ui.Dialog({
				title: __('Select Possible Supplier'),
				fields: [
					{
						fieldname: 'supplier',
						fieldtype:'Link',
						options:'Supplier',
						label:'Supplier',
						reqd:1,
						description: __("Get Items from Material Requests against this Supplier")
					}
				],
				primary_action_label: __("Get Items"),
				primary_action: (args) => {
					if(!args) return;
					dialog.hide();
					if(frm.doc.suppliers.length == 1 && !frm.doc.suppliers[0].supplier){
						$.each(frm.doc.suppliers, function(idx, item_row){
							if(!item_row.supplier)
							{
								frappe.model.set_value(item_row.doctype, item_row.name, 'supplier', args.supplier);
							}

						})
					}
					else{
						var row = frappe.model.add_child(frm.doc, "Request for Quotation Supplier", "suppliers");
						frappe.model.set_value(row.doctype, row.name, 'supplier', args.supplier);
					}
					refresh_field('suppliers')
					erpnext.utils.map_current_doc({
						method: "erpnext.buying.doctype.request_for_quotation.request_for_quotation.get_item_from_material_requests_based_on_supplier",
						source_name: args.supplier,
						target: me.frm,
						setters: {
							company: me.frm.doc.company
						},
						get_query_filters: {
							material_request_type: "Purchase",
							docstatus: 1,
							status: ["!=", "Stopped"],
							per_ordered: ["<", 100]
						}
					});
					dialog.hide();
				}
			});

			dialog.show();
		}, __("Get Items From"));

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