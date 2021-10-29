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
							$.each(r.message, function(idx, item_row){
								
									var row = frappe.model.add_child(frm.doc, "BOM Creation Attribute Table", "attribute_table");
									frappe.model.set_value(row.doctype, row.name, 'mapped_item', item_row['mapped_item']);
									frappe.model.set_value(row.doctype,row.name,'attribute',item_row['attribute']);
								});
							refresh_field('attribute_table')
						}
					}
				})
		}
		}
	}
});
