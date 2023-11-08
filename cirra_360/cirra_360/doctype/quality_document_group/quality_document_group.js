// Copyright (c) 2021, sujay and contributors
// For license information, please see license.txt


frappe.ui.form.on("Quality Document Group", {
	setup(frm) {
		frm.make_methods = {
			'Timesheet': () => {
				open_form(frm, "Timesheet", "Timesheet Detail", "time_logs");
			},
			'Purchase Order': () => {
				open_form(frm, "Purchase Order", "Purchase Order Item", "items");
			},
			'Purchase Receipt': () => {
				open_form(frm, "Purchase Receipt", "Purchase Receipt Item", "items");
			},
			'Purchase Invoice': () => {
				open_form(frm, "Purchase Invoice", "Purchase Invoice Item", "items");
			},
		};
	},
	onload: function (frm) {
		const so = frm.get_docfield("sales_order");
		so.get_route_options_for_new_doc = () => {
			if (frm.is_new()) return;
			return {
				"customer": frm.doc.customer,
				"quality_document_group_name": frm.doc.name
			};
		};

		frm.set_query('customer', 'erpnext.controllers.queries.customer_query');

		frm.set_query("user", "users", function () {
			return {
				query: "cirra_360.cirra_360.doctype.quality_document_group.quality_document_group.get_users_for_quality_document_group"
			};
		});

		// sales order
		frm.set_query('sales_order', function () {
			var filters = {
				'quality_document_group': ["in", frm.doc.__islocal ? [""] : [frm.doc.name, ""]]
			};

			if (frm.doc.customer) {
				filters["customer"] = frm.doc.customer;
			}

			return {
				filters: filters
			};
		});
	},

	refresh: function (frm) {
		if (frm.doc.__islocal) {
			frm.web_link && frm.web_link.remove();
		} else {
			frm.add_web_link("/cirra_360?quality_document_group=" + encodeURIComponent(frm.doc.name));

			frm.trigger('show_dashboard');
		}
		frm.events.set_buttons(frm);
	},

	set_buttons: function(frm) {
		if (!frm.is_new()) {
			frm.add_custom_button(__('Duplicate Quality Document Group with Quality Documents'), () => {
				frm.events.create_duplicate(frm);
			},__('More Action'));

			frm.add_custom_button(__('Completed'), () => {
				frm.events.set_status(frm, 'Completed');
			}, __('Set Status'));

			frm.add_custom_button(__('Cancelled'), () => {
				frm.events.set_status(frm, 'Cancelled');
			}, __('Set Status'));


			if (frappe.model.can_read("Quality Document")) {
				frm.add_custom_button(__("Gantt Chart"), function () {
					frappe.route_options = {
						"quality_document_group": frm.doc.name
					};
					frappe.set_route("List", "Quality Document", "Gantt");
				},__('More Action'));

				frm.add_custom_button(__("Kanban Board"), () => {
					frappe.call('cirra_360.cirra_360.doctype.quality_document_group.quality_document_group.create_kanban_board_if_not_exists', {
						quality_document_group: frm.doc.name
					}).then(() => {
						frappe.set_route('List', 'Quality Document', 'Kanban', frm.doc.quality_document_group_name);
					});
				},__('More Action'));
			}
		}


	},

	create_duplicate: function(frm) {
		return new Promise(resolve => {
			frappe.prompt('Quality Document Group Name', (data) => {
				frappe.xcall('cirra_360.cirra_360.doctype.quality_document_group.quality_document_group.create_duplicate_quality_document_group',
					{
						prev_doc: frm.doc,
						quality_document_group_name: data.value
					}).then(() => {
					frappe.set_route('Form', "Quality Document Group", data.value);
					frappe.show_alert(__("Duplicate Quality Document Group has been created"));
				});
				resolve();
			});
		});
	},

	set_status: function(frm, status) {
		frappe.confirm(__('Set Quality Document Group and all Quality Document to status {0}?', [status.bold()]), () => {
			frappe.xcall('cirra_360.cirra_360.doctype.quality_document_group.quality_document_group.set_quality_document_group_status',
				{quality_document_group: frm.doc.name, status: status}).then(() => { /* page will auto reload */ });
		});
	},

});

function open_form(frm, doctype, child_doctype, parentfield) {
	frappe.model.with_doctype(doctype, () => {
		let new_doc = frappe.model.get_new_doc(doctype);

		// add a new row and set the quality_document_group
		let new_child_doc = frappe.model.get_new_doc(child_doctype);
		new_child_doc.quality_document_group = frm.doc.name;
		new_child_doc.parent = new_doc.name;
		new_child_doc.parentfield = parentfield;
		new_child_doc.parenttype = doctype;
		new_doc[parentfield] = [new_child_doc];

		frappe.ui.form.make_quick_entry(doctype, null, null, new_doc);
	});

}

cur_frm.fields_dict['user_details'].grid.get_field('user').get_query = function(doc, cdt, cdn) {
	var d  = locals[cdt][cdn];
	return {
		query: 'cirra_360.cirra_360.doctype.quality_document_group.quality_document_group.get_user_query',
		filters: {
			customer: cur_frm.doc.customer
		}
	};
}

cur_frm.fields_dict['user_details'].grid.get_field('role').get_query = function(doc, cdt, cdn) {
	var d  = locals[cdt][cdn];
	return {
		query: 'cirra_360.cirra_360.doctype.quality_document_group.quality_document_group.get_user_role',
		filters: {
			user: d.user
		}
	};
}
