// Copyright (c) 2023, instrument and contributors
// For license information, please see license.txt

frappe.ui.form.on('Barcodes', {
	refresh: function(frm) {
		if(frm.doc.docstatus == 0 || frm.doc.docstatus == 1){
			frm.add_custom_button(__('Export Excel'), function() {
				
          		frappe.call({
					'method':"instrument.instrument.doctype.barcodes.barcodes.get_barcode_details",
					'args': {doc:frm.doc},
					callback: function(r) {
						if(frm.doc.doctype_name == 'Batch'){
							var w = window.open(
							frappe.urllib.get_full_url(
							"/api/method/instrument.instrument.doctype.barcodes.barcodes.download_xlsx_batch?"));

							if(!w)
								frappe.msgprint(__("Please enable pop-ups")); return;
						}
						if(frm.doc.doctype_name == 'Item'){
							var w = window.open(
							frappe.urllib.get_full_url(
							"/api/method/instrument.instrument.doctype.barcodes.barcodes.download_xlsx_item?"));

							if(!w)
								frappe.msgprint(__("Please enable pop-ups")); return;
						}
						if(frm.doc.doctype_name == 'Work Order'){
							var w = window.open(
							frappe.urllib.get_full_url(
							"/api/method/instrument.instrument.doctype.barcodes.barcodes.download_xlsx_wo?"));

							if(!w)
								frappe.msgprint(__("Please enable pop-ups")); return;
						}
						if(frm.doc.doctype_name == 'Stock Entry'){
							var w = window.open(
							frappe.urllib.get_full_url(
							"/api/method/instrument.instrument.doctype.barcodes.barcodes.download_xlsx_se?"));

							if(!w)
								frappe.msgprint(__("Please enable pop-ups")); return;
						}
						
						if(frm.doc.doctype_name == 'Job Card'){
							var w = window.open(
							frappe.urllib.get_full_url(
							"/api/method/instrument.instrument.doctype.barcodes.barcodes.download_xlsx_jc?"));

							if(!w)
								frappe.msgprint(__("Please enable pop-ups")); return;
						}
						
						if(frm.doc.doctype_name == 'Pick List'){
							var w = window.open(
							frappe.urllib.get_full_url(
							"/api/method/instrument.instrument.doctype.barcodes.barcodes.download_xlsx_pl?"));

							if(!w)
								frappe.msgprint(__("Please enable pop-ups")); return;
						}
						
					}
				})			
			})
		}
	}
});
