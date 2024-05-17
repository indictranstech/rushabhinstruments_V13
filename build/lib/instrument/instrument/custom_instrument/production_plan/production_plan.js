frappe.ui.form.on('Production Plan', {
	refresh:function(frm){
		//Hide Pick List,Work Order from Create Button
		setTimeout(() => {
			 	frm.remove_custom_button('Work Order / Subcontract PO', 'Create');
			 	}, 10);
		if (frm.doc.po_items && frm.doc.status !== "Closed" && frm.doc.docstatus == 1) {
			frm.add_custom_button(__('Work Orders / Subcontract PO'), () => frm.events.create_work_orders(frm),
					__("Create"));
		}
		
	},
	create_work_orders:function(frm){
		frappe.call({
			method : "instrument.instrument.custom_instrument.production_plan.production_plan.make_work_order",
			freeze: true,
			args : {
				doc : frm.doc
			},
			callback:function(r){
				frm.reload_doc();
			}
		})
	},
	get_sub_assembly_items: function(frm) {
		frm.dirty();
		frappe.call({
			method: "instrument.instrument.custom_instrument.production_plan.production_plan.get_sub_assembly_items",
			args:{
					doc: frm.doc
			},
			callback:function(r) {
				if(r.message){
					frm.doc.sub_assembly_items = ''
					$.each(r.message, function(idx, new_row){
						$.each(new_row, function(idx, item_row){
							var row = frappe.model.add_child(frm.doc, "Production Plan Sub Assembly Item", "sub_assembly_items");
							frappe.model.set_value(row.doctype, row.name, 'available_quantity', item_row['available_quantity']);
							frappe.model.set_value(row.doctype, row.name, 'bom_level', item_row['bom_level']);
							frappe.model.set_value(row.doctype, row.name, 'bom_no', item_row['bom_no']);
							frappe.model.set_value(row.doctype,row.name,'description',item_row['description']);
							frappe.model.set_value(row.doctype,row.name,'fg_warehouse',item_row['fg_warehouse']);
							frappe.model.set_value(row.doctype,row.name,'indent',item_row['indent']);
							frappe.model.set_value(row.doctype,row.name,'is_sub_contracted_item',item_row['is_sub_contracted_item']);
							frappe.model.set_value(row.doctype,row.name,'item_name',item_row['item_name']);
							frappe.model.set_value(row.doctype,row.name,'original_required_qty',item_row['original_required_qty']);
							frappe.model.set_value(row.doctype,row.name,'parent_item_code',item_row['parent_item_code']);
							frappe.model.set_value(row.doctype,row.name,'production_item',item_row['production_item']);
							frappe.model.set_value(row.doctype,row.name,'qty',item_row['qty']);
							frappe.model.set_value(row.doctype,row.name,'schedule_date',item_row['schedule_date']);
							frappe.model.set_value(row.doctype,row.name,'stock_qty',item_row['stock_qty']);
							frappe.model.set_value(row.doctype,row.name,'stock_uom',item_row['stock_uom']);
							frappe.model.set_value(row.doctype,row.name,'type_of_manufacturing',item_row['type_of_manufacturing']);
							frappe.model.set_value(row.doctype,row.name,'uom',item_row['uom']);
						})
					})
				}

				refresh_field("sub_assembly_items");
			}
		});
	}
})