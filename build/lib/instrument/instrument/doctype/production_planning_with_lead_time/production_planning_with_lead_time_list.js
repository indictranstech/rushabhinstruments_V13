frappe.listview_settings['Production Planning With Lead Time'] = {
	add_fields: ["status", "sales_order", "from_date",
		"to_date"],
	get_indicator: function(doc) {
		if(doc.status==="Submitted") {
			return [__("Not Started"), "orange", "status,=,Submitted"];
		} else {
			return [__(doc.status), {
				"Draft": "red",
				"Stopped": "red",
				"Not Started": "red",
				"In Progress": "orange",
				"Completed": "green",
				"Cancelled": "grey"
			}[doc.status], "status,=," + doc.status];
		}
	}
};
