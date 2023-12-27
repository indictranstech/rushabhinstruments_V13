from frappe import _


def get_data():
	return {
		"fieldname": "consolidated_pick_list",
		"non_standard_fieldnames": {
			"Work Order": "consolidated_pick_list",
			"Stock Entry":"consolidated_pick_list"
		},
		"transactions": [
			{"label": _("Stock"), "items": ["Stock Entry"]},
			{"label": _("Manufacture"), "items": ["Work Order"]},
		]
	}