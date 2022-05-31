// Copyright (c) 2021, instrument and contributors
// For license information, please see license.txt

frappe.ui.form.on('Package Document', {
	refresh: function(frm) {
		frm.add_custom_button(__('Copy Rows'),() => frm.events.copy(frm));
	},
	copy:function(frm){
		let selected_rows_from_attachment = []
		let selected_rows_from_file_locations = []
		frm.doc.attachment.forEach(function(row){
			if(row.__checked == 1){
				selected_rows_from_attachment.push(row)
			}

		})
		frm.doc.file_locations.forEach(function(row){
			if(row.__checked == 1){
				selected_rows_from_file_locations.push(row)
			}
		})
		if(selected_rows_from_attachment.length == 0 && selected_rows_from_file_locations.length ==0 ){
			frappe.throw("Please Select the Document")
		}
		var dialog = new frappe.ui.Dialog({
			title: 'Enter Package Document',
				fields: [
				{	"fieldtype": "Link", 
					"label": __("Package Document"), 
					"fieldname": "package_document",
					"options":"Package Document",
					"description":"Package document where the selected attachments to be copy",
					"get_query": function(){ return {'filters': [['item_code','=',frm.doc.item_code],['revision','=',frm.doc.revision]]}}
					// "reqd": 1
				},
				{	
					"fieldtype": "Button", 
					"label": __("Submit"), 
					"fieldname": "add_package_doc"
				}
				]
		});
		dialog.fields_dict.add_package_doc.input.onclick = function() {
			var package_document = $("input[data-fieldname='package_document']").val();
			if(selected_rows_from_attachment.length >0){
				frappe.call({
					"method":"instrument.instrument.doctype.package_document.package_document.copy_doc_to_other_doc",
					"args" :{
						item_list : selected_rows_from_attachment,
						package_type : frm.doc.package_type,
						item_code : frm.doc.item_code,
						revision : frm.doc.revision,
						docname :frm.doc.name,
						package_document:package_document
					},
					callback:function(r){
						location.reload()

					}
				})
			}
			if(selected_rows_from_file_locations.length > 0){
				frappe.call({
					"method":"instrument.instrument.doctype.package_document.package_document.copy_doc_to_other_doc_for_file",
					"args" : {
						item_list : selected_rows_from_file_locations,
						package_type : frm.doc.package_type,
						item_code : frm.doc.item_code,
						revision :frm.doc.revision,
						docname :frm.doc.name,
						package_document:package_document
					},
					callback:function(r){
						location.reload()

					}
				})
			}
			dialog.hide()
		}
		dialog.show();
	}
});


