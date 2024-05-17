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
		frm.set_query("revision", "other_engineering_revision", function(doc, cdt, cdn) {
			const row = locals[cdt][cdn];
			return {
				query: "instrument.instrument.custom_instrument.request_for_quotation.request_for_quotation.get_engineering_revisions_for_filter",
				filters:{ 'item_code': row.item_code }
			}
		});
		frm.set_query("purchase_package_name", "other_engineering_revision", function(doc, cdt, cdn) {
			const row = locals[cdt][cdn];
			return {
				query: "instrument.instrument.doctype.engineering_revision.engineering_revision.get_purchasing_pkg_name",
				filters:{ 'item_code': row.item_code}
			}
		});
		frm.set_query("manufacturing_package_name", "other_engineering_revision", function(doc, cdt, cdn) {
			const row = locals[cdt][cdn];
			return {
				query: "instrument.instrument.doctype.engineering_revision.engineering_revision.get_manufacturing_pkg_name",
				filters:{ 'item_code': row.item_code }
			}
		});
		frm.set_query("engineering_package_name", "other_engineering_revision", function(doc, cdt, cdn) {
			const row = locals[cdt][cdn];
			return {
				query: "instrument.instrument.doctype.engineering_revision.engineering_revision.get_engineering_pkg_name",
				filters:{ 'item_code': row.item_code }
			}
		});

	}
});
frappe.ui.form.on('Other Engineering Revisions', {
	// exclude_purchasing_package:function(frm,cdt,cdn){
	// 	console.log("*******************")
	// 	var row = locals[cdt][cdn]
	// 	console.log("$$$$$$$",row.exclude_purchasing_package)
	// 	var df = frappe.meta.get_docfield("Other Engineering Revisions","purchase_package_name", cur_frm.doc.name);
	// 	console.log("====================before",df)
	// 	if(row.exclude_purchasing_package == 1){
	// 		var df = frappe.meta.get_docfield("Other Engineering Revisions","purchase_package_name", cur_frm.doc.name);
	// 		console.log("IIIIIIIIIIIIIIIII",df)
	// 		df.hidden = 1;
	// 		df.read_only=1;
	// 		frm.refresh_fields();
	// 	}
	// },
})
