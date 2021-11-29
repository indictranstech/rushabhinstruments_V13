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
			if(frm.doc.docstatus == 1 && frm.doc.check_propogation_to_descendent_bom && frm.doc.propogate_to_descendent_bom==0){
				cur_frm.add_custom_button(__('Propogate Updates to Descendent BOMs'),function(){
					frappe.call({
						method: "instrument.instrument.doctype.mapped_bom.mapped_bom.propogate_update_to_descendent",
						freeze: true,
						args: {
						
							"current_bom": frm.doc.old_reference_bom,
							"new_bom": frm.doc.name
						
						}
					});
				})

			}
			
			cur_frm.add_custom_button(__('Update References'),function(){
				if (frm.doc.name && frm.doc.old_reference_bom) {
					frappe.call({
						method: "instrument.instrument.doctype.mapped_bom.mapped_bom.enqueue_replace_bom",
						freeze: true,
						args: {
							args: {
								"current_bom": frm.doc.old_reference_bom,
								"new_bom": frm.doc.name
							}
						}
					});
				}else{
					frappe.msgprint("Please Enter Old Reference BOM ")
				}	
				
			})
		}
		if(frm.doc.item){
			frappe.call({
				method : "instrument.instrument.doctype.mapped_bom.mapped_bom.get_mapped_bom_query",
					args:{
						item_code : frm.doc.item
					},
					callback:function(r){
						if(r.message){
							cur_frm.fields_dict['old_reference_bom'].get_query = function(doc, cdt, cdn) {
								return {
									filters: [
										['Mapped BOM','name', 'in', r.message],
									]
								}
						    }
												
						}
					}
				})
		}
		if(frm.doc.item){
			if(!frm.doc.old_reference_bom && frm.doc.__islocal){
				frappe.call({
					method : "instrument.instrument.doctype.mapped_bom.mapped_bom.get_default_bom",
					args:{
						item_code : frm.doc.item
					},
					callback:function(r){
						if(r.message){
							if(r.message[1] == 'No'){
								frm.set_value("old_reference_bom",r.message[0]);
							}else{
								frm.set_value("old_reference_bom",r.message[0]);
							}
							
						}
					}
				})
			}
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

	},
	item:function(frm){
		if(frm.doc.item){
			if(!frm.doc.old_reference_bom && frm.doc.__islocal){
				frappe.call({
					method : "instrument.instrument.doctype.mapped_bom.mapped_bom.get_default_bom",
					args:{
						item_code : frm.doc.item
					},
					callback:function(r){
						if(r.message){
							if(r.message[1] == 'No'){
								frm.set_value("old_reference_bom",r.message[0]);
							}else{
								frm.set_value("old_reference_bom",r.message[0]);
							}
							
						}
					}
				})
			}
			frappe.call({
				method : "instrument.instrument.doctype.mapped_bom.mapped_bom.get_mapped_bom_query",
					args:{
						item_code : frm.doc.item
					},
					callback:function(r){
						if(r.message){
							cur_frm.fields_dict['old_reference_bom'].get_query = function(doc, cdt, cdn) {
								return {
									filters: [
										['Mapped BOM','name', 'in', r.message],
									]
								}
						    }
												
						}
					}
				})
		}
	},
	onload:function(frm){
		var query = window.location.href
		var index = query.indexOf("=")
		var string_data= query.substring(index+1)
		var data1 = JSON.parse(decodeURIComponent(string_data));
		console.log("-----------------data",data1)
		if(data1){
			frappe.call({
				method : "instrument.instrument.custom_instrument.bom.bom.duplicate_bom",
				args : {
					doc : data1.doc
				},
				callback:function(r){
					if(r.message){
						var data = r.message
						frm.doc.items = ''
						frm.set_value('allow_alternative_item',data.allow_alternative_item)
						frm.set_value('rm_cost_as_per',data.rm_cost_as_per)
						frm.set_value('inspection_required',data.inspection_required)
						frm.set_value('plc_conversion_rate',data.plc_conversion_rate)
						frm.set_value('conversion_rate',data.conversion_rate)
						frm.set_value('price_list_currency',data.price_list_currency)
						frm.set_value('project',data.project)
						frm.set_value('quantity',data.quantity)
						frm.set_value('quality_inspection_template',data.quality_inspection_template)
						if(data.items){
							$.each(data.items,function(idx,item_row){
								var row = frappe.model.add_child(frm.doc, "Mapped BOM Item", "items");
								frappe.model.set_value(row.doctype, row.name, 'item_code', item_row['item_code']);
								frappe.model.set_value(row.doctype, row.name, 'item_name', item_row['item_name']);
								frappe.model.set_value(row.doctype, row.name, 'stock_uom', item_row['stock_uom']);
								frappe.model.set_value(row.doctype, row.name, 'uom', item_row['uom']);
								frappe.model.set_value(row.doctype, row.name, 'qty', item_row['qty']);
								frappe.model.set_value(row.doctype, row.name, 'base_rate', item_row['base_rate']);
								frappe.model.set_value(row.doctype, row.name, 'rate', item_row['rate']);
								frappe.model.set_value(row.doctype, row.name, 'conversion_factor', item_row['conversion_factor']);
							})
							refresh_field('items')
						}
						if(data.operations){
							$.each(data.operations,function(idx,item_row){
								var row = frappe.model.add_child(frm.doc, "BOM Operation", "operations");
								frappe.model.set_value(row.doctype, row.name, 'operation', item_row['operation']);
								frappe.model.set_value(row.doctype, row.name, 'workstation', item_row['workstation']);
								frappe.model.set_value(row.doctype, row.name, 'time_in_mins', item_row['time_in_mins']);
								frappe.model.set_value(row.doctype, row.name, 'hour_rate', item_row['hour_rate']);
								frappe.model.set_value(row.doctype, row.name, 'batch_size', item_row['batch_size']);
								frappe.model.set_value(row.doctype, row.name, 'set_cost_based_on_bom_qty', item_row['set_cost_based_on_bom_qty']);
							})
							refresh_field('operations')
						}
						if(data.scrap_data){
							$.each(data.scrap_data,function(idx,item_row){
								var row = frappe.model.add_child(frm.doc, "BOM Scrap Item", "scrap_items");
								frappe.model.set_value(row.doctype, row.name, 'item_code', item_row['item_code']);
								frappe.model.set_value(row.doctype, row.name, 'item_name', item_row['item_name']);
								frappe.model.set_value(row.doctype, row.name, 'is_process_loss', item_row['is_process_loss']);
								frappe.model.set_value(row.doctype, row.name, 'stock_qty', item_row['stock_qty']);
								frappe.model.set_value(row.doctype, row.name, 'stock_uom', item_row['stock_uom']);
								frappe.model.set_value(row.doctype, row.name, 'rate', item_row['rate']);
							})
							refresh_field('scrap_items')
						}
					}
				}
			})
		}
			
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
		else{
			frappe.model.set_value(row.doctype, row.name, 'mapped_bom','')
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