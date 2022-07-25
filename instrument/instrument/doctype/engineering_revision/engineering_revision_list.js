frappe.listview_settings['Engineering Revision'] = {
	onload:function(listview){
		var old_link = window.location.href
		if (old_link.includes("Default")){
			var split_data = old_link.split("?")
			var item_code = split_data[1].split("_")[0]
			if (split_data[1].split("_")[1]=="Default"){
				frappe.db.get_value("Engineering Revision", {"item_code":item_code, "is_default":1, "is_active":1}, "name", (r) => {
					var link =  split_data[0]+r.name
					window.open(link, "_self");
				});
			}
		}
	}
};