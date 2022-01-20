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
