# Copyright (c) 2023, instrument and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
	data = get_is_active_default_bom(filters)
	columns = get_columns()
	return columns, data

def get_is_active_default_bom(filters):
    conditions = get_conditions(filters)
    bom_list= frappe.db.sql('''select name, item, item_name, is_active, is_default from `tabBOM` where is_active=1 and is_default=1 %s ''' % conditions, filters, as_dict=1, debug=1)
    return bom_list
    
def get_columns():
	return[
		{
			'fieldname': 'name',
            'label': 'Name',
            'fieldtype': 'Link',
			"width": 250,
			'options': 'BOM'
		},
		{
			'fieldname': 'item',
            'label': 'Item',
            'fieldtype': 'Link',
			"width": 150,
			'options': 'BOM'
		},
		{
			'fieldname': 'item_name',
            'label': 'Item Name',
            'fieldtype': 'Data',
			"width": 300,
			'options': 'BOM'
		},
		{
			'fieldname': 'is_active',
            'label': 'Is Active',
            'fieldtype': 'check',
			"width": 150,
		},
		{
			'fieldname': 'is_default',
            'label': 'Is Default',
            'fieldtype': 'check',
			"width": 150,
		}

	]

def get_conditions(filters=None):
	conditions = ''
	if filters.get('item'):
		conditions += ' and item=%(item)s'

	return conditions


    
    

