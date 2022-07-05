// Copyright (c) 2022, instrument and contributors
// For license information, please see license.txt

// frappe.ui.form.on('Bulk Payment Process', {
// 	// refresh: function(frm) {

// 	// }
// });
// Copyright (c) 2022, Indictrans and contributors
// For license information, please see license.txt

frappe.ui.form.on('Bulk Payment Process', {
	onload: function(frm, cdt, cdn){
		hide_approve_checkbox(frm, cdt, cdn);
		apply_read_only_for_approve(frm, cdt, cdn);
	},
	refresh: function(frm, cdt, cdn){
		hide_approve_checkbox(frm, cdt, cdn);
		apply_read_only_for_approve(frm, cdt, cdn);
		if(frm.doc.docstatus!=0){
			frm.set_df_property('get_invoices', 'read_only', 1);
			frm.set_df_property('get_invoices', 'hidden', 1);
		}
		else {
			frm.set_df_property('get_invoices', 'read_only', 0);
			frm.set_df_property('get_invoices', 'hidden', 0);
		}
		check_mode_of_payment(frm);
		if(frm.doc.docstatus == 1) {
			cur_frm.add_custom_button(__('Create Payment'),function(){
				frappe.call({
					method: "on_update_after_submit",
					doc: frm.doc,
					callback: function(r) {

					}
				});
			},__("Menu"))
		}
	},
	get_invoices: function(frm) {
		frm.doc.items = ''
		frappe.call({
			method: "get_invoices_with_filters",
			doc: frm.doc,
			callback: function(r) {
				refresh_field("items");
			}
		});
  //   frm.clear_table("items");
		// frm.refresh_fields();
    // get_invoices_with_filters(frm);
	},
	upto_due_date: function(frm){
		frm.set_value('from_invoice_date',);
		frm.set_value('to_invoice_date',);
		frm.refresh_fields();
	},
	validate: function(frm){
		calculate_totals(frm);
	},
	mode_of_payment: function(frm){
		if(frm.doc.mode_of_payment){
			get_payment_mode_account(frm, frm.doc.mode_of_payment, function(account){
				frm.set_value("payment_account", account);
			});
			check_mode_of_payment(frm);
		}
	}
});

function get_invoices_with_filters(frm){
  frappe.call({
    "method":"instrument.instrument.doctype.bulk_payment_process.bulk_payment_process.get_invoices_with_filters",
    "args":{
			'upto_due_date' : frm.doc.upto_due_date,
			'from_invoice_date' : frm.doc.from_invoice_date,
			'to_invoice_date' : frm.doc.to_invoice_date,
			// 'supplier_group' : frm.doc.supplier_group,
			'order_by': frm.doc.order_by,
			'sort_by': frm.doc.sort_as
    },
    callback: function(r){
			console.log(r);
      if(r && r.message && r.message.length > 0){
        for(var i=0; i< r.message.length; i++){
          let row =frm.add_child('items',{
            invoice_no: r.message[i].name
          });
          frm.script_manager.trigger("invoice_no", row.doctype, row.name);
          
        }
        // refresh_field("items");
        frm.save();
				calculate_totals(frm);
        // refresh_fields();
      }
			else{
				frappe.show_alert('No Purchase Invoice found with given filters', 5);
			}
    }
  })
}

function calculate_totals(frm){
	var total_outstanding_amount = 0;
	var total_paid_amount = 0;
	$.each(frm.doc.items || [],function(i,item){
		total_outstanding_amount=total_outstanding_amount+item.outstanding_amount;
		total_paid_amount=total_paid_amount+item.amount;
	});
	frm.set_value('total_outstanding_amount', total_outstanding_amount);
	frm.set_value('total_paid_amount', total_paid_amount);
	frm.refresh_fields()
}

var get_payment_mode_account = function(frm, mode_of_payment, callback) {
	if(!frm.doc.company) {
		frappe.throw({message:__("Please select a Company first."), title: __("Mandatory")});
	}
	if(!mode_of_payment) {
		return;
	}
	return  frappe.call({
		method: "erpnext.accounts.doctype.sales_invoice.sales_invoice.get_bank_cash_account",
		args: {
			"mode_of_payment": frm.doc.mode_of_payment,
			"company": frm.doc.company
		},
		callback: function(r, rt) {
			if(r.message) {
				callback(r.message.account)
			}
		}
	});
}

function check_mode_of_payment(frm){
	if(frm.doc.mode_of_payment){
		frm.toggle_reqd('reference_no', frm.doc.mode_of_payment!="Cash");
		frm.toggle_reqd('reference_date', frm.doc.mode_of_payment!="Cash");
		if(frm.doc.mode_of_payment=="Cash"){
			frm.set_df_property('reference_no', 'read_only', 1);
			frm.set_df_property('reference_date', 'read_only', 1);
		}
		else {
			frm.set_df_property('reference_no', 'read_only', 0);
			frm.set_df_property('reference_date', 'read_only', 0);
		}
	}
}

function hide_unapproved_rows(frm, cdt, cdn){
	if(frm.doc.workflow_state=="Approved"){
		var data = frm.doc.items;
		data.forEach(function(e){
			if (e.approve == "0"){
				$("[data-idx='"+e.idx+"']").hide()
			}
		});
	}
}

function hide_approve_checkbox(frm, cdt, cdn){
	if(frm.doc.docstatus!=1){
		var data = frm.doc.items;
		data.forEach(function(e){
				$("[data-fieldname='approve']").hide()
		});
	}
}

function apply_read_only_for_approve(frm, cdt, cdn){
	if(frm.doc.workflow_state!="Pending"){
		var df1 = frappe.meta.get_docfield("Bulk Payment Process Item", "approve", frm.doc.name);
		df1.read_only = 1;
		df1.hidden = 1;
		frm.refresh_field('items');
	}
}