// Copyright (c) 2021, instrument and contributors
// For license information, please see license.txt

frappe.ui.form.on('Engineering Revision', {
	purchasing_package_on_form_rendered:function(frm, cdt, cdn){
		// hide delete, insert above and insert below fields inside Scrap Finished Good child table
		frm.fields_dict['purchasing_package'].grid.wrapper.find('.grid-delete-row').hide();
		frm.fields_dict['purchasing_package'].grid.wrapper.find('.grid-insert-row-below').hide();
		frm.fields_dict['purchasing_package'].grid.wrapper.find('.grid-insert-row').hide();
	},
	manufacturing_package_on_form_rendered:function(frm, cdt, cdn){
		// hide delete, insert above and insert below fields inside Scrap Finished Good child table
		frm.fields_dict['manufacturing_package'].grid.wrapper.find('.grid-delete-row').hide();
		frm.fields_dict['manufacturing_package'].grid.wrapper.find('.grid-insert-row-below').hide();
		frm.fields_dict['manufacturing_package'].grid.wrapper.find('.grid-insert-row').hide();
	},
	engineering_package_on_form_rendered:function(frm, cdt, cdn){
		// hide delete, insert above and insert below fields inside Scrap Finished Good child table
		frm.fields_dict['engineering_package'].grid.wrapper.find('.grid-delete-row').hide();
		frm.fields_dict['engineering_package'].grid.wrapper.find('.grid-insert-row-below').hide();
		frm.fields_dict['engineering_package'].grid.wrapper.find('.grid-insert-row').hide();
	},
	refresh: function(frm) {
		
		frm.fields_dict['purchasing_package'].grid.wrapper.find('.grid-insert-row').hide();
		frm.fields_dict['purchasing_package'].grid.wrapper.find('.grid-insert-row-below').hide();
		frm.fields_dict['purchasing_package'].grid.wrapper.find('.grid-add-row').hide();

		frm.fields_dict['manufacturing_package'].grid.wrapper.find('.grid-insert-row').hide();
		frm.fields_dict['manufacturing_package'].grid.wrapper.find('.grid-insert-row-below').hide();
		frm.fields_dict['manufacturing_package'].grid.wrapper.find('.grid-add-row').hide();

		frm.fields_dict['engineering_package'].grid.wrapper.find('.grid-insert-row').hide();
		frm.fields_dict['engineering_package'].grid.wrapper.find('.grid-insert-row-below').hide();
		frm.fields_dict['engineering_package'].grid.wrapper.find('.grid-add-row').hide();

		cur_frm.fields_dict['purchasing_package'].grid.get_field("purchasing_package_name").get_query = function(doc, cdt, cdn) {
			return {
				filters: [
					["Package Document", "package_type", "=", 'Purchasing_Package'],
					["Package Document", "item_code", "=", frm.doc.item_code]
				]
			}
		};

		cur_frm.fields_dict['manufacturing_package'].grid.get_field("manufacturing_package_name").get_query = function(doc, cdt, cdn) {
			return {
				filters: [
					["Package Document", "package_type", "=", 'Manufacturing_Package'],
					["Package Document", "item_code", "=", frm.doc.item_code]
				]
			}
		};

		cur_frm.fields_dict['engineering_package'].grid.get_field("engineering_package_name").get_query = function(doc, cdt, cdn) {
			return {
				filters: [
					["Package Document", "package_type", "=", 'Engineering_Package'],
					["Package Document", "item_code", "=", frm.doc.item_code]
				]
			}
		};

	}
});
