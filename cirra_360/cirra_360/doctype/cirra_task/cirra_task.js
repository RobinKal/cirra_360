// Copyright (c) 2022, sujay and contributors
// For license information, please see license.txt

frappe.ui.form.on('Cirra Task', {
	refresh: function (frm) {
		if (frm.doc.task_type == "Event") {
			if (frm.doc.status == "To be Analysed" || frm.doc.status == "Overdue") {
				frm.add_custom_button(__("Processing Report"), () => {
					frm.events.set_status(frm, "Processing Report");
				}, "Action");
			}
			if (frm.doc.status == "Processing Report" || frm.doc.status == "Overdue") {
				frm.add_custom_button(__("Transmitted to ASN"), () => {
					frm.events.set_status(frm, "Transmitted to ASN");
				}, "Action");
			}
		} else{
			if (frm.doc.status == "Not Started") {
				frm.add_custom_button(__("In Progress"), () => {
					frm.events.set_status(frm, "In Progress");
				}, "Action");
			}
			if (frm.doc.status == "In Progress") {
				frm.add_custom_button(__("Done"), () => {
					frm.events.set_status(frm, "Done");
				}, "Action");
			}
		}
		frm.set_query("client_event", function() {
			return { filters: { 'quality_action_plan': frm.doc.quality_action_plan } };
		});
	},
	set_status: function (frm, status) {
		frm.call({
			method: "set_status",
			doc: frm.doc,
			args: { 'status': status },
			callback: function (r) {
				frm.reload_doc();
			}
		})
	},
	download: function(frm,cdt,cdn) {
		frm.call({
			method:"download_file_data",
			doc:frm.doc,
			freeze:true,
			callback:function(r){
				if (r.message) {
					var file_url = r.message.replace(/#/g, '%23');
					window.open(file_url);
				}else{
					frappe.msgprint(__("Upload File In Cirra Setting."))
				}
			}
		})
	},
	submit_to: function(frm){
		// if(frm.doc.event_category == "Serious adverse event (EIG)") {
		// 	window.open('https://signalement.social-sante.gouv.fr/psig_ihm_utilisateurs/index.html#/choixSignalementPS', '_blank');
		// }
		// if(frm.doc.event_category == "Significant Radiation Protection Event (ESR)") {
		// 	window.open('https://teleservices.asn.fr', '_blank');
		// }
		frm.call({
			method:"submit_to",
			doc:frm.doc,
			freeze:true,
			callback:function(r){
				if (r.message) {
					window.open(r.message)
				}else{
					frappe.msgprint(__("Set Link In Cirra Setting."))
				}
			}
		})
	}
});
