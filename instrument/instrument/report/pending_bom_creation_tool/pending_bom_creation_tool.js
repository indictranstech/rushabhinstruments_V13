// Copyright (c) 2024, instrument and contributors
// For license information, please see license.txt

frappe.query_reports["Pending BOM Creation Tool"] = {
	"filters": [
		{
			fieldname: "mapped_bom",
			label: __("Mapped BOM"),
			fieldtype: "Link",
			options: "Mapped BOM",
			// reqd: 1
		},
		{
			fieldname: "mapped_item",
			label: __("Item"),
			fieldtype: "Link",
			options: "Item",
			// reqd: 1
		},
	]
};
