frappe.ui.form.on('Delivery Note',{
	delivery_note_additional_label_info_template:function(frm){
		frm.doc.delivery_note_additional_custom_labels = ''
		if(frm.doc.delivery_note_additional_label_info_template){
			frappe.call({
				method : "instrument.instrument.custom_instrument.delivery_note.delivery_note.get_label_details",
				args:{
					template_name : frm.doc.delivery_note_additional_label_info_template
				},
				callback:function(r){
					if(r.message){
						$.each(r.message, function(idx,item_row) {
							var row = frappe.model.add_child(frm.doc, "Delivery Note Additional Custom Labels", "delivery_note_additional_custom_labels");
							frappe.model.set_value(row.doctype, row.name, 'label', item_row['label']);
						})
						refresh_field("delivery_note_additional_custom_labels");
					}
				}
			})
		}
	}
})