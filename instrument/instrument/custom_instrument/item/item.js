frappe.ui.form.on('Item',{
	refresh:function(frm){
		var prev_route = frappe.get_prev_route();
		if ("Item Mapping" == prev_route[1] || "Mapped BOM" == prev_route[1] || "BOM Creation Tool" == prev_route[1]) {
			frm.set_value("is_map_item", 1)
		}

		//Filter Engineering Revision
		cur_frm.fields_dict['engineering_revision'].get_query = function(doc, cdt, cdn) {
			return {
				filters: [
					['Engineering Revision','item_code', '=', frm.doc.item_code],
				]
			}
	    }
	    cur_frm.add_custom_button(__('Print Label'),function(){
			var dialog = new frappe.ui.Dialog({
				title: __('Item Details'),
				keep_open: true,
				fields: [
				{
					"label": "Enter No of Copies",
					"fieldname": "no_of_copies",
					"fieldtype": "Data",
					"reqd": 1
				},
				{
					"label": "Printer Name",
					"fieldname": "printer_name",
					"fieldtype": "Link",
					"options":"Printer",
					"reqd": 1
				}
				],
				onhide: () => {
				}
				});
				dialog.set_primary_action(__('Submit'), () => {
					create_label_print(frm,dialog);
					dialog.hide()
				});
				dialog.show();
		})

	},
	item_additional_label_info_template:function(frm){
		frm.doc.item_additional_custom_labels = ''
		if(frm.doc.item_additional_label_info_template){
			frappe.call({
				method : "instrument.instrument.custom_instrument.item.item.get_label_details",
				args:{
					template_name : frm.doc.item_additional_label_info_template
				},
				callback:function(r){
					if(r.message){
						$.each(r.message, function(idx,item_row) {
							var row = frappe.model.add_child(frm.doc, "Item Additional Custom Labels", "item_additional_custom_labels");
							frappe.model.set_value(row.doctype, row.name, 'label', item_row['label']);
						})
						refresh_field("item_additional_custom_labels");
					}
				}
			})
		}
	}
})
var create_label_print = function(frm,dialog){
	frappe.call({
		method: 'instrument.instrument.custom_instrument.item.item.print_label',
		// async: false,
		args: {
            "data": dialog.get_values(),
            "doc": frm.doc
        },
		callback: (r) => {
			if(r.message)
			{
				frappe.msgprint("Item Barcode Details Created. You can open it through" + r.message)

			}
		}
	});
};

