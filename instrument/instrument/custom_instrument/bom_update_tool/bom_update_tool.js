frappe.ui.form.on('BOM Update Tool',{
	replace:function(frm){
		if(frm.doc.current_bom && frm.doc.new_bom){
			frappe.call({
				method : "instrument.instrument.custom_instrument.bom_update_tool.bom_update_tool.update_mapped_bom_item",
				args:{
					current_bom : frm.doc.current_bom,
					new_bom : frm.doc.new_bom,
					current_doc: frm.doc.new_bom
				},
				callback:function(r){
					if(r.message){
					}
				}
			})
		}
	}
})