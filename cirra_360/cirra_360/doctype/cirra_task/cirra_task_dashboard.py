from frappe import _
def get_data():
	return {
		'heatmap': True,
		'heatmap_message': _('This is about Cirra Task'),
		'transactions': [
			{
				'label': _('Action Plan and Event'),
				'items': ['Quality Action Plan', 'Client Event']
			}
			
		]
	}
