// Copyright (c) 2022, instrument and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Work Order Pick List Item"] = {
	"filters": [
		{
			fieldname: "work_order_pick_list",
			label: __("Work Order Pick List"),
			fieldtype: "Link",
			options: "Work Order Pick List",
			reqd: 1
		},

	]
};
