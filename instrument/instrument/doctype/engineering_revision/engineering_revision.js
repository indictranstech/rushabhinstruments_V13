// Copyright (c) 2021, instrument and contributors
// For license information, please see license.txt

frappe.ui.form.on('Engineering Revision', {
	refresh: function(frm) {
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
