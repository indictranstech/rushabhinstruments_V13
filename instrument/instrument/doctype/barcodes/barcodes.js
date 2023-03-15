// Copyright (c) 2023, instrument and contributors
// For license information, please see license.txt

frappe.ui.form.on('Barcodes', {
	refresh: function(frm) {
		if(frm.doc.docstatus == 0 || frm.doc.docstatus == 1){
			cur_frm.add_custom_button(__('Export'),function(){
				frappe.msgprint("================")
			})
		}

	}
});
