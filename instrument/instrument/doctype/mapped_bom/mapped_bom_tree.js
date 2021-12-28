frappe.treeview_settings["Mapped BOM"] = {
	get_tree_nodes: 'instrument.instrument.doctype.mapped_bom.mapped_bom.get_children',
	filters: [
		{
			fieldname: "mapped_bom",
			fieldtype:"Link",
			options: "Mapped BOM",
			label: __("Mapped BOM")
		}
	],
	title: "Mapped BOM",
	breadcrumb: "instrument",
	disable_add_node: true,
	root_label: "Mapped BOM", //fieldname from filters
	get_tree_root: true,
	show_expand_all: true,
	get_label: function(node) {
		if(node.data.qty) {
			return node.data.qty + " x " + node.data.item_code;
		} else {
			return node.data.item_code || node.data.value;
		}
	},
	onload: function(me) {
		var label = frappe.get_route()[0] + "/" + frappe.get_route()[1];
		if(frappe.pages[label]) {
			delete frappe.pages[label];
		}
		var filter = me.opts.filters[0];
		if(frappe.route_options && frappe.route_options[filter.fieldname]) {
			var val = frappe.route_options[filter.fieldname];
			delete frappe.route_options[filter.fieldname];
			filter.default = "";
			me.args[filter.fieldname] = val;
			me.root_label = val;
			me.page.set_title(val);
		}

		me.make_tree();
	},
	toolbar: [
		{ toggle_btn: true },
		{
			label:__("Edit"),
			condition: function(node) {
				return node.expandable;
			},
			click: function(node) {
				var name_string = node.data.value
				if(name_string.startsWith('Map')){
					frappe.set_route("Form", "Mapped BOM", node.data.value);
				}
				else{
					frappe.set_route("Form", "BOM", node.data.value);
				}
				
			}
		},
		{ toggle_btn: false },
		{
			label:__("Check"),
			click:function(node){
				if(node.data.is_map_item){
					frappe.msgprint("Mapped Item")
				}
				else{
					frappe.msgprint("Standard Item")
				}
			}
		}
	],
	menu_items: [
		{
			label: __("New Mapped BOM"),
			action: function() {
				frappe.new_doc("Mapped BOM", true)
			},
			condition: 'frappe.boot.user.can_create.indexOf("Mapped BOM") !== -1'
		}
	],
	onrender: function(node) {
		if(node.is_root && node.data.value!="Mapped BOM") {
			frappe.model.with_doc("Mapped BOM", node.data.value, function() {
				var bom = frappe.model.get_doc("Mapped BOM", node.data.value);
				node.data.image = escape(bom.image) || "";
				node.data.description = bom.description || "";
				node.data.item_code = bom.item || "";
			});
		}else if(node.is_root && node.data.value!="BOM"){
			frappe.model.with_doc("BOM", node.data.value, function() {
				var bom = frappe.model.get_doc("BOM", node.data.value);
				node.data.image = escape(bom.image) || "";
				node.data.description = bom.description || "";
				node.data.item_code = bom.item || "";
			});
		}
	},

	view_template: 'mapped_bom_item_preview'
}
