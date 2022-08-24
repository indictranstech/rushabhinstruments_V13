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