// Copyright (c) 2021, instrument and contributors
// For license information, please see license.txt

frappe.ui.form.on('Item Mapping', {
	refresh: function(frm) {

		//Display list of customers who are not distributors
		cur_frm.fields_dict['mapped_item'].get_query = function(doc, cdt, cdn) {
			return {
				filters: [
					['Item','is_map_item', '=', 1],
				]
			}
	    }
	    cur_frm.fields_dict['item_code'].get_query = function(doc, cdt, cdn) {
			return {
				filters: [
					['Item','is_map_item', '=', 0],
				]
			}
	    }
	    //Filter Items
		frm.set_query("value", "attribute_table", function(doc, cdt, cdn) {
			const row = locals[cdt][cdn];
			return {
				query: "instrument.instrument.doctype.bom_creation_tool.bom_creation_tool.get_attribute_value",
				filters:{ 'attribute': row.attribute }
			}
		});
		frm.set_query("attribute", "attribute_table", function(doc, cdt, cdn) {
			const row = locals[cdt][cdn];
			return {
				query: "instrument.instrument.doctype.item_mapping.item_mapping.get_attribute_in_table",
				filters:{ 'mapped_item': frm.doc.mapped_item }
			}
		});
		if(!frm.doc.__islocal){
			frappe.call({
				method : "instrument.instrument.doctype.item_mapping.item_mapping.check_propogation_for_item_mapping",
				args:{
					doc : frm.doc
				},
				callback:function(r){

				}

			})
		}
		if(frm.doc.propogate_updates_to_affected_boms_status == "Need To Run"){
			frm.add_custom_button(__('Propogate Updates to Affected BOMs'), function() {
				frappe.call({
					method: "instrument.instrument.doctype.item_mapping.item_mapping.propogate_updates_to_affected_boms",
					freeze: true,
					args: {
						doc : frm.doc
						}
					});
				}, __("Menu"));

			}	
	},
	mapped_item:function(frm){
		if(frm.doc.mapped_item){
			frappe.call({
				method: "instrument.instrument.doctype.item_mapping.item_mapping.get_attributes",
				args : {
					mapped_item : frm.doc.mapped_item
				},
				callback:function(r){
					if(r.message){
						$.each(r.message,function(idx,item_row){
							var row = frappe.model.add_child(frm.doc, "Attribute Table", "attribute_table");
							frappe.model.set_value(row.doctype, row.name, 'attribute', item_row['attribute']);
						})
						frm.refresh_field("attribute_table");
					}
				}
			})
		}
	},
	item_code:function(frm){
		if(!frm.doc.__islocal){
			if(!frm.doc.old_standrad_item_code){
				frappe.throw("Please Enter Old Standard Item Code")

			}
		}
	}
});
frappe.ui.form.on('Attribute Table',{
	// attribute:function(frm,cdt,cdn){
	// 	var row = locals[cdt][cdn]
	// 	frappe.call({
	// 		method : "instrument.instrument.doctype.mapped_item.mapped_item.get_attribute_value",
	// 		args:{
	// 			attribute : row.attribute
	// 		},
	// 		callback:function(r){
	// 			if(r.message){
	// 				var options = [];
	// 				$.each(r.message, function(idx, item_row){
	// 					options.push(item_row.attribute_value)
	// 				})
	// 				frm.fields_dict.attribute_table.grid.update_docfield_property('value','options',[''].concat(options));
	// 			}
	// 		}
	// 	})
	// }
    
});