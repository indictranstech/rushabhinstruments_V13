// Copyright (c) 2021, instrument and contributors
// For license information, please see license.txt

frappe.ui.form.on('BOM Creation Tool', {
	attribute_table_on_form_rendered:function(frm, cdt, cdn){
		// hide delete, insert above and insert below fields inside Attribute  child table
		frm.fields_dict['attribute_table'].grid.wrapper.find('.grid-delete-row').hide();
		frm.fields_dict['attribute_table'].grid.wrapper.find('.grid-insert-row-below').hide();
		frm.fields_dict['attribute_table'].grid.wrapper.find('.grid-insert-row').hide();
	},
	item_assignment_table_for_mapped_item_on_form_rendered:function(frm, cdt, cdn){
		// hide delete, insert above and insert below fields inside Attribute  child table
		frm.fields_dict['item_assignment_table_for_mapped_item'].grid.wrapper.find('.grid-delete-row').hide();
		frm.fields_dict['item_assignment_table_for_mapped_item'].grid.wrapper.find('.grid-insert-row-below').hide();
		frm.fields_dict['item_assignment_table_for_mapped_item'].grid.wrapper.find('.grid-insert-row').hide();
	},
	refresh: function(frm) {
		if(frm.doc.docstatus==1){
			frm.set_df_property('review_item_mappings','hidden',1)
		}
		frm.fields_dict['attribute_table'].grid.wrapper.find('.grid-insert-row').hide();
		frm.fields_dict['attribute_table'].grid.wrapper.find('.grid-insert-row-below').hide();
		frm.fields_dict['attribute_table'].grid.wrapper.find('.grid-add-row').hide();

		frm.fields_dict['item_assignment_table_for_mapped_item'].grid.wrapper.find('.grid-insert-row').hide();
		frm.fields_dict['item_assignment_table_for_mapped_item'].grid.wrapper.find('.grid-insert-row-below').hide();
		frm.fields_dict['item_assignment_table_for_mapped_item'].grid.wrapper.find('.grid-add-row').hide();

		// Filter Items
		frm.set_query("value", "attribute_table", function(doc, cdt, cdn) {
			const row = locals[cdt][cdn];
			return {
				query: "instrument.instrument.doctype.bom_creation_tool.bom_creation_tool.get_attribute_value",
				filters:{ 'attribute': row.attribute }
			}
		});
		// Filter Items
		frm.set_query("value", "item_assignment_table_for_mapped_item", function(doc, cdt, cdn) {
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
		frm.set_query("standard_item_code", "review_item_mapping", function(doc, cdt, cdn) {
			const row = locals[cdt][cdn];
			return {
				query: "instrument.instrument.doctype.bom_creation_tool.bom_creation_tool.get_standard_item_code",
				filters:{ 'mapped_item': row.mapped_item }
			}
		});
		cur_frm.fields_dict['mapped_item'].get_query = function(doc, cdt, cdn) {
			return {
				filters: [
					['Item','is_map_item', '=', 1],
				]
			}
	    }
	    cur_frm.fields_dict['item_mapping'].get_query = function(doc, cdt, cdn) {
			return {
				filters: [
					['Item Mapping','mapped_item', '=', frm.doc.mapped_item],
				]
			}
	    }
	    frm.set_query("standard_item_code", function() {
			return {
				query: "instrument.instrument.doctype.bom_creation_tool.bom_creation_tool.get_standard_item_code",
				filters : {
					'mapped_item':frm.doc.mapped_item
				}
			};
		});

	  //   cur_frm.fields_dict['standard_item_code'].get_query = function(doc, cdt, cdn) {
			// return {
			// 	filters: [
			// 		['Item','is_map_item', '=', 0],
			// 	]
			// }
	  //   }

	    cur_frm.fields_dict['standard_bom'].get_query = function(doc, cdt, cdn) {
			return {
				filters: [
					['BOM','item', '=', frm.doc.standard_item_code],
				]
			}
	    }
		if(frm.doc.docstatus==0 &&  !frm.doc.__islocal){
			cur_frm.add_custom_button(__('Copy Attribute Values'),function(){
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
		if(frm.doc.attribute_table == ''){
			frm.trigger('mapped_bom')
			frm.save()
		}
		// if(frm.doc.__islocal){
		// 	// Fetch all the attributes for mapped item
		// 	if(frm.doc.mapped_bom){
		// 		frappe.call({
		// 			"method":"instrument.instrument.doctype.bom_creation_tool.bom_creation_tool.get_map_item_attributes",
		// 			"args":{
		// 				mapped_bom : frm.doc.mapped_bom
		// 			},
		// 			callback:function(r){
		// 				if(r.message){
		// 					if(r.message[1]==true){
		// 						$.each(r.message[0], function(idx, item_row){
		// 							var row = frappe.model.add_child(frm.doc, "BOM Creation Attribute Table", "attribute_table");
		// 							frappe.model.set_value(row.doctype, row.name, 'mapped_bom', item_row['mapped_bom']);
		// 							frappe.model.set_value(row.doctype, row.name, 'mapped_item', item_row['mapped_item']);
		// 							frappe.model.set_value(row.doctype,row.name,'attribute',item_row['attribute']);
		// 							frappe.model.set_value(row.doctype,row.name,'value',item_row['value']);
		// 						})

		// 					}else{
		// 						$.each(r.message[0], function(idx, item_row){
		// 							if(item_row['attribute_list'].length == 1){
		// 								var row = frappe.model.add_child(frm.doc, "BOM Creation Attribute Table", "attribute_table");
		// 								frappe.model.set_value(row.doctype, row.name, 'mapped_bom', item_row['parent']);
		// 								frappe.model.set_value(row.doctype, row.name, 'mapped_item', item_row['item_code']);
		// 								frappe.model.set_value(row.doctype,row.name,'attribute',item_row['attribute_list'][0]["attribute"]);
		// 							}else{
		// 								$.each(item_row['attribute_list'], function(idx, col){
		// 									var row = frappe.model.add_child(frm.doc, "BOM Creation Attribute Table", "attribute_table");
		// 									frappe.model.set_value(row.doctype, row.name, 'mapped_bom', item_row['parent']);
		// 									frappe.model.set_value(row.doctype, row.name, 'mapped_item', item_row['item_code']);
		// 									frappe.model.set_value(row.doctype,row.name,'attribute',col["attribute"]);

		// 								})
		// 							}
		// 						});
		// 					}
							
		// 					refresh_field('attribute_table')
		// 				}
		// 			}
		// 		})
		// }
		// }
	},
	standard_item_code:function(frm){
		frappe.call({
			"method":"instrument.instrument.doctype.bom_creation_tool.bom_creation_tool.check_recent_version_of_BCT",
			"args":{
				standard_item_code : frm.doc.standard_item_code
			},
			callback:function(r){
				if(r.message){
					frappe.msgprint('Item Mapping' + ' ' + frm.doc.standard_item_code +' '+ 'Used In ' + r.message)

				}
			}
		})
		frm.trigger('mapped_bom')

	},
	mapped_bom:function(frm){
		// if(frm.doc.__islocal){
			if(frm.doc.docstatus == 0){
				// Fetch all the attributes for mapped item
				if(frm.doc.mapped_bom && frm.doc.mapped_item && frm.doc.standard_item_code){
					// frm.doc.item_assignment_table_for_mapped_item = ''
					frm.doc.attribute_table = ''
					// frm.set_df_property('item_assignment_table_for_mapped_item','reqd',1)
					// frappe.call({
					// 	"method":"instrument.instrument.doctype.bom_creation_tool.bom_creation_tool.get_map_item_attributes_for_mapped_item",
					// 	"args":{
					// 		mapped_bom : frm.doc.mapped_bom
					// 	},
					// 	callback:function(r){
					// 		if(r.message){
					// 			$.each(r.message[0], function(idx, item_row){
								
					// 				frm.set_value('mapped_item',item_row['mapped_item'])
					// 				var row = frappe.model.add_child(frm.doc, "Item Assignment Table For Mapped Item", "item_assignment_table_for_mapped_item");
					// 				frappe.model.set_value(row.doctype, row.name, 'mapped_item', item_row['mapped_item']);
					// 				frappe.model.set_value(row.doctype,row.name,'attribute',item_row['attribute']);
					// 			})
					// 			refresh_field('item_assignment_table_for_mapped_item')
					// 		}

					// 	}
					// })
					
					frappe.call({
						"method":"instrument.instrument.doctype.bom_creation_tool.bom_creation_tool.get_map_item_attributes",
						"args":{
							mapped_bom : frm.doc.mapped_bom,
							mapped_item : frm.doc.mapped_item,
							standard_item_code : frm.doc.standard_item_code
						},
						callback:function(r){
							if(r.message){
								
								if(r.message[1]==true){
									$.each(r.message[0], function(idx, item_row){
										var row = frappe.model.add_child(frm.doc, "BOM Creation Attribute Table", "attribute_table");
										frappe.model.set_value(row.doctype, row.name, 'mapped_bom', item_row['mapped_bom']);
										frappe.model.set_value(row.doctype, row.name, 'mapped_boms', item_row['mapped_boms']);
										frappe.model.set_value(row.doctype, row.name, 'mapped_item', item_row['mapped_item']);
										frappe.model.set_value(row.doctype,row.name,'attribute',item_row['attribute']);
										frappe.model.set_value(row.doctype,row.name,'value',item_row['value']);
									})

								}else{
									$.each(r.message[0], function(idx, item_row){
										if(item_row['attribute_list'].length == 1){
											var row = frappe.model.add_child(frm.doc, "BOM Creation Attribute Table", "attribute_table");
											frappe.model.set_value(row.doctype, row.name, 'mapped_bom', item_row['parent']);
											frappe.model.set_value(row.doctype, row.name, 'mapped_boms', item_row['mapped_boms']);
											frappe.model.set_value(row.doctype, row.name, 'mapped_item', item_row['item_code']);
											frappe.model.set_value(row.doctype,row.name,'attribute',item_row['attribute_list'][0]["attribute"]);
											frappe.model.set_value(row.doctype,row.name,'value',item_row['attribute_list'][0]["value"]);
										}else{
											$.each(item_row['attribute_list'], function(idx, col){
												var row = frappe.model.add_child(frm.doc, "BOM Creation Attribute Table", "attribute_table");
												frappe.model.set_value(row.doctype, row.name, 'mapped_bom', item_row['parent']);
												frappe.model.set_value(row.doctype, row.name, 'mapped_boms', item_row['mapped_boms']);
												frappe.model.set_value(row.doctype, row.name, 'mapped_item', item_row['item_code']);
												frappe.model.set_value(row.doctype,row.name,'attribute',col["attribute"]);
												frappe.model.set_value(row.doctype,row.name,'value',col["value"]);

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
	mapped_item:function(frm){
		if(frm.doc.mapped_item){
			frappe.call({
				"method":"instrument.instrument.doctype.bom_creation_tool.bom_creation_tool.get_mapped_bom",
				"args" : {
					mapped_item : frm.doc.mapped_item
				},
				callback:function(r){
					if(r.message){
						frm.set_value("mapped_bom",r.message)
					}

				}
			})
		}

	},
	validate:function(frm){
		if(frm.doc.__islocal){
			frm.set_df_property('mapped_item','read_only',1)
			frm.set_df_property('mapped_bom','read_only',1)
			frm.set_df_property('standard_item_code','read_only',1)
			frm.set_df_property('standard_bom','read_only',1)
		// 	// Fetch all the attributes for mapped item
		// 	if(frm.doc.mapped_bom){
		// 		frappe.call({
		// 			"method":"instrument.instrument.doctype.bom_creation_tool.bom_creation_tool.get_map_item_attributes",
		// 			"args":{
		// 				mapped_bom : frm.doc.mapped_bom
		// 			},
		// 			callback:function(r){
		// 				if(r.message){
		// 					if(r.message[1]==true){
		// 						$.each(r.message[0], function(idx, item_row){
		// 							var row = frappe.model.add_child(frm.doc, "BOM Creation Attribute Table", "attribute_table");
		// 							frappe.model.set_value(row.doctype, row.name, 'mapped_bom', item_row['mapped_bom']);
		// 							frappe.model.set_value(row.doctype, row.name, 'mapped_item', item_row['mapped_item']);
		// 							frappe.model.set_value(row.doctype,row.name,'attribute',item_row['attribute']);
		// 							frappe.model.set_value(row.doctype,row.name,'value',item_row['value']);
		// 						})

		// 					}else{
		// 						$.each(r.message[0], function(idx, item_row){
		// 							if(item_row['attribute_list'].length == 1){
		// 								var row = frappe.model.add_child(frm.doc, "BOM Creation Attribute Table", "attribute_table");
		// 								frappe.model.set_value(row.doctype, row.name, 'mapped_bom', item_row['parent']);
		// 								frappe.model.set_value(row.doctype, row.name, 'mapped_item', item_row['item_code']);
		// 								frappe.model.set_value(row.doctype,row.name,'attribute',item_row['attribute_list'][0]["attribute"]);
		// 							}else{
		// 								$.each(item_row['attribute_list'], function(idx, col){
		// 									var row = frappe.model.add_child(frm.doc, "BOM Creation Attribute Table", "attribute_table");
		// 									frappe.model.set_value(row.doctype, row.name, 'mapped_bom', item_row['parent']);
		// 									frappe.model.set_value(row.doctype, row.name, 'mapped_item', item_row['item_code']);
		// 									frappe.model.set_value(row.doctype,row.name,'attribute',col["attribute"]);

		// 								})
		// 							}
		// 						});
		// 					}
							
		// 					refresh_field('attribute_table')
		// 				}
		// 			}
		// 		})
		// }
		}
		// refresh_field('review_item_mapping')

	},
	review_item_mappings:function(frm){
		return frm.call({
					doc: frm.doc,
					method: "review_item_mappings",
					freeze: true,
					callback: function(r) {
						if(r.message){
							refresh_field('review_item_mapping')
							refresh_field('difference_between_previous_and_current_review_item_mappings')

						}
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
frappe.ui.form.on('BOM Creation Attribute Table', {
	value:function(frm,cdt,cdn){
		frm.doc.review_item_mapping = ''
		frm.refresh_field("review_item_mapping")
		frm.doc.difference_between_previous_and_current_review_item_mappings = ''
		frm.refresh_field("difference_between_previous_and_current_review_item_mappings")
		var row = locals[cdt][cdn]
		if(row.value){
			if(!frm.doc.__islocal){
				$.each(frm.doc.attribute_table, function(idx, item_row){
					if(row.name != item_row['name']){
						if(row.attribute == item_row['attribute']){
							frappe.model.set_value(item_row['doctype'], item_row['name'], 'value', '');
						}
					}
				})
			}
		}

	}
})