frappe.ui.form.on('Item',{
	refresh:function(frm){
		//Filter Engineering Revision
		cur_frm.fields_dict['engineering_revision'].get_query = function(doc, cdt, cdn) {
			return {
				filters: [
					['Engineering Revision','item_code', '=', frm.doc.item_code],
				]
			}
	    }
	}
})