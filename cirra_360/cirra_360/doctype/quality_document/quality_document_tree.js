frappe.provide("frappe.treeview_settings");

frappe.treeview_settings['Quality Document'] = {
	get_tree_nodes: "cirra_360.cirra_360.doctype.quality_document.quality_document.get_children",
	add_tree_node: "cirra_360.cirra_360.doctype.quality_document.quality_document.add_node",
	filters: [
		{
			fieldname: "quality_document_group",
			fieldtype:"Link",
			options: "Quality Document Group",
			label: __("Quality Document Group"),
		},
		{
			fieldname: "quality_document",
			fieldtype:"Link",
			options: "Quality Document",
			label: __("Quality Document"),
			get_query: function() {
				var me = frappe.treeview_settings['Quality Document'];
				var quality_document_group = me.page.fields_dict.quality_document_group.get_value();
				var args = [["Quality Document", 'is_group', '=', 1]];
				if(quality_document_group){
					args.push(["Quality Document", 'quality_document', "=", quality_document]);
				}
				return {
					filters: args
				};
			}
		}
	],
	breadcrumb: "cirra_360",
	get_tree_root: false,
	root_label: "All Quality Documents",
	ignore_fields: ["parent_quality_document"],
	onload: function(me) {
		console.log(frappe)
		frappe.treeview_settings['Quality Document'].page = {};
		$.extend(frappe.treeview_settings['Quality Document'].page, me.page);
		me.make_tree();
	},
	toolbar: [
		{
			label:__("Add Multiple"),
			condition: function(node) {
				return node.expandable;
			},
			click: function(node) {
				this.data = [];
				const dialog = new frappe.ui.Dialog({
					title: __("Add Multiple Quality Documents"),
					fields: [
						{
							fieldname: "multiple_quality_documents", fieldtype: "Table",
							in_place_edit: true, data: this.data,
							get_data: () => {
								return this.data;
							},
							fields: [{
								fieldtype:'Data',
								fieldname:"subject",
								in_list_view: 1,
								reqd: 1,
								label: __("Subject")
							}]
						},
					],
					primary_action: function() {
						dialog.hide();
						return frappe.call({
							method: "cirra_360.cirra_360.doctype.quality_document.quality_document.add_multiple_quality_documents",
							args: {
								data: dialog.get_values()["multiple_quality_documents"],
								parent: node.data.value
							},
							callback: function() { }
						});
					},
					primary_action_label: __('Create')
				});
				dialog.show();
			}
		}
	],
	extend_toolbar: true,
	onrender: function(node) {
		console.log(node.data)
		if (node.data && node.data.status!==undefined) {
			$('<span class="balance-area pull-right">'
			+ node.data.status	
			+ '</span>').insertBefore(node.$ul);
		}
	}
};
