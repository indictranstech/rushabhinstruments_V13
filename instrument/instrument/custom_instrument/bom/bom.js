frappe.ui.form.on("BOM", {
	refresh:function(frm){
		//Filter Engineering Revision
		frm.set_query("engineering_revision", "items", function(doc, cdt, cdn) {
			const row = locals[cdt][cdn];
			return {
				query: "instrument.instrument.custom_instrument.bom.bom.get_engineering_revisions_for_filter",
				filters:{ 'item_code': row.item_code }
			}
		});	
		if(!frm.doc.__islocal){
			cur_frm.add_custom_button(__('Duplicate to Mapped BOM'),function(){
				var old_link = window.location.href
				var split_data = old_link.split("/app")
				var data = {doc : frm.doc.name}
				var myJSON = JSON.stringify(data);
				var link =  split_data[0]+"/app/mapped-bom/new-mapped-bom-1?data="+myJSON
				window.open(link);
				// frappe.call({
				// 	method : "instrument.instrument.custom_instrument.bom.bom.duplicate_bom",
				// 	args : {
				// 		doc : frm.doc.name
				// 	},
				// 	callback:function(r){
				// 		if(r.message){
				// 			var old_link = window.location.href
				// 			var split_data = old_link.split("/app")
				// 			var myJSON = JSON.stringify(r.message);
				// 			var link =  split_data[0]+"/app/mapped-bom/new-mapped-bom-1?data="+myJSON
				// 			window.open(link);
										
				// 		}
				// 	}
				// })
			},__("Menu"))
		}
		if(frm.doc.item){
			frappe.call({
				method : "instrument.instrument.custom_instrument.bom.bom.get_bom_query",
					args:{
						item_code : frm.doc.item
					},
					callback:function(r){
						if(r.message){
							cur_frm.fields_dict['old_reference_bom'].get_query = function(doc, cdt, cdn) {
								return {
									filters: [
										['BOM','name', 'in', r.message],
									]
								}
						    }
												
						}
					}
				})
			if(!frm.doc.old_reference_bom && frm.doc.__islocal){
				frappe.call({
					method : "instrument.instrument.custom_instrument.bom.bom.get_default_bom",
					args:{
						item_code : frm.doc.item
					},
					callback:function(r){
						if(r.message){
							
								frm.set_value("old_reference_bom",r.message);	
						}
					}
				})
			}
		}
		if(frm.doc.docstatus==1){
			cur_frm.add_custom_button(__('Update References'),function(){
				if (frm.doc.name && frm.doc.old_reference_bom) {
					frappe.call({
						method: "erpnext.manufacturing.doctype.bom_update_tool.bom_update_tool.enqueue_replace_bom",
						freeze: true,
						args: {
							args: {
								"current_bom": frm.doc.name,
								"new_bom": frm.doc.old_reference_bom
							}
						}
					});
				}else{
					frappe.msgprint("Please Enter Old Reference BOM")
				}
			},__("Menu"))

		}
		
	},
	item:function(frm){
		if(frm.doc.item){
			frappe.call({
				method : "instrument.instrument.custom_instrument.bom.bom.get_bom_query",
					args:{
						item_code : frm.doc.item
					},
					callback:function(r){
						if(r.message){
							cur_frm.fields_dict['old_reference_bom'].get_query = function(doc, cdt, cdn) {
								return {
									filters: [
										['BOM','name', 'in', r.message],
									]
								}
						    }
												
						}
					}
				})
			if(!frm.doc.old_reference_bom && frm.doc.__islocal){
				frappe.call({
					method : "instrument.instrument.custom_instrument.bom.bom.get_default_bom",
					args:{
						item_code : frm.doc.item
					},
					callback:function(r){
						if(r.message){
							
								frm.set_value("old_reference_bom",r.message);	
						}
					}
				})
			}
		}
	}
});
frappe.ui.form.on('BOM Item', {
    item_code: function(frm, cdt, cdn) {
		var row = locals[cdt][cdn]
		if(row.item_code){
			frappe.call({
				"method" :"instrument.instrument.custom_instrument.bom.bom.get_engineering_revision",
				"args" : {
					item_code : row.item_code,
				},
				callback:function(r){
					if(r.message){
						frappe.model.set_value(row.doctype, row.name, 'engineering_revision', r.message)
					}
				}
			})
		}
    }
});