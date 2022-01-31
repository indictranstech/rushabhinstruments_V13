# Copyright (c) 2013, instrument and contributors
# For license information, please see license.txt

import frappe
def execute(filters=None):
	data = []
	columns = get_columns()
	get_data(filters, data)
	return columns, data

def get_data(filters, data):
	get_exploded_items(filters, data)

def get_exploded_items(filters, data, indent=0):
	conditions = get_conditions(filters)
	task_list = frappe.db.sql("""SELECT name,subject,status,is_group,parent_task,priority,issue,exp_start_date,exp_end_date,expected_time,progress ,project from `tabTask` where parent_task is null and {0}""".format(conditions),as_dict=1,debug=1)
	
	for item in task_list:
		print(item.name, indent)
		item["indent"] = indent
		data.append({
			'name': item.name,
			'subject': item.subject,
			'project' : item.project,
			'indent': indent,
			'status': item.status,
			'is_group':item.is_group,
			'parent_task' : item.parent_task,
			'priority':item.priority,
			'issue':item.issue,
			'exp_start_date':item.exp_start_date,
			'exp_end_date':item.exp_end_date,
			'expected_time':item.expected_time,
			'progress':item.progress
		})
		if item.is_group :
			get_exploded_tasks(item.name, data, indent=indent+1)
		else:
			print(item.name, indent)
			item["indent"] = indent
			data.append({
				'name': item.name,
				'subject': item.subject,
				'project' : item.project,
				'indent': indent,
				'status': item.status,
				'is_group':item.is_group,
				'parent_task' : item.parent_task,
				'priority':item.priority,
				'issue':item.issue,
				'exp_start_date':item.exp_start_date,
				'exp_end_date':item.exp_end_date,
				'expected_time':item.expected_time,
				'progress':item.progress
				})
		
def get_exploded_tasks(task,data,indent=0):
	exploded_items = frappe.get_all("Task",
		filters={"parent_task": task},
		fields= ['name','subject','status','is_group','parent_task','priority','issue','exp_start_date','exp_end_date','expected_time','progress'])
	for item in exploded_items:
		
		print(item.name, indent)
		item["indent"] = indent
		data.append({
			'name': item.name,
			'subject': item.subject,
			'project' : item.project,
			'indent': indent,
			'status': item.status,
			'is_group': item.is_group,
			'parent_task' :item.parent_task,
			'priority':item.priority,
			'issue':item.issue,
			'exp_start_date':item.exp_start_date,
			'exp_end_date':item.exp_end_date,
			'expected_time':item.expected_time,
			'progress':item.progress
		})
		if item.is_group:
			get_exploded_tasks(item.name, data, indent=indent+1)

def get_columns():
	return [
		{
			"label": "Task Name",
			"fieldtype": "Link",
			"fieldname": "name",
			"width": 250,
			"options": "Task"
		},
		{
			"label": "Subject",
			"fieldtype": "data",
			"fieldname": "subject",
			"width": 300
		},
		{
			"label": "Project",
			"fieldtype": "Link",
			"fieldname": "project",
			"options":"Project",
			"width": 150
		},
		{
			"label": "Status",
			"fieldtype": "Data",
			"fieldname": "status",
			"width": 150
		},
		{
			"label": "Is Group",
			"fieldtype": "Data",
			"fieldname": "is_group",
			"width": 150
		},
		{
			"label": "Parent Task",
			"fieldtype": "Link",
			"fieldname": "parent_task",
			"options": "Task",
			"width": 150
		},
		{
			"label": "Priority",
			"fieldtype": "Data",
			"fieldname": "priority",
			"width": 150
		},
		{
			"label": "Issue",
			"fieldtype": "Link",
			"fieldname": "issue",
			"options": "Issue",
			"width": 150
		},
		{
			"label": "Expected Start Date",
			"fieldtype": "Date",
			"fieldname": "exp_start_date",
			"width": 150
		},
		{
			"label": "Expected End Date",
			"fieldtype": "Date",
			"fieldname": "exp_end_date",
			"width": 150
		},
		{
			"label": "Expected Time",
			"fieldtype": "data",
			"fieldname": "expected_time",
			"width": 150
		},
		{
			"label": "Progress",
			"fieldtype": "data",
			"fieldname": "progress",
			"width": 150
		}
	]
def get_conditions(filters=None):
	conditions = "1=1 "
	if filters.get("project") :
		conditions += "and project = '{0}'".format(filters.get("project"))
	if filters.get("subject") :
		conditions += "and subject like '{0}'".format(filters.get("subject"))
	if filters.get("status") :
		conditions += " and status = '{0}' ".format(filters.get("status"))
	if filters.get("task") :
		conditions += " and name = '{0}' ".format(filters.get("task"))
		
	return conditions
