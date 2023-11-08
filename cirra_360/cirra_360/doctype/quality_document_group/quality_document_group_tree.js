
frappe.treeview_settings["Quality Document Group"] = {
	ignore_fields:["parent_quality_document_group"],
	get_tree_nodes: "cirra_360.cirra_360.doctype.quality_document_group.quality_document_group.get_children",
	add_tree_node: "cirra_360.cirra_360.doctype.quality_document_group.quality_document_group.add_node",
	filters: [
		{
			fieldname: "quality_document_group",
			fieldtype:"Link",
			options: "Quality Document Group",
			label: __("Quality Document Group"),
			get_query: function() {
				return {
					filters: [["Quality Document Group", 'is_group', '=', 1]]
				};
			}
		},
		{
			fieldname: "customer",
			fieldtype:"Link",
			options: "Customer",
			label: __("Customer")
		}
	],
	fields: [
		{fieldtype:'Data', fieldname: 'quality_document_group_name',
			label:__('New Quality Document Group Name'), reqd:true},
		{fieldtype:'Link', fieldname:'customer',
			label:__('Customer'), options:'Customer',
			description: __("Please enter Customer")},
		{fieldtype:'Check', fieldname:'is_group', label:__('Group Node'),
			description: __("Further nodes can be only created under 'Group' type nodes")}
	],
	breadcrumb: "cirra_360",
	root_label: "All Quality Document Groups",
	get_tree_root: false,
	menu_items: [
		{
			label: __("New Quality Document Group"),
			action: function() {
				frappe.new_doc("Quality Document Group", true);
			},
		}
	],
	onload: function(treeview) {
		treeview.make_tree();
	}
};
