
frappe.listview_settings['Work Order'] = {
	refresh:function(listview){
		listview.page.add_action_item(__("Create Work Order Pick List"), function() {
			const assets = listview.get_checked_items();
			var data = {work_order_data:assets};
			// var data = assets[0]
			var myJSON = JSON.stringify(data);
			// var link =  "#Form/Stock Entry/New Stock Entry 1?data="+myJSON
			// var newWindow =window.open(link,"_blank");
			var old_link = window.location.href
			var split_data = old_link.split("/app")
			var link =  split_data[0]+"/app#work-order-pick-list/new-work-order-pick-list-1?data="+myJSON
			window.open(link);
			// listview.call_for_selected_items(method, {"status": "Not Started"});
		});
	},
	add_fields: ["bom_no", "status", "sales_order", "qty",
		"produced_qty", "expected_delivery_date", "planned_start_date", "planned_end_date"],
	filters: [["status", "!=", "Stopped"]],
	get_indicator: function(doc) {
		if(doc.status==="Submitted") {
			return [__("Not Started"), "orange", "status,=,Submitted"];
		} else {
			return [__(doc.status), {
				"Draft": "red",
				"Stopped": "red",
				"Not Started": "red",
				"In Process": "orange",
				"Completed": "green",
				"Cancelled": "gray"
			}[doc.status], "status,=," + doc.status];
		}
	}
	// add_fields: ["status","item_stock_status"],
	// get_indicator: function(doc) {
	// 	if(doc.status==="Submitted") {
	// 		return [__("Not Started"), "orange", "status,=,Submitted"];
	// 	} else {
	// 		return [__(doc.status), {
	// 			"Draft": "red",
	// 			"Stopped": "red",
	// 			"Not Started": "red",
	// 			"In Process": "orange",
	// 			"Completed": "green",
	// 			"Cancelled": "gray"
	// 		}[doc.status], "status,=," + doc.status];
	// 	}
	// 	if(doc.item_stock_status==="Qty Not Available") {
	// 		return [__("Qty Not Available"), "red", "item_stock_status,=,Qty Not Available"];
	// 	} else {
	// 		return [__(doc.item_stock_status), {
	// 			"Partial Qty Available": "orange",
	// 			"Full Qty Available": "green"
	// 		}[doc.item_stock_status], "item_stock_status,=," + doc.item_stock_status];
	// 	}
	// 	if(doc.item_stock_status=="Full Qty Available") {
	// 		return [__("Full Qty Available"), "green", "item_stock_status,=,Full Qty Available"];
	// 	} else if(doc.item_stock_status=="Partial Qty Available") {
	// 		return [__("Partial Qty Available"), "orange", "item_stock_status,=,Partial Qty Available"];
	// 	} else if(doc.item_stock_status=="Qty Not Available") {
	// 		return [__("Qty Not Available"), "red", "item_stock_status,=,Qty Not Available"];
	// 	}
	// }
};