// Copyright (c) 2021, instrument and contributors
// For license information, please see license.txt

frappe.ui.form.on('Mapped BOM', {
	refresh: function(frm) {
		// Add button Create BOM Tree on Mapped BOM
		if(frm.doc.docstatus == 1){
			cur_frm.add_custom_button(__('Create BOM Tree'),function(){
				frappe.set_route("Form","BOM Creation Tool", "new bom creation tool");
				frappe.route_options = {"mapped_bom": frm.doc.name}	

			})
		}
		cur_frm.fields_dict['item'].get_query = function(doc, cdt, cdn) {
			return {
				filters: [
					['Item','is_map_item', '=', 1],
				]
			}
	    }
		frm.set_query("mapped_bom", "items", function(doc, cdt, cdn) {
			const row = locals[cdt][cdn];
			return {
				query: "instrument.instrument.doctype.mapped_bom.mapped_bom.get_mapped_bom",
				filters:{ 'item_code': row.item_code }
			}
		});
		frm.set_query("bom_no", "items", function(doc, cdt, cdn) {
			const row = locals[cdt][cdn];
			return {
				query: "instrument.instrument.doctype.mapped_bom.mapped_bom.get_bom",
				filters:{ 'item_code': row.item_code }
			}
		});
		//Filter Items
		frm.set_query("item_code", "items", function(doc, cdt, cdn) {
			const row = locals[cdt][cdn];
			return {
				query: "instrument.instrument.doctype.mapped_bom.mapped_bom.get_items",
				filters:{ 'is_map_item': row.is_map_item }
			}
		});

	}
});
frappe.ui.form.on('Mapped BOM Item', {
	is_map_item:function(frm,cdt,cdn){
		var row = locals[cdt][cdn]
		if(row.is_map_item){
			cur_frm.fields_dict['items'].grid.get_field("item_code").get_query = function(doc, cdt, cdn) {
					return {
						filters: [
							["Item", "is_map_item", "=", 1]
						]
					}
				};
			frappe.model.set_value(row.doctype, row.name, 'bom_no','')
		}

		
	},
	item_code:function(frm,cdt,cdn){
		var row = locals[cdt][cdn]
		if(row.item_code){
			frappe.call({
				method : "instrument.instrument.doctype.mapped_bom.mapped_bom.get_default_bom",
				args:{
					item_code : row.item_code
				},
				callback:function(r){
					if(r.message){
						if(r.message[1] == 'No'){
							frappe.model.set_value(cdt, cdn, 'bom_no', r.message[0]);
						}else{
							frappe.model.set_value(cdt, cdn, 'mapped_bom', r.message[0]);
						}
						
					}
				}
			})
		}

	}
})