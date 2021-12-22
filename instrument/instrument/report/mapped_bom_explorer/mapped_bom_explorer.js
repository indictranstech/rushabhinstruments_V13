// Copyright (c) 2016, instrument and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Mapped BOM Explorer"] = {
	"filters": [
		{
			fieldname: "mapped_bom",
			label: __("Mapped BOM"),
			fieldtype: "Link",
			options: "Mapped BOM",
			reqd: 1
		},
	]
};
