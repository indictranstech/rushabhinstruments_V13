frappe.ui.form.on("Stock Entry", {
	refresh:function(frm){
		// if(frm.doc.stock_entry_type == 'Material Transfer' || frm.doc.stock_entry_type == 'Material Receipt'){
		// 	frm.set_value("apply_putaway_rule",1)
		// }
		if(frm.doc.stock_entry_type =="Manufacture"){
			frm.set_value("to_warehouse",'')
			if(frm.doc.work_order){
				frappe.call({
					"method":"instrument.instrument.custom_instrument.stock_entry.stock_entry.get_target_warehouse",
					"args":{
						work_order : frm.doc.work_order

					},
					callback:function(r){
						if(r.message){
							cur_frm.fields_dict['to_warehouse'].get_query = function(doc, cdt, cdn) {
								return {
									filters: [
										['Warehouse','name', 'in', r.message]
									]
								}
				    		}
						}
					}

				})

			}
			
			//Filter Accepted warehouse
			frm.set_query("t_warehouse", "items", function(doc, cdt, cdn) {
				const row = locals[cdt][cdn];
				return {
					query: "instrument.instrument.custom_instrument.stock_entry.stock_entry.get_warehouse_for_query",
					filters:{ 'parent': row.item_code }
				}
			});
		}
		if (!frm.doc.__islocal) {
			cur_frm.add_custom_button(__('Print Label'),function(){
				var dialog = new frappe.ui.Dialog({
					title: __('Stock Traveler Details'),
					keep_open: true,
					fields: [
					{
						"label": "Enter No of Copies",
						"fieldname": "no_of_copies",
						"fieldtype": "Data",
						"reqd": 1
					},
					{
						"label": "Printer Name",
						"fieldname": "printer_name",
						"fieldtype": "Link",
						"options":"Printer",
						"reqd": 1
					}
					],
					onhide: () => {
					}
					});
					dialog.set_primary_action(__('Submit'), () => {
						create_label_print(frm,dialog);
						dialog.hide()
					});
					dialog.show();
			})
		}

	},
	onload:function(frm){
		var query = window.location.href
		var index = query.indexOf("=")
		var string_data= query.substring(index+1)
		var data = JSON.parse(decodeURIComponent(string_data));
		// if(data.purpose=="Material Transfer For Manufacture"){
		// 	frm.set_value("stock_entry_type",data.type);
		// 	frm.set_value("work_order",data.work_order)
		// 	frm.set_value("work_order_pick_list",data.work_order_pick_list)

		// }
		// if(frm.doc.__islocal && frm.doc.work_order_pick_list){
		// 	frappe.call({
		// 		method :"instrument.instrument.custom_instrument.stock_entry.stock_entry.get_items_from_pick_list",
		// 		args : {
		// 			pick_list : frm.doc.work_order_pick_list,
		// 			work_order : frm.doc.work_order
		// 		},
		// 		callback:function(r){
		// 			if(r.message){
		// 				frm.set_value('fg_completed_qty',r.message[1])
		// 				frm.set_value('posting_date', frappe.datetime.get_today())
		// 				frm.set_value('posting_time',frappe.datetime.now_time())
		// 				frm.doc.items = ''
		// 				$.each(r.message[0], function(idx, item_row){
		// 					if(item_row['s_warehouse']){
		// 						var row = frappe.model.add_child(frm.doc, "Stock Entry Detail", "items");
		// 						frappe.model.set_value(row.doctype, row.name, 'item_code', item_row['item_code']);
		// 						frappe.model.set_value(row.doctype,row.name,'item_name',item_row['item_name']);
		// 						frappe.model.set_value(row.doctype, row.name, 'qty', item_row['picked_qty']);
		// 						frappe.model.set_value(row.doctype, row.name, 'uom', item_row['stock_uom']);
		// 						frappe.model.set_value(row.doctype, row.name, 'stock_uom', item_row['stock_uom']);
		// 						frappe.model.set_value(row.doctype, row.name, 'conversion_factor', 1);
		// 						frappe.model.set_value(row.doctype, row.name, 's_warehouse',item_row['s_warehouse']);
		// 						frappe.model.set_value(row.doctype, row.name, 'engineering_revision',item_row['engineering_revision']);
		// 						frappe.model.set_value(row.doctype, row.name, 'batch_no',item_row['batch_no']);
		// 					}else{
		// 						var row = frappe.model.add_child(frm.doc, "Stock Entry Detail", "items");
		// 						frappe.model.set_value(row.doctype, row.name, 'item_code', item_row['item_code']);
		// 						frappe.model.set_value(row.doctype,row.name,'item_name',item_row['item_name']);
		// 						frappe.model.set_value(row.doctype, row.name, 'qty', item_row['picked_qty']);
		// 						frappe.model.set_value(row.doctype, row.name, 'uom', item_row['stock_uom']);
		// 						frappe.model.set_value(row.doctype, row.name, 'stock_uom', item_row['stock_uom']);
		// 						frappe.model.set_value(row.doctype, row.name, 'conversion_factor', 1);
		// 						frappe.model.set_value(row.doctype, row.name, 't_warehouse',item_row['t_warehouse']);
		// 						frappe.model.set_value(row.doctype, row.name, 'engineering_revision',item_row['engineering_revision']);
		// 					}
		// 				});
		// 			}
		// 		}
		// 	})
		// }
	},

	on_submit: function(frm){
		if (frm.doc.consolidated_pick_list){
			history.back()
		}
		// window.open(window.history.previous.href, "_self");
	}
})
var create_label_print = function(frm,dialog){
	frappe.call({
		method: 'instrument.instrument.custom_instrument.stock_entry.stock_entry.print_label',
		// async: false,
		args: {
            "data": dialog.get_values(),
            "doc": frm.doc
        },
		callback: (r) => {
			if(r.message)
			{
				frappe.msgprint("Stock Entry Traveler Created. You can open it through" + r.message)

			}
		}
	});
};

