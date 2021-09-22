frappe.ui.form.on('Work Order', {
	refresh: function(frm) {
		//Filter Engineering Revision
		frm.set_query("engineering_revision", "required_items", function(doc, cdt, cdn) {
			const row = locals[cdt][cdn];
			return {
				query: "instrument.instrument.custom_instrument.work_order.work_order.get_engineering_revisions_for_filter",
				filters:{ 'item_code': row.item_code }
			}
		});	
		cur_frm.fields_dict['engineering_revision'].get_query = function(doc, cdt, cdn) {
		return {
			filters: [
				['Engineering Revision','item_code', '=', frm.doc.production_item]
			]
		}
    }
		if(frm.doc.__unsaved){
			if(frm.doc.production_item){
				frappe.call({
				"method" :"instrument.instrument.custom_instrument.work_order.work_order.get_engineering_revision",
				"args" : {
					item_code : frm.doc.production_item
				},
				callback:function(r){
					if(r.message){
						frm.set_value('engineering_revision', r.message)
					}
				}
			})
			}
			
			if(frm.doc.required_items){
				frm.doc.required_items.forEach(function(row){
					if(row['item_code']){
						frappe.call({
							"method" :"instrument.instrument.custom_instrument.work_order.work_order.get_engineering_revision",
							"args" : {
								item_code : row['item_code'],
								bom_no : frm.doc.bom_no
							},
							callback:function(r){
								if(r.message){
									frappe.model.set_value(row.doctype, row.name, 'engineering_revision', r.message[0]['engineering_revision'])
									frappe.model.set_value(row.doctype, row.name, 'use_specific_engineering_revision', r.message[0]['use_specific_engineering_revision'])
								}
							}
						})
					}

				})
			}

		}		
	}
});
