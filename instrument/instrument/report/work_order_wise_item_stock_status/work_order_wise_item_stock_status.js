// Copyright (c) 2016, instrument and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Work Order Wise Item Stock Status"] = {
	"filters": [
	// {
	// 		"fieldname":"planned_start_date",
	// 		"label": __("Planned Start Date"),
	// 		"fieldtype": "Date",
	// 		"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
	// 		"width": "80"
	// 	},
	// 	{
	// 		"fieldname":"planned_end_date",
	// 		"label": __("Planned End Date"),
	// 		"fieldtype": "Date",
	// 		"default": frappe.datetime.get_today()
	// 	},
		{
			"fieldname":"work_order",
			"label": __("Work Order"),
			"fieldtype": "Link",
			"options": "Work Order"
		},
		{
			"fieldname":"production_plan",
			"label": __("Production Plan"),
			"fieldtype": "Link",
			"options": "Production Plan"
		}

	]
};
