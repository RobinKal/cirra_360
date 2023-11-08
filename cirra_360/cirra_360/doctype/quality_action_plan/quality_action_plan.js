// Copyright (c) 2022, sujay and contributors
// For license information, please see license.txt

frappe.ui.form.on('Quality Action Plan', {
	refresh: function(frm) {
		$('[data-doctype="Client Event"]').find("button").hide();
		if(!frm.doc.__islocal && frm.doc.status != "Completed"){
			(frm.get_field("status").df.options.split("\n") || []).forEach(status => {			
				frm.add_custom_button(__(status),function(){
					frm.call({
						method:"set_status",
						doc:frm.doc,
						args:{"status":status},
						freeze:true,
						async:false,
						callback:function(r){
							frm.reload_doc()
						}
					})
				},__("Action"))
			});
		}
		// frm.add_custom_button(_("Ready For Meeting"),function(){

		// },__("Action"))
		// frm.add_custom_button(_("Action Plan Ongoing"),function(){

		// },__("Action"))
		// frm.add_custom_button(_("Completed"),function(){

		// },__("Action"))
		// frm.add_custom_button(_("Cancelled"),function(){

		// },__("Action"))
	}
});
