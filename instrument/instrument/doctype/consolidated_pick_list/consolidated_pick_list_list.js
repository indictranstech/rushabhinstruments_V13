
frappe.listview_settings['Consolidated Pick List'] = {
	get_indicator: function(doc) {
		if(doc.status==="Submitted") {
			return [__("Submitted"), "orange", "status,=,Submitted"];
		} else {
			return [__(doc.status), {
				"Draft": "red",
				// "Submitted": "orange",
				"Completed": "green",
				"Cancelled": "gray"
			}[doc.status], "status,=," + doc.status];
		}
	}
};