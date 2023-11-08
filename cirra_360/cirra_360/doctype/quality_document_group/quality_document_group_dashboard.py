
from frappe import _


def get_data():
	return {
		'heatmap': True,
		'heatmap_message': _('This is based on the  quality_document'),
		'fieldname': 'quality_document_group',
		'transactions': [
			{
				'label': _('Quality Document Group'),
				'items': ['Quality Document']
			}
			
		]
	}
