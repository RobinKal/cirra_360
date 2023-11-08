// Copyright (c) 2022, sujay and contributors
// For license information, please see license.txt

frappe.ui.form.on('Client Event', {
	setup: function(frm) {
		frm.set_query("declaring_info_name",function(){
			return {
				filters:[["Cirra Customer","customers","=",frm.doc.customer]]
			}
		})
		frm.set_query("department",function(){
			return {
				filters:[["Department","is_cirra_department","=",1]]
			}
		})
	},
	refresh: function(frm) {
		if (frm.doc.status == "To Be Analysed") {
			console.log('asd')
			frm.add_custom_button(__('Processing Report'), function() {
				frm.call({
					method:"set_status",
					doc:frm.doc,
					args:{'status':'Processing Report'},
					callback:function(r){
						console.log(r)
						frm.reload_doc()
					}
				})
			})
		}
		if(!frm.doc.__islocal && frm.doc.status != "Completed") {
			frm.add_custom_button(__('Complete'), function() {
				frm.call({
					method:"set_status",
					doc:frm.doc,
					args:{'status':'Completed'},
					callback:function(r){
						frm.refresh()
					}
				})
			})
		}
		if(!frm.doc.__islocal) {
			if(frm.doc.type_of_event == "Significant"){
				frm.add_custom_button(__('Action Plan'), function() {
					frappe.set_route("Form","Quality Action Plan",frm.doc.quality_action_plan)
				})
			}
		}
	},
	asn_submit_button: function(frm) {
		frm.call({
			method:"set_status",
			doc:frm.doc,
			args:{'status':'Transmitted to ASN'},
			callback:function(r){
				frm.reload_doc()
			}
		})
	}
});



frappe.ui.form.on('Client Event', {
	setup: function(frm) {
		frm.set_query("physician", function() {
			return {
				filters: [
					["Employee","designation", '=', "physician"]
				]
			}
		});
	}
});

