frappe.ui.form.on("Batch", {
	refresh:function(frm){
		cur_frm.add_custom_button(__('Print Label'),function(){
			var dialog = new frappe.ui.Dialog({
				title: __('Batch Travller Details'),
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
					"fieldtype": "Data",
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
			// frappe.call({
			// 	'method':'instrument.instrument.custom_instrument.batch.batch.print_label',
			// 	'args':{
			// 		batch_name:frm.doc.name,
			// 		part_no : frm.doc.item
			// 	},
			// 	callback:function(r){
					
			// 	}
			// })
		})

	}
})
var create_label_print = function(frm,dialog){
	frappe.call({
		method: 'instrument.instrument.custom_instrument.batch.batch.print_label',
		// async: false,
		args: {
            "data": dialog.get_values(),
            "doc": frm.doc
        },
		callback: (r) => {
			if(r.message)
			{
				console.log("===================",r.message)
				frappe.msgprint("Batch Travller Created. You can open it through" + r.message)

			}
		}
	});
};

