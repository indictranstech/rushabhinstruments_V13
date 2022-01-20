
frappe.ui.form.on("Task", {
	refresh:function(frm){
		if(!frm.doc.__islocal) {
			frm.add_custom_button(__('Move Task'), function() {
			var dialog = new frappe.ui.Dialog({
				title: 'Move Task',
				fields: [
				{	"fieldtype": "Link", 
					"label": __("Task To Be Moved"), 
					"fieldname": "task_to_be_moved",
					"options" : "Task",
					"read_only": 1,
					"default":frm.doc.name 
				},
				// {	"fieldtype":"Check",
				// 	"label":__("Is Group"),
				// 	"fieldname":"is_group",
				// 	"reqd":0
				// },
				{	"fieldtype":"Link",
					"label":__("Parent Task"),
					"fieldname":"parent_task",
					"options" : "Task",
					"reqd":0,
					get_query: function() {
						return frm.events.parent_task_query(frm);
					}
				},
				{
					"fieldtype": "Button", 
					"label": __("Submit"), 
					"fieldname": "move_task"
				}
				]
			});
			dialog.fields_dict.move_task.input.onclick = function() {
				var task_to_be_moved = $("input[data-fieldname='task_to_be_moved']").val();
				var is_group = $("input[data-fieldname='is_group']").val();
				var parent_task = $("input[data-fieldname='parent_task']").val();
				if(task_to_be_moved == ''){
					frappe.throw("Please set value for task")
				}
				else{
					var args = dialog.get_values();
					frappe.call({
						method: "instrument.instrument.custom_instrument.task.task.move_task",
						args: {
							"task_to_be_moved": args.task_to_be_moved,
							"parent_task" :  args.parent_task || ''
						},
						callback: function (r) {
							if(r.message){
								dialog.hide()
								frappe.msgprint("Task Moved Successfully")
								frm.reload_doc()
							}
						}
						
					});

				}
			}
			dialog.show();
		});

		}
	},
	parent_task_query:function(frm){
		var filters = {
			"is_group": 1,
			"name": ["!=", frm.doc.name]
		};
		if (frm.doc.project) filters["project"] = frm.doc.project;
		return {
			filters: filters
		}
		
	}
})