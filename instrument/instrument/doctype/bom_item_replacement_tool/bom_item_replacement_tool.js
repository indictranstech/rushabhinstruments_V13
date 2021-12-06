// Copyright (c) 2021, instrument and contributors
// For license information, please see license.txt

frappe.ui.form.on('BOM Item Replacement Tool', {
	refresh: function(frm) {
		cur_frm.fields_dict['old_item_number'].get_query = function(doc, cdt, cdn) {
			return {
				filters: [
					['Item','is_map_item', '=', 0],
				]
			}
	    }

	    cur_frm.fields_dict['new_item_number'].get_query = function(doc, cdt, cdn) {
			return {
				filters: [
					['Item','is_map_item', '=', 0],
				]
			}
	    }
	    cur_frm.fields_dict['new_bom'].get_query = function(doc, cdt, cdn) {
			return {
				filters: [
					['BOM','item', '=', frm.doc.new_item_number],
				]
			}
	    }

	},
	new_item_number:function(frm){
		if(frm.doc.new_item_number){
			frappe.call({
				method : "instrument.instrument.doctype.bom_item_replacement_tool.bom_item_replacement_tool.get_default_bom",
				args : {
					item : frm.doc.new_item_number
				},
				callback:function(r){
					if(r.message){
						frm.set_value("new_bom",r.message)
					}else{
						frm.set_value("new_bom",'')
					}
				}
			})
		}

	},
	replace :function(frm){
		if(frm.doc.old_item_number && frm.doc.new_item_number){
			if(frm.doc.old_item_number == frm.doc.new_item_number){
				frappe.throw("Old Item Number and New Item Number Cannot Be Same")
			}
			return frm.call({
				doc: frm.doc,
				method: "replace",
				freeze: true,
				callback: function(r) {
					if(r.message){
						frappe.msgprint("Item Replaced Successfully")
					}
				}
			})
		}else{
			frappe.throw("Please Enter Old Item Number and New Item Number")
		}
	},
	onload:function(frm){
		frm.set_value('old_item_number','')
		frm.set_value('new_item_number','')
		frm.set_value('new_item_name','')
		frm.set_value('old_item_name','')
		frm.set_value('new_bom','')

	}
});
