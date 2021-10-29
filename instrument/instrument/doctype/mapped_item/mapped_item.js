// Copyright (c) 2021, instrument and contributors
// For license information, please see license.txt

frappe.ui.form.on('Mapped Item', {
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