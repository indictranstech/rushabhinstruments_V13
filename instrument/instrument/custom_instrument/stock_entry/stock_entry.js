frappe.ui.form.on("Stock Entry", {
	refresh:function(frm){
		if(frm.doc.stock_entry_type == 'Material Transfer' || frm.doc.stock_entry_type == 'Material Receipt'){
			frm.set_value("apply_putaway_rule",1)
		}
	}
})