// Copyright (c) 2021, instrument and contributors
// For license information, please see license.txt

frappe.ui.form.on('Work Order Pick List', {
	refresh: function(frm) {
		// if(frm.doc.docstatus==0){
		// 	cur_frm.set_df_property('create_stock_entry', 'read_only', 1);
		// }
		var df = frappe.meta.get_docfield("Pick Orders","create_stock_entry", cur_frm.doc.name);
		df.read_only = 1;
		frm.set_query('production_plan', () => {
			return {
				filters: {
					'status' :'In Process' 
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
		if(frm.doc.docstatus == 0 || frm.doc.docstatus == 1){
			frm.add_custom_button(__('Export Excel'), function() {
				
          		frappe.call({
					'method':"instrument.instrument.doctype.work_order_pick_list.work_order_pick_list.get_pick_list_details",
					'args': {doc:frm.doc},
					callback: function(r) {
						var w = window.open(
						frappe.urllib.get_full_url(
						"/api/method/instrument.instrument.doctype.work_order_pick_list.work_order_pick_list.download_xlsx?"));

						if(!w)
							frappe.msgprint(__("Please enable pop-ups")); return;
					}
				})			
			})
		}

	},
	get_work_orders: (frm) => {
		frm.doc.work_orders = ''
		if(frm.doc.production_plan){
			frappe.call({
				method : 'instrument.instrument.doctype.work_order_pick_list.work_order_pick_list.get_work_orders',
				args : {
					production_plan : frm.doc.production_plan

				},
				callback:function(r){
					if(r.message){
						$.each(r.message, function(idx, item_row){
							var row = frappe.model.add_child(frm.doc, "Pick Orders", "work_orders");
							frappe.model.set_value(row.doctype, row.name, 'work_order', item_row['name']);
							frappe.model.set_value(row.doctype, row.name, 'total_qty_to_of_finished_goods_on_work_order', item_row['qty']);
							frappe.model.set_value(row.doctype, row.name, 'qty_of_finished_goods_already_completed', item_row['produced_qty']);
							frappe.model.set_value(row.doctype,row.name,'qty_of_finished_goods',item_row['pending_qty']);
						});
						frm.save()
					}
				}
			})
		}else{
			frappe.msgprint("Please Select Production Plan")
		}
	},
	get_items: (frm) => {
		frm.doc.work_order_pick_list_item = ''
		frm.call({
			method: "get_work_order_items",
			doc: frm.doc,
			callback: function(r, rt) {
				frm.save()
				frm.reload_doc();
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
				var row = frappe.model.add_child(frm.doc, "Pick Orders", "work_orders");
				frappe.model.set_value(row.doctype, row.name, 'work_order', item_row['name']);
				if(item_row['name']){
					frappe.call({
						method : "instrument.instrument.doctype.work_order_pick_list.work_order_pick_list.get_work_order_data",
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
	}
});
frappe.ui.form.on('Pick Orders', {
	work_order:function(frm,cdt,cdn){
		var row = locals[cdt][cdn]
		if(row.work_order){
			frappe.call({
					method : 'instrument.instrument.doctype.work_order_pick_list.work_order_pick_list.get_work_order_data',
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
		if(row.work_order && frm.doc.docstatus ==1){
			frappe.call({
				"method":"instrument.instrument.doctype.work_order_pick_list.work_order_pick_list.check_stock_entries",
				"args" : {
					work_order : row.work_order,
					work_order_pick_list : frm.doc.name
				},
				callback:function(r){
					if(r.message){
						frappe.call({
							"method":"instrument.instrument.doctype.work_order_pick_list.work_order_pick_list.create_stock_entry",
							"args" : {
								work_order : row.work_order,
								work_order_pick_list : frm.doc.name
							},
							callback:function(r){
								if(r.message){
									var old_link = window.location.href
									var split_data = old_link.split("/app")
									var link =  split_data[0]+"/app#stock-entry/"+r.message
									window.open(link);
																			}

							}
						})
					}
				}
			})
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
				"method" : "instrument.instrument.doctype.work_order_pick_list.work_order_pick_list.validate_picked_qty",
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
