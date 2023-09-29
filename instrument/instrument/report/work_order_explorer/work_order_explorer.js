// Copyright (c) 2023, instrument and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Work Order Explorer"] = {
	"filters": [
		{
			fieldname: "work_order",
			label: __("Work Order"),
			fieldtype: "Link",
			options: "Work Order"
		},
		{
			fieldname: "production_item",
			label: __("Production Item"),
			fieldtype: "Link",
			options: "Item"
		},
		// {
		// 	fieldname: "status",
		// 	label: __("Status"),
		// 	fieldtype: "Select",
		// 	options : ['Not Started','In Progress','Completed']
		// }
	]
};
