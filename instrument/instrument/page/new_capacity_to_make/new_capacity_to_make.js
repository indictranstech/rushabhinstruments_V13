// frappe.pages['new-capacity-to-make'].on_page_load = function(wrapper) {
// 	var page = frappe.ui.make_app_page({
// 		parent: wrapper,
// 		title: 'Capacity To Make',
// 		single_column: true
// 	});
// }


frappe.pages['new-capacity-to-make'].on_page_load = function(wrapper) {
	frappe.capacity_to_make_data = new frappe.capacity_to_make(wrapper);
}

frappe.capacity_to_make = Class.extend({
	init : function(wrapper){
		this.page = frappe.ui.make_app_page({
			parent: wrapper,
			title: 'Capacity To Make',
			single_column: true
		});
    	this.wrapper = wrapper
    	this.make()
		this.add_filters()
		this.add_menus(wrapper);
	},

	make: function() {
		var me = this;
		$(`<div class="frappe-list list-container"></div>`).appendTo(me.page.main);
	},
	add_menus:function(wrapper){
		var me = this
		var filters = {"production_item":me.production_item}
		wrapper.page.add_menu_item("Export",function(){
			if (me.production_item){
		    	me.export()
			}
		})
	},
	export:function(){
		var me = this
	    var filters = {"production_item":me.production_item}
	    frappe.call({
	        "method": "instrument.instrument.page.new_capacity_to_make.new_capacity_to_make.get_capacity_data",
	        args: {filters:filters},
	        callback: function (r) {
	        	if (r.message){
	          		data = r.message.data
	          		me.download_xlsx(data)
						          
	        	}

	        }//calback end
	    })

	},
	download_xlsx: function(data) {
		var me = this;
		return frappe.call({
			module:"instrument.instrument",
			page:"new_capacity_to_make",
			method: "make_xlsx_file",
			args: {renderd_data:data},
			callback: function(r) {
				var w = window.open(
				frappe.urllib.get_full_url(
				"/api/method/instrument.instrument.page.new_capacity_to_make.new_capacity_to_make.download_xlsx?"));

				if(!w)
					frappe.msgprint(__("Please enable pop-ups")); return;
			}
		})
	},
	get_data:function(){
		var me = this
	    $('.frappe-list').html("")
	    if(me.delivery_date){
	    	var filters = {"production_item":me.production_item
	    ,	"delivery_date":me.delivery_date}
		    frappe.call({
		        "method": "instrument.instrument.page.new_capacity_to_make.new_capacity_to_make.get_capacity_data",
		        args: {filters:filters},
		        freeze : true,
				freeze_message: __("Please wait..."),
		        callback: function (r) {
		        	if (r.message){
		          		var html = r.message.html
						$('.frappe-list').html(html)
							          
		        	}

		        }//calback end
		    })
	    }else{
	    	var filters = {"production_item":me.production_item}
	    	frappe.call({
	        "method": "instrument.instrument.page.new_capacity_to_make.new_capacity_to_make.get_capacity_data",
	        freeze : true,
			freeze_message: __("Loading..."),
	        args: {filters:filters},
	        callback: function (r) {
	        	if (r.message){
	          		var html = r.message.html
					$('.frappe-list').html(html)
						          
	        	}

	        }//calback end
	    })
	    }
	},
	add_filters:function(){
		var me = this;
		me.page.add_field({
			fieldtype: 'Link',
			label: __('Production Item'),
			fieldname: 'production_item',
			options: "Item",
			reqd:1,
			get_query: function(){ return {'filters': [['Item', 'item_group','in',['Product','Subassembly','Made in House']]]}},
			onchange: function() {
				me.production_item = this.value?this.value:null
				me.get_data()
				
			}

		})

		// const today = frappe.datetime.get_today();
		// me.page.add_field({
		// 	fieldtype: 'Date',
		// 	label: __('Expected Delivery Date'),
		// 	fieldname: 'delivery_date',
		// 	reqd : 0,
		// 	onchange: function() {
		// 		me.delivery_date = this.value?this.value:null
		// 		// var today = new Date();
		// 		// if(me.delivery_date <= today){
		// 		// 	frappe.throw("Expected Delivery Date Must be Greater Than Or Equal To Today")
		// 		// }
		// 		me.get_data()
		// 	}
		// })
		
  	}
})
