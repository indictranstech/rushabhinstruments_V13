// Copyright (c) 2023, instrument and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Standard Item Mapping With Standard BOM"] = {
	"filters": [
		{
            fieldname: 'item',
            label: __('Item'),
            fieldtype: 'Link',
			options: "Item"
        },
	]
};
