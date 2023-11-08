// Copyright (c) 2021, sujay and contributors
// For license information, please see license.txt



frappe.ui.form.on("Quality Document", {
	refresh: function(frm) {
		console.log('asd')
		frm.add_custom_button(__("Generate PDF"), function() {
			frappe.call({
				method:"cirra_360.utils.attach_pdf.attach_pdf",
				args:{'doc_name':frm.doc.name},
				freeze:true,
				freeze_message:"Generating PDF...",
				async:false,
				callback:function(r){
					frm.reload_doc()
				}
			})
		})
			// frappe.call({
			// 	method:"cirra_360.utils.attach_pdf.get_attach_quality_document",
			// 	args:{'doc_name':frm.doc.name},
			// 	callback:function(r){
			// 		frm.set_df_property('quality_document_attachment', 'options', [''].concat(r.message));
			// 		frm.refresh()
			// 	}
			// })
			
	},
	setup:function(frm,cdt,cdn) {
		var doc = locals[cdt][cdn];
		frm.set_query("quality_document_attachment", function() {
			return { filters: { attached_to_doctype: "Quality Document",attached_to_name: doc.name} };
		});
		
		frm.set_query("quality_document_group", function() {
			return {
				filters:[
					["Quality User","user","=",frappe.session.user]
				]
			};
		});
		// frm.set_query("quality_document_group", function() {
		// 	return {
		// 		query: 'cirra_360.cirra_360.doctype.quality_document.quality_document.get_quality_document_group'
		// 	};
		// });
	},
	quality_document_attachment: function(frm,cdt,cdn) {
		var doc = locals[cdt][cdn];
		if(doc.quality_document_attachment){
			frappe.call({
				method:"cirra_360.utils.attach_pdf.get_file_url",
				args:{'file_name':frm.doc.quality_document_attachment},
				callback:function(r){
					var wrapper = frm.get_field("preview_pdf").$wrapper;
					var file_url = r.message;
					if (doc.quality_document_attachment) {
						file_url = file_url.replace(/#/g, '%23');
						console.log(file_url)
						wrapper.html('<embed src="'+file_url+'#toolbar=0&zoom=80" width=100% height=600px>')
					}
				}
			})
		}

	},
	onload: function (frm) {

		frm.set_query("quality_document", "depends_on", function () {
			let filters = {
				name: ["!=", frm.doc.name]
			};
			if (frm.doc.quality_document_group) filters["quality_document_group"] = frm.doc.quality_document_group;
			return {
				filters: filters
			};
		})

		frm.set_query("parent_quality_document", function () {
			let filters = {
				"is_group": 1,
				"name": ["!=", frm.doc.name]
			};
			if (frm.doc.quality_document_group) filters["quality_document_group"] = frm.doc.quality_document_group;
			return {
				filters: filters
			}
		});
	},

	is_group: function (frm) {
		frappe.call({
			method: "cirra_360.cirra_360.doctype.quality_document.quality_document.check_if_child_exists",
			args: {
				name: frm.doc.name
			},
			callback: function (r) {
				if (r.message.length > 0) {
					let message = __('Cannot convert Task to non-group because the following child Quality Documents exist: {0}.',
						[r.message.join(", ")]
					);
					frappe.msgprint(message);
					frm.reload_doc();
				}
			}
		})
	},

	validate: function (frm) {
		frm.doc.quality_document_group && frappe.model.remove_from_locals("Quality Document Group",
			frm.doc.quality_document_group);
	}
});
