// Copyright (c) 2016, instrument and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Task Explorer"] = {
	"filters": [
		{
			fieldname: "project",
			label: __("Project"),
			fieldtype: "Link",
			options: "Project"
		},
		{
			fieldname: "task",
			label: __("Task"),
			fieldtype: "Link",
			options: "Task"
		},
		{
			fieldname: "subject",
			label: __("Subject"),
			fieldtype: "Data"
		},
		{
			fieldname: "status",
			label: __("Status"),
			fieldtype: "Select",
			options : ['Open','Working','Pending Review','Overdue','Template','Completed','Cancelled']
		},
		{
			fieldname: "priority",
			label: __("Priority"),
			fieldtype: "Select",
			options: ['Low','Medium','High','Urgent']
		}
	]
};
