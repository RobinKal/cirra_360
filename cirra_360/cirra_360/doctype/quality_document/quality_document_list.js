frappe.listview_settings['Quality Document'] = {
	add_fields: ["quality_document_group", "status", "priority", "exp_start_date",
		"exp_end_date", "subject", "progress", "depends_on_quality_documents","quality_document_type_master"],
	filters: [["status", "=", "Open"]],
	onload: function(listview) {
		var method = "cirra_360.cirra_360.doctype.quality_document.quality_document.set_multiple_status";

		listview.page.add_menu_item(__("Set as Open"), function() {
			listview.call_for_selected_items(method, {"status": "Open"});
		});

		listview.page.add_menu_item(__("Set as Completed"), function() {
			listview.call_for_selected_items(method, {"status": "Completed"});
		});
		listview.filter_area.clear();
		listview.filter_area.add([[listview.doctype, "_assign", 'like',  '%' + frappe.session.user + '%']]);
		let actions_map = {
			"Tout": "All",
			"Brouillon": "Draft",
			"Vérification demandée": "To be verified",
			"Vérifié": "Verified",
			"Approbation demandée": "Verified",
			"Approuvé":"Approved"
		}
		$.each(actions_map, function(key, value) {
			listview.page.add_button(__(key), () => {
				listview.filter_area.clear();
				if (value != "All") {
					setTimeout(function() {
						listview.filter_area.add([[listview.doctype, "workflow_state", '=', value]]);
					},500);
				}
			}).addClass("btn-primary");
		})
	},
	// get_indicator: function(doc) {
	// 	var colors = {
	// 		"Open": "orange",
	// 		"Overdue": "red",
	// 		"Pending Review": "orange",
	// 		"Working": "orange",
	// 		"Completed": "green",
	// 		"Cancelled": "dark grey",
	// 		"Template": "blue"
	// 	}
	// 	return [__(doc.status), colors[doc.status], "status,=," + doc.status];
	// },
	get_indicator: function(doc) {
		var colors = {
			"Fiche d’enregistrement" : "blue",
			"Mode opératoire" :  "cyan",
			"Protocole" : "cyan",
			"Procédure" : "cyan",
			"Macro Processus" : "orange",
			"processus" : "pink",
			"sous processus" : "pink",
		}
		return [__(doc.quality_document_type_master), colors[doc.quality_document_type_master], "quality_document_type_master,=," + doc.quality_document_type_master];
	},
	// get_indicator: function(doc) {
	// 	return [__(doc.quality_document_type_master), {
	// 		"Mode opératoire" :  "cyan",
	// 		"Protocole" : "cyan",
	// 		"Procédure" : "cyan",
	// 		"Macro processus" : "pink",
	// 		"processus" : "pink",
	// 		"sous processus" : "pink",
	// 	}[doc.quality_document_type_master]];
	// },
	gantt_custom_popup_html: function(ganttobj, quality_document) {
		var html = `<h5><a style="text-decoration:underline"\
			href="/app/quality_document/${ganttobj.id}""> ${ganttobj.name} </a></h5>`;

		if(quality_document.quality_document_group) html += `<p>Quality Document: ${quality_document.quality_document_group}</p>`;
		html += `<p>Progress: ${ganttobj.progress}</p>`;

		if(quality_document._assign_list) {
			html += quality_document._assign_list.reduce(
				(html, user) => html + frappe.avatar(user)
			, '');
		}

		return html;
	}

};
