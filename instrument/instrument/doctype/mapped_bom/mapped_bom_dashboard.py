
from frappe import _


def get_data():
	return {
		'fieldname': 'mapped_bom',
		'non_standard_fieldnames': {
			'BOM' : 'mapped_bom'
		},
		'transactions': [
			{
				'label': _('Manufacture'),
				'items': ['BOM']
			}
			
		],
		'disable_create_buttons': ["Item", "Purchase Order", "Purchase Receipt",
			"Purchase Invoice", "Job Card", "Stock Entry", "BOM"]
	}
