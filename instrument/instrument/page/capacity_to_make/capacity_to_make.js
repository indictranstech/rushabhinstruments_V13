frappe.pages['capacity_to_make'].on_page_load = function(wrapper) {
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
		// this.add_menus(wrapper);
	},

	make: function() {
		var me = this;
		$(`<div class="frappe-list list-container"></div>`).appendTo(me.page.main);
	},
	get_data:function(){
		var me = this
	    $('.frappe-list').html("")
	    var filters = {"production_item":me.production_item
	    ,"delivery_date":me.delivery_date}
	    frappe.call({
	        "method": "instrument.instrument.page.capacity_to_make.capacity_to_make.get_capacity_data",
	        args: {filters:filters},
	        callback: function (r) {
	        	if (r.message){
	          		var html = r.message.html
					$('.frappe-list').html(html)
						          
	        	}

	        }//calback end
	    })

	},
	add_filters:function(){
		var me = this;
		me.page.add_field({
			fieldtype: 'Link',
			label: __('Production Item'),
			fieldname: 'production_item',
			options: "Item",
			reqd:1,
			onchange: function() {
				me.production_item = this.value?this.value:null
				
			}

		})

		const today = frappe.datetime.get_today();
		me.page.add_field({
			fieldtype: 'Date',
			label: __('Expected Delivery Date'),
			fieldname: 'delivery_date',
			reqd : 1,
			onchange: function() {
				me.delivery_date = this.value?this.value:null
				// var today = new Date();
				// if(me.delivery_date <= today){
				// 	frappe.throw("Expected Delivery Date Must be Greater Than Or Equal To Today")
				// }
				me.get_data()
			}
		})
		
  	}
})
