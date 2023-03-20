// Copyright (c) 2023, instrument and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Standard Item Mapping With Mapped BOM"] = {
	"filters": [
	{
			fieldname: "mapped_bom",
			label: __("Mapped BOM"),
			fieldtype: "Link",
			options: "Mapped BOM",
			reqd: 1
		}

	]
};
