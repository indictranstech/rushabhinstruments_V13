from frappe import _


def get_data():
	return {
		"fieldname": "production_planning_with_lead_time",
		"non_standard_fieldnames": {
			"Work Order": "production_planning_with_lead_time",
			"Material Request":"production_planning_with_lead_time"
		},
		"transactions": [
			{"label": _("Stock"), "items": ["Material Request"]},
			{"label": _("Manufacture"), "items": ["Work Order"]},
		]
	}