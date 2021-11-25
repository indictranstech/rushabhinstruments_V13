// Copyright (c) 2021, instrument and contributors
// For license information, please see license.txt

frappe.ui.form.on('BOM Creation Tool', {
	attribute_table_on_form_rendered:function(frm, cdt, cdn){
		// hide delete, insert above and insert below fields inside Attribute  child table
		frm.fields_dict['attribute_table'].grid.wrapper.find('.grid-delete-row').hide();
		frm.fields_dict['attribute_table'].grid.wrapper.find('.grid-insert-row-below').hide();
		frm.fields_dict['attribute_table'].grid.wrapper.find('.grid-insert-row').hide();
	},
	refresh: function(frm) {
		frm.fields_dict['attribute_table'].grid.wrapper.find('.grid-insert-row').hide();
		frm.fields_dict['attribute_table'].grid.wrapper.find('.grid-insert-row-below').hide();
		frm.fields_dict['attribute_table'].grid.wrapper.find('.grid-add-row').hide();

		//Filter Items
		frm.set_query("value", "attribute_table", function(doc, cdt, cdn) {
			const row = locals[cdt][cdn];
			return {
				query: "instrument.instrument.doctype.bom_creation_tool.bom_creation_tool.get_attribute_value",
				filters:{ 'attribute': row.attribute }
			}
		});
		frm.set_query("standard_bom", "review_item_mapping", function(doc, cdt, cdn) {
			const row = locals[cdt][cdn];
			return {
				query: "instrument.instrument.doctype.bom_creation_tool.bom_creation_tool.get_standard_bom_for_query",
				filters:{ 'standard_item_code': row.standard_item_code }
			}
		});
		if(frm.doc.docstatus==0 &&  !frm.doc.__islocal){
			cur_frm.add_custom_button(__('Copy Attribute Value'),function(){
				return frm.call({
					doc: frm.doc,
					method: "copy_to_all_rows",
					freeze: true,
					callback: function(r) {
						if(r.message == true){
							frappe.msgprint("Copied Successfully");
						}
					}
				});
			})
		}
	},
	onload:function(frm){
		if(frm.doc.__islocal){
			// Fetch all the attributes for mapped item
			if(frm.doc.mapped_bom){
				frappe.call({
					"method":"instrument.instrument.doctype.bom_creation_tool.bom_creation_tool.get_map_item_attributes",
					"args":{
						mapped_bom : frm.doc.mapped_bom
					},
					callback:function(r){
						if(r.message){
							if(r.message[1]==true){
								$.each(r.message[0], function(idx, item_row){
									var row = frappe.model.add_child(frm.doc, "BOM Creation Attribute Table", "attribute_table");
									frappe.model.set_value(row.doctype, row.name, 'mapped_bom', item_row['mapped_bom']);
									frappe.model.set_value(row.doctype, row.name, 'mapped_item', item_row['mapped_item']);
									frappe.model.set_value(row.doctype,row.name,'attribute',item_row['attribute']);
									frappe.model.set_value(row.doctype,row.name,'value',item_row['value']);
								})

							}else{
								$.each(r.message[0], function(idx, item_row){
									if(item_row['attribute_list'].length == 1){
										var row = frappe.model.add_child(frm.doc, "BOM Creation Attribute Table", "attribute_table");
										frappe.model.set_value(row.doctype, row.name, 'mapped_bom', item_row['parent']);
										frappe.model.set_value(row.doctype, row.name, 'mapped_item', item_row['item_code']);
										frappe.model.set_value(row.doctype,row.name,'attribute',item_row['attribute_list'][0]["attribute"]);
									}else{
										$.each(item_row['attribute_list'], function(idx, col){
											var row = frappe.model.add_child(frm.doc, "BOM Creation Attribute Table", "attribute_table");
											frappe.model.set_value(row.doctype, row.name, 'mapped_bom', item_row['parent']);
											frappe.model.set_value(row.doctype, row.name, 'mapped_item', item_row['item_code']);
											frappe.model.set_value(row.doctype,row.name,'attribute',col["attribute"]);

										})
									}
								});
							}
							
							refresh_field('attribute_table')
						}
					}
				})
		}
		}
	},
	validate:function(frm){
		if(frm.doc.__islocal){
			// Fetch all the attributes for mapped item
			if(frm.doc.mapped_bom){
				frappe.call({
					"method":"instrument.instrument.doctype.bom_creation_tool.bom_creation_tool.get_map_item_attributes",
					"args":{
						mapped_bom : frm.doc.mapped_bom
					},
					callback:function(r){
						if(r.message){
							if(r.message[1]==true){
								$.each(r.message[0], function(idx, item_row){
									var row = frappe.model.add_child(frm.doc, "BOM Creation Attribute Table", "attribute_table");
									frappe.model.set_value(row.doctype, row.name, 'mapped_bom', item_row['mapped_bom']);
									frappe.model.set_value(row.doctype, row.name, 'mapped_item', item_row['mapped_item']);
									frappe.model.set_value(row.doctype,row.name,'attribute',item_row['attribute']);
									frappe.model.set_value(row.doctype,row.name,'value',item_row['value']);
								})

							}else{
								$.each(r.message[0], function(idx, item_row){
									if(item_row['attribute_list'].length == 1){
										var row = frappe.model.add_child(frm.doc, "BOM Creation Attribute Table", "attribute_table");
										frappe.model.set_value(row.doctype, row.name, 'mapped_bom', item_row['parent']);
										frappe.model.set_value(row.doctype, row.name, 'mapped_item', item_row['item_code']);
										frappe.model.set_value(row.doctype,row.name,'attribute',item_row['attribute_list'][0]["attribute"]);
									}else{
										$.each(item_row['attribute_list'], function(idx, col){
											var row = frappe.model.add_child(frm.doc, "BOM Creation Attribute Table", "attribute_table");
											frappe.model.set_value(row.doctype, row.name, 'mapped_bom', item_row['parent']);
											frappe.model.set_value(row.doctype, row.name, 'mapped_item', item_row['item_code']);
											frappe.model.set_value(row.doctype,row.name,'attribute',col["attribute"]);

										})
									}
								});
							}
							
							refresh_field('attribute_table')
						}
					}
				})
		}
		}
		refresh_field('review_item_mapping')

	},
	review_item_mappings:function(frm){
		return frm.call({
					doc: frm.doc,
					method: "review_item_mappings",
					freeze: true,
					callback: function(r) {
					}
				});
	}
});
frappe.ui.form.on('Review Item Mapping', {
	standard_item_code:function(frm,cdt,cdn){
		var row = locals[cdt][cdn]
		if(row.standard_item_code){
			frappe.call({
					method : 'instrument.instrument.doctype.bom_creation_tool.bom_creation_tool.get_standard_bom',
					args : {
						standard_item_code : row.standard_item_code,
						mapped_item : row.mapped_item

					},
					callback:function(r){
						if(r.message){
							if(r.message == false){
							var df = frappe.meta.get_docfield("Review Item Mapping","standard_bom", cur_frm.doc.name);
							df.read_only = 1;
							
						}else{
							frappe.model.set_value(row.doctype, row.name, 'standard_bom', r.message);
						}
						}
						
					}
				})
		}
	},
})