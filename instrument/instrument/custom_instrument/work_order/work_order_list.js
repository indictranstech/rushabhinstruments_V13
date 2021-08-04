
frappe.listview_settings['Work Order'] = {
	add_fields: ["status","item_stock_status"],
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
		if(doc.item_stock_status==="Qty Not Available") {
			return [__("Qty Not Available"), "red", "item_stock_status,=,Qty Not Available"];
		} else {
			return [__(doc.item_stock_status), {
				"Partial Qty Available": "orange",
				"Full Qty Available": "green"
			}[doc.item_stock_status], "item_stock_status,=," + doc.item_stock_status];
		}
		if(doc.item_stock_status=="Full Qty Available") {
			return [__("Full Qty Available"), "green", "item_stock_status,=,Full Qty Available"];
		} else if(doc.item_stock_status=="Partial Qty Available") {
			return [__("Partial Qty Available"), "orange", "item_stock_status,=,Partial Qty Available"];
		} else if(doc.item_stock_status=="Qty Not Available") {
			return [__("Qty Not Available"), "red", "item_stock_status,=,Qty Not Available"];
		}
	}
};