import frappe
@frappe.whitelist()
def move_task(task_to_be_moved,parent_task):
	if task_to_be_moved :
		task_doc = frappe.get_doc("Task",task_to_be_moved)
		if task_doc:
			old_parent = task_doc.parent_task
			if parent_task:
				new_parent = parent_task
				task_doc.parent_task = parent_task
				if new_parent:
					new_parent_doc = frappe.get_doc("Task",new_parent)
					if new_parent_doc:
						new_parent_doc.append('depends_on',{
							'task':task_to_be_moved,
							'subject':task_doc.subject
						})
						new_parent_doc.save()
			else:
				task_doc.parent_task = ''
			if old_parent:
				old_parent_doc = frappe.get_doc("Task",old_parent)
				if old_parent_doc:
					if old_parent_doc.depends_on:
						for d in old_parent_doc.depends_on:
							if d.task == task_to_be_moved:
								old_parent_doc.remove(d)
						old_parent_doc.save()
			
			task_doc.save()
			return task_doc
@frappe.whitelist()
def get_children(doctype, parent, task=None, project=None,subject=None,status = None,is_root=False):

	filters = [['docstatus', '<', '2']]

	if task:
		filters.append(['parent_task', '=', task])
	elif parent and not is_root:
		# via expand child
		filters.append(['parent_task', '=', parent])
	else:
		filters.append(['ifnull(`parent_task`, "")', '=', ''])

	if project:
		filters.append(['project', '=', project])
	if subject:
		filters.append(['subject' , 'LIKE',"%%%s%%" % subject])
	if status:
		filters.append(['status','=',status])

	tasks = frappe.get_list(doctype, fields=[
		'name as value',
		'subject as title',
		'is_group as expandable'
	], filters=filters, order_by='name')

	# return tasks
	return tasks

@frappe.whitelist()
def get_count(doc):
	if doc:
		count = frappe.db.sql("""SELECT count(d.task) as count from `tabTask Depends On` d join `tabTask` t on t.name = d.task where d.parent = '{0}' and t.status in ('Open','Pending Review','Overdue','Working')""".format(doc),as_dict=1)
		return count