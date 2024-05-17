frappe.listview_settings['Mapped BOM'] = {
	// colwidths: {"name": 8,"is_active":1,"is_default":1,"item":1},
	add_fields: ["is_active", "is_default"],
	get_indicator: function(doc) {
		if(doc.is_default) {
			return [__("Default"), "green", "is_default,=,Yes"];
		} else if(doc.is_active) {
			return [__("Active"), "blue", "is_active,=,Yes"];
		} else if(!doc.is_active) {
			return [__("Not active"), "gray", "is_active,=,No"];
		}
	}
};

