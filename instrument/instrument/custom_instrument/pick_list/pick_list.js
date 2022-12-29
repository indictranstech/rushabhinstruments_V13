frappe.ui.form.on("Pick List", {
	refresh:function(frm){
		if (!frm.doc.__islocal) {
				cur_frm.add_custom_button(__('Print Label'),function(){
					var dialog = new frappe.ui.Dialog({
						title: __('Pick List Details'),
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
})
var create_label_print = function(frm,dialog){
	frappe.call({
		method: 'instrument.instrument.custom_instrument.pick_list.pick_list.print_label',
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

