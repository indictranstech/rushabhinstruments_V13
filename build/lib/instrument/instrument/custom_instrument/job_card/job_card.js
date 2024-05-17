frappe.ui.form.on("Job Card", {
	refresh:function(frm){
		//Filter Engineering Revision
		frm.set_query("engineering_revision", "items", function(doc, cdt, cdn) {
			const row = locals[cdt][cdn];
			return {
				query: "instrument.instrument.custom_instrument.bom.bom.get_engineering_revisions_for_filter",
				filters:{ 'item_code': row.item_code }
			}
		});
		if (!frm.doc.__islocal) {
				cur_frm.add_custom_button(__('Print Label'),function(){
					var dialog = new frappe.ui.Dialog({
						title: __('Job Card Traveler Details'),
						keep_open: true,
						fields: [
						{
							"label": "Enter No of Copies",
							"fieldname": "no_of_copies",
							"fieldtype": "Data",
							"reqd": 1
						},
						{
							"label": "Printer Name",
							"fieldname": "printer_name",
							"fieldtype": "Link",
							"options":"Printer",
							"reqd": 1
						}
						],
						onhide: () => {
						}
						});
						dialog.set_primary_action(__('Submit'), () => {
							create_label_print(frm,dialog);
							dialog.hide()
						});
						dialog.show();
				})
		}	
	}
});
frappe.ui.form.on('Job Card Item', {
    item_code: function(frm, cdt, cdn) {
		var row = locals[cdt][cdn]
		if(row.item_code){
			frappe.call({
				"method" :"instrument.instrument.custom_instrument.job_card.job_card.get_engineering_revision",
				"args" : {
					item_code : row.item_code,
					work_order : frm.doc.work_order
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

var create_label_print = function(frm,dialog){
	frappe.call({
		method: 'instrument.instrument.custom_instrument.job_card.job_card.print_label',
		// async: false,
		args: {
            "data": dialog.get_values(),
            "doc": frm.doc
        },
		callback: (r) => {
			if(r.message)
			{
				frappe.msgprint("Work Order Traveler Created. You can open it through" + r.message)

			}
		}
	});
};

