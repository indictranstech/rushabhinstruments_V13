// Copyright (c) 2021, instrument and contributors
// For license information, please see license.txt

frappe.ui.form.on('Consolidated Pick List', {
	work_orders_on_form_rendered:function(frm, cdt, cdn){
		// hide delete, insert above and insert below fields inside Attribute  child table
		frm.fields_dict['work_orders'].grid.wrapper.find('.grid-delete-row').hide();
		frm.fields_dict['work_orders'].grid.wrapper.find('.grid-insert-row-below').hide();
		frm.fields_dict['work_orders'].grid.wrapper.find('.grid-insert-row').hide();
	},
	refresh: function(frm) {
		// if(frm.doc.docstatus==0){
		// 	cur_frm.set_df_property('create_stock_entry', 'read_only', 1);
		// }
		frm.fields_dict['work_orders'].grid.wrapper.find('.grid-insert-row').hide();
		frm.fields_dict['work_orders'].grid.wrapper.find('.grid-insert-row-below').hide();
		frm.fields_dict['work_orders'].grid.wrapper.find('.grid-add-row').hide();

		frm.set_query("work_order", "work_order_table", function(doc, cdt, cdn) {
			const row = locals[cdt][cdn];
			return {
				query: "instrument.instrument.doctype.consolidated_pick_list.consolidated_pick_list.get_work_order_for_pick_list",
				filters:{ 'purpose': frm.doc.purpose }
			}
		});
		var df = frappe.meta.get_docfield("Pick Orders","create_stock_entry", cur_frm.doc.name);
		df.read_only = 1;
		frm.set_query('production_plan', () => {
			return {
				filters: {
					'status' :'In Progress' 
				}
			};
		});
		frm.set_query('batch_no', 'work_order_pick_list_item', (frm, cdt, cdn) => {
			const row = locals[cdt][cdn];
			return {
				query: 'erpnext.controllers.queries.get_batch_no',
				filters: {
					item_code: row.item_code,
					warehouse: row.warehouse
				},
			};
		});
		frm.set_query("stock_entry", "work_orders", function(doc, cdt, cdn) {
			const row = locals[cdt][cdn];
			return {
				query: "instrument.instrument.doctype.consolidated_pick_list.consolidated_pick_list.get_se",
				filters:{ 'work_order': row.work_order}
			}
		});
		if(frm.doc.docstatus == 0 || frm.doc.docstatus == 1){
			frm.add_custom_button(__('Export Excel'), function() {
				
          		frappe.call({
					'method':"instrument.instrument.doctype.consolidated_pick_list.consolidated_pick_list.get_pick_list_details",
					'args': {doc:frm.doc},
					callback: function(r) {
						var w = window.open(
						frappe.urllib.get_full_url(
						"/api/method/instrument.instrument.doctype.consolidated_pick_list.consolidated_pick_list.download_xlsx?"));

						if(!w)
							frappe.msgprint(__("Please enable pop-ups")); return;
					}
				})			
			})
			
		}
		//Hide Button
		if(frm.doc.docstatus == 0 && frm.doc.work_orders != []){
			frm.add_custom_button(__('Create Stock Entries In Bulk'), function() {
				frappe.call({
					method : "instrument.instrument.doctype.consolidated_pick_list.consolidated_pick_list.create_stock_entries_in_bulk",
					freeze:true,
					freeze_message:"Creating Stock Entries..",
					args:{
						doc : frm.doc
					},
					callback:function(r){

					}
				})
			})
		} 
		if (frm.doc.__islocal && frm.doc.work_order) {
			frm.trigger("get_fg_work_orders")
			frm.set_value("naming_series", "WO-PICK-.YYYY.-")
			frm.set_value("planned_start_date", "")
			frm.set_value("planned_end_date", "")
			frm.set_value("expected_delivery_date", "")
		} else if (frm.doc.__islocal && frm.doc.sales_order){
			frm.trigger("get_fg_sales_orders")
			frm.set_value("naming_series", "SO-PICK-.YYYY.-")
			frm.set_value("purpose", "Sales Order Fulfillment")			
			frm.set_value("delivery_start_date", "")
			frm.set_value("delivery_end_date", "")
			frm.set_value("customer", "")
			frm.set_value("customer_po_number", "")
		} else if (frm.doc.__islocal && frm.doc.purchase_order) {
			frm.trigger("get_fg_purchase_orders")
			frm.set_value("naming_series", "PO-PICK-.YYYY.-")
			frm.set_value("purpose", "Material Transfer for Subcontracted Goods")
			frm.set_value("start_date", "")
			frm.set_value("end_date", "")
			frm.set_value("supplier", "")
		}
	},

	// validate: function(frm) {
	// 	if (frm.doc.docstatus==1){
	// 		frm.set_value("status", "Submitted")
	// 	}
	// },

	purpose: (frm) => {
		if ((frm.doc.purpose == 'Material Transfer for Manufacture') || (frm.doc.purpose == 'Manufacture')){
			frm.set_value("naming_series", "WO-PICK-.YYYY.-")
		} else if (frm.doc.purpose == 'Sales Order Fulfillment') {
			frm.set_value("naming_series", "SO-PICK-.YYYY.-")
		} else {
			frm.set_value("naming_series", "PO-PICK-.YYYY.-")
		}
	},

	get_work_orders: (frm) => {
		frm.doc.work_orders = ''
		frm.dirty();
		return new Promise(function(resolve, reject) {
					frappe.confirm(
						'Do you want to consider current stock of subassembly items?',
				function(){
					frm.doc.consider_current_stock = 1
					var negative = 'frappe.validated = true';
					resolve(negative);
					frappe.call({
						method: "get_sub_assembly_items",
						freeze: true,
						doc: frm.doc,
						callback: function() {
							refresh_field("work_orders");
						}
					});	
				},function(){
					frm.doc.consider_current_stock = 0
					reject();
					frappe.call({
						method: "get_sub_assembly_items",
						freeze: true,
						doc: frm.doc,
						callback: function() {
							refresh_field("work_orders");
						}
					});
			});
		})
	},
	get_fg_work_orders:(frm) =>{
		// frm.doc.work_order_table = ''
		frm.dirty();
		frm.call({
			method: "get_fg_work_orders",
			doc: frm.doc,
			callback: function(r, rt) {
				refresh_field("work_order_table");
				frm.set_value("work_order", "")
			}
		})

	},
	remove_work_orders:(frm)=>{
		
		frappe.call({
			method : "remove_work_orders",
			doc: frm.doc,
			callback: function(r, rt) {
				// refresh_field("work_order_table");
				// frm.set_value("work_order", "")
			}
		})
	},

	get_fg_sales_orders:(frm) =>{
		frm.doc.sales_order_table = ''
		frm.dirty();
		frm.call({
			method: "get_fg_sales_orders",
			doc: frm.doc,
			callback: function(r, rt) {
				refresh_field("sales_order_table");
				// refresh_field("pick_list_sales_order_table");
				// frm.set_value("work_order", "")
			}
		})
	},

	get_sales_orders:(frm) =>{
		frm.doc.pick_list_sales_order_table = ''
		frm.dirty();
		frm.call({
			method: "get_sales_orders",
			doc: frm.doc,
			callback: function(r, rt) {
				refresh_field("pick_list_sales_order_table");
				// frm.set_value("work_order", "")
			}
		})
	},

	get_purchase_orders:(frm) =>{
		frm.doc.pick_list_purchase_order_table = ''
		frm.dirty();
		frm.call({
			method: "get_purchase_orders",
			doc: frm.doc,
			callback: function(r, rt) {
				refresh_field("pick_list_purchase_order_table");
				// frm.set_value("work_order", "")
			}
		})
	},
		// if(frm.doc.production_plan){
		// 	frappe.call({
		// 		method : 'instrument.instrument.doctype.work_order_pick_list.work_order_pick_list.get_work_orders',
		// 		args : {
		// 			production_plan : frm.doc.production_plan

		// 		},
		// 		callback:function(r){
		// 			if(r.message){
		// 				$.each(r.message, function(idx, item_row){
		// 					var row = frappe.model.add_child(frm.doc, "Pick Orders", "work_orders");
		// 					frappe.model.set_value(row.doctype, row.name, 'work_order', item_row['name']);
		// 					frappe.model.set_value(row.doctype, row.name, 'total_qty_to_of_finished_goods_on_work_order', item_row['qty']);
		// 					frappe.model.set_value(row.doctype, row.name, 'qty_of_finished_goods_already_completed', item_row['produced_qty']);
		// 					frappe.model.set_value(row.doctype,row.name,'qty_of_finished_goods',item_row['pending_qty']);
		// 				});
		// 				frm.save()
		// 			}
		// 		}
		// 	})
		// }else{
		// 	frappe.msgprint("Please Select Production Plan")
		// }
	// },
	get_items: (frm) => {
		frm.doc.work_order_pick_list_item = ''
		frm.dirty();
		frm.call({
			method: "get_work_order_items",
			doc: frm.doc,
			freeze: true,
			freeze_message: __("Fetching Work Order Items..."),
			callback: function(r) {
				if (r.message) {
					cur_frm.clear_table("work_order_pick_list_item");
					$.each(r.message, function(idx, item_row){
						var row = frappe.model.add_child(frm.doc, "Work Order Pick List Item", "work_order_pick_list_item");
						row.item_code = item_row.item_code
						row.uom = item_row.uom
						row.uom_conversion_factor = item_row.uom_conversion_factor
						row.stock_uom = item_row.stock_uom
						row.serial_nos = item_row.serial_nos					
						row.warehouse = item_row.warehouse
						row.required_qty = item_row.required_qty
						row.work_order = item_row.work_order
						row.stock_qty=item_row.stock_qty
						row.picked_qty=item_row.picked_qty
						row.batch_no=item_row.batch_no
						row.wip_stock = item_row.wip_stock
						row.actual_required_qty = item_row.actual_required_qty
					});
					frm.save()
					refresh_field("work_order_pick_list_item");
				}
			}
		})
	},

	get_so_items: (frm) => {
		frm.doc.sales_order_pick_list_item = ''
		frm.dirty();
		frm.call({
			method: "get_sales_order_items",
			doc: frm.doc,
			callback: function(r) {
				if (r.message) {
					cur_frm.clear_table("sales_order_pick_list_item");
					$.each(r.message, function(idx, item_row){
						var row = frappe.model.add_child(frm.doc, "Sales Order Pick List Item", "sales_order_pick_list_item");
						row.item_code = item_row.item_code
						row.uom = item_row.uom
						row.uom_conversion_factor = item_row.uom_conversion_factor
						row.stock_uom = item_row.stock_uom
						row.serial_nos = item_row.serial_nos					
						row.warehouse = item_row.warehouse
						row.required_qty = item_row.required_qty
						row.sales_order = item_row.sales_order
						row.stock_qty=item_row.stock_qty
						row.picked_qty=item_row.picked_qty
						row.batch_no=item_row.batch_no
						row.sales_order_item=item_row.sales_order_item
					});
					frm.save()
					refresh_field("sales_order_pick_list_item");
				}
			}
		})
	},


	onload:function(frm){
		var query = window.location.href
		var index = query.indexOf("=")
		var string_data= query.substring(index+1)
		var data = JSON.parse(decodeURIComponent(string_data));
		if(data.work_order_data){
			$.each(data.work_order_data, function(idx, item_row){
				var row = frappe.model.add_child(frm.doc, "Pick List FG Work Orders", "work_order_table");
				frappe.model.set_value(row.doctype, row.name, 'work_order', item_row['name']);
				if(item_row['name']){
					frappe.call({
						method : "instrument.instrument.doctype.consolidated_pick_list.consolidated_pick_list.get_work_order_data",
						args :{
							work_order : item_row['name']
						},
						callback:function(r){
							if(r.message){
								$.each(r.message, function(idx, item){
									// var row = frappe.model.add_child(frm.doc, "Pick Orders", "work_orders");
									// frappe.model.set_value(row.doctype, row.name, 'work_order', item_row['name']);
									frappe.model.set_value(row.doctype, row.name, 'total_qty_to_of_finished_goods_on_work_order', item['qty']);
									frappe.model.set_value(row.doctype, row.name, 'qty_of_finished_goods_already_completed', item['produced_qty']);
									frappe.model.set_value(row.doctype, row.name, 'qty_of_finished_goods_to_pull', item['qty_will_be_produced']);
									frappe.model.set_value(row.doctype,row.name,'qty_of_finished_goods',item['pending_qty']);
								});
							// frm.save()
							}
						}
					})
				}
			});
		}
	},
	get_fg_purchase_orders:(frm) =>{
		frm.doc.purchase_order_table = ''
		// frm.doc.pick_list_purchase_order_table = ''
		frm.dirty();
		frm.call({
			method: "get_fg_purchase_orders",
			doc: frm.doc,
			callback: function(r, rt) {
				refresh_field("purchase_order_table");
				// refresh_field("pick_list_purchase_order_table");
				// frm.set_value("work_order", "")
			}
		})

	},


	get_po_items: (frm) => {
		frm.doc.purchase_order_pick_list_item = ''
		frm.dirty();
		frm.call({
			method: "get_purchase_order_items",
			doc: frm.doc,
			callback: function(r) {
				if (r.message) {
					cur_frm.clear_table("purchase_order_pick_list_item");
					$.each(r.message, function(idx, item_row){
						var row = frappe.model.add_child(frm.doc, "Purchase Order Pick List Item", "purchase_order_pick_list_item");
						row.main_item = item_row.main_item
						row.item_code = item_row.item_code
						row.uom = item_row.uom
						row.uom_conversion_factor = item_row.uom_conversion_factor
						row.stock_uom = item_row.stock_uom
						row.serial_nos = item_row.serial_nos					
						row.warehouse = item_row.warehouse
						row.required_qty = item_row.required_qty
						row.purchase_order = item_row.purchase_order
						row.stock_qty=item_row.stock_qty
						row.picked_qty=item_row.picked_qty
						row.batch_no=item_row.batch_no
						row.serial_no = item_row.serial_no
					});
					frm.save()
					refresh_field("purchase_order_pick_list_item");
				}
			}
		})
	},

	pick_list_purchase_order_table_on_form_rendered:function(frm,cdt,cdn){
		var d = locals[cdt][cdn]
		var stock_entry = frm.open_grid_row().get_field('stock_entry').value
		if (stock_entry){
			frm.open_grid_row().set_field_property("create_stock_entry", 'hidden', 1)
		}
		frm.refresh_field('pick_list_purchase_order_table');
	},

	// work_orders_on_form_rendered:function(frm,cdt,cdn){
	// 	var d = locals[cdt][cdn]
	// 	var stock_entry = frm.open_grid_row().get_field('stock_entry').value
	// 	if (stock_entry){
	// 		frm.open_grid_row().set_field_property("create_stock_entry", 'hidden', 1)
	// 	}
	// 	frm.refresh_field('work_orders');
	// },

	pick_list_sales_order_table_on_form_rendered:function(frm,cdt,cdn){
		var d = locals[cdt][cdn]
		var stock_entry = frm.open_grid_row().get_field('delivery_note').value
		if (stock_entry){
			frm.open_grid_row().set_field_property("select_item_for_delivery", 'hidden', 1)
		}
		frm.refresh_field('pick_list_sales_order_table');
	},

	create_delivery_note:function(frm){
		frm.call({
			method: "new_create_dn_for_so",
			doc: frm.doc,
			callback:function(r){
				if(r.message){
					var data = r.message
					// frappe.model.set_value(row.doctype, row.name, 'delivery_note', data.name);
					// frappe.model.set_value(row.doctype, row.name, 'delivery_note_status', data.status);
					// frm.save()
					frm.refresh_field("pick_list_sales_order_table");
					var old_link = window.location.href
					var split_data = old_link.split("/app")
					var link =  split_data[0]+"/app/delivery-note/"+data.name
					window.open(link, "_self");
				}
			}
		})
	},

	work_orders_on_form_rendered:function(frm,cdt,cdn){
		var row = locals[cdt][cdn]
		var stock_entry_status = frm.open_grid_row().get_field('stock_entry_status').value
		if(stock_entry_status=="Not Created"){
			frm.open_grid_row().set_field_property("create_stock_entry", 'hidden', false)
		} else {
			frm.open_grid_row().set_field_property("create_stock_entry", 'hidden', true)
		}
	}

});
frappe.ui.form.on('Pick Orders', {
	work_order:function(frm,cdt,cdn){
		var row = locals[cdt][cdn]
		if(row.work_order){
			frappe.call({
					method : 'instrument.instrument.doctype.consolidated_pick_list.consolidated_pick_list.get_work_order_data',
					args : {
						work_order : row.work_order

					},
					callback:function(r){
						if(r.message){
							$.each(r.message, function(idx, item_row){
								// var row = frappe.model.add_child(frm.doc, "Pick Orders", "work_orders");
								// frappe.model.set_value(row.doctype, row.name, 'work_order', item_row['name']);
								frappe.model.set_value(row.doctype, row.name, 'total_qty_to_of_finished_goods_on_work_order', item_row['qty']);
								frappe.model.set_value(row.doctype, row.name, 'qty_of_finished_goods_already_completed', item_row['produced_qty']);
								frappe.model.set_value(row.doctype, row.name, 'qty_of_finished_goods_to_pull', item_row['qty_will_be_produced']);
								frappe.model.set_value(row.doctype,row.name,'qty_of_finished_goods',item_row['pending_qty']);
							});
							// frm.save()
						}
					}
				})
		}
	},
	create_stock_entry:function(frm,cdt,cdn){
		var row = locals[cdt][cdn]
		if(row.work_order){
			frappe.call({
				"method":"instrument.instrument.doctype.consolidated_pick_list.consolidated_pick_list.check_stock_entries",
				"args" : {
					work_order : row.work_order,
					consolidated_pick_list : frm.doc.name,
					row_name: row.name
				},
				callback:function(r){
					if(r.message){
						frappe.call({
							"method":"instrument.instrument.doctype.consolidated_pick_list.consolidated_pick_list.create_stock_entry",
							"args" : {
								work_order : row.work_order,
								consolidated_pick_list : frm.doc.name,
								row_name: row.name
							},
							callback:function(r){
								if(r.message){
									frappe.model.set_value(row.doctype, row.name, 'stock_entry_status','Draft');
									frappe.model.set_value(row.doctype, row.name, 'stock_entry',r.message);
									var old_link = window.location.href
									var split_data = old_link.split("/app")
									var link =  split_data[0]+"/app/stock-entry/"+r.message
									window.open(link);
																			}

							}
						})
					}
				}
			})
			frm.save()
		}else{
			frappe.msgprint("Please pick quanity for atleast one item and submit the form")
		}
		
		// if(frm.doc.docstatus ==1){
			
		// 	if(row.work_order){
				
		// 		// frappe.set_route("Form","Stock Entry", "new stock entry");
		// 		// frappe.route_options = {"stock_entry_type": "Manufacture","work_order" :row.work_order,"work_order_pick_list":frm.doc.name}	
		// 	}
		// }
	}			
})

frappe.ui.form.on('Work Order Pick List Item', {
	picked_qty:function(frm,cdt,cdn){
		var row = locals[cdt][cdn]
		if(row.stock_qty < row.picked_qty){
			frappe.throw("You cannot pick qty more than" + row.stock_qty)
		}
		if(row.work_order && row.required_qty && row.picked_qty > 0){
			frappe.call({
				"method" : "instrument.instrument.doctype.consolidated_pick_list.consolidated_pick_list.validate_picked_qty",
				"args" : {
					work_order : row.work_order,
					required_qty : row.required_qty,
					picked_qty : row.picked_qty,
					doc_name : frm.doc.name,
					row_name : row.name,
					item_code : row.item_code
				},
				callback:function(r){
					if(r.message){
						var total_picked_qty = flt(r.message) + row.picked_qty
						if(row.picked_qty > row.required_qty || total_picked_qty >  row.required_qty ){
							var difference = flt(total_picked_qty) - flt(row.required_qty)
							frappe.msgprint('You have Picked' + ' ' + difference +' '+ 'More Qty for Item ' + row.item_code)
						}
						
					}

				}
			})	

		}
		
	}
})
frappe.ui.form.on('Pick List FG Work Orders', {
	work_order:function(frm,cdt,cdn){
		var row = locals[cdt][cdn]
		frappe.call({
			method : "instrument.instrument.doctype.consolidated_pick_list.consolidated_pick_list.get_pending_qty",
			args :{
				work_order : row.work_order,
				purpose : frm.doc.purpose
			},
			callback:function(r){
				if(r.message){
					frappe.model.set_value(row.doctype, row.name, 'pending_qty', r.message[0]['qty']);
					frappe.model.set_value(row.doctype, row.name, 'qty_can_be_pulledmanufactured', r.message[0]['qty_will_be_produced']);
				}
			}
		})
	}
})


frappe.ui.form.on('Pick List Purchase Order Table', {
	create_stock_entry:function(frm,cdt,cdn){
		var row = locals[cdt][cdn]
		frappe.call({
			method : "instrument.instrument.doctype.consolidated_pick_list.consolidated_pick_list.create_stock_entry_for_po",
			args :{
				purchase_order : row.purchase_order,
				item : row.item,
				row_name: row.name,
				name: frm.doc.name
			},
			callback:function(r){
				if(r.message){
					var data = r.message
					frappe.model.set_value(row.doctype, row.name, 'stock_entry', data.name);
					frappe.model.set_value(row.doctype, row.name, 'stock_entry_status', data.status);
					frm.save()
					// frm.submit()
					frm.refresh_field("pick_list_purchase_order_table");
					var old_link = window.location.href
					var split_data = old_link.split("/app")
					var link =  split_data[0]+"/app/stock-entry/"+data.name
					window.open(link, "_self");
				}

			}
		})
	}
})

frappe.ui.form.on('Pick List Sales Order Table', {
	create_delivery_note:function(frm,cdt,cdn){
		var row = locals[cdt][cdn]
		frappe.call({
			method : "instrument.instrument.doctype.consolidated_pick_list.consolidated_pick_list.create_dn_for_so",
			args :{
				sales_order : row.sales_order,
				item : row.item,
				row_name: row.name,
				name: frm.doc.name
			},
			callback:function(r){
				if(r.message){
					var data = r.message
					frappe.model.set_value(row.doctype, row.name, 'delivery_note', data.name);
					frappe.model.set_value(row.doctype, row.name, 'delivery_note_status', data.status);
					frm.save()
					frm.refresh_field("pick_list_sales_order_table");
					var old_link = window.location.href
					var split_data = old_link.split("/app")
					var link =  split_data[0]+"/app/delivery-note/"+data.name
					window.open(link, "_self");
				}
			}
		})
	}
})