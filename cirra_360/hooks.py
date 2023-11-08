from . import __version__ as app_version

app_name = "cirra_360"
app_title = "cirra_360"
app_publisher = "sujay"
app_description = "cirra_360"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "sujay.j@tacten.co"
app_license = "MIT"
app_logo_url = '/assets/cirra_360/images/Cirralogo.png'




fixtures = ["Client Script",
    {
        "dt": "Custom Field",
        "filters": [
            ["name", "in", [
				#Customer
				'Customer-employee_details',
				'Customer-user_creation_info',
				#Employee
				'Employee-customer',
                'Employee-is_cirra_employee',
                #Department
                'Department-is_cirra_department',
                #Client Event
                'Client Event-immediate_corrective_action',
                #Quality Document
                'Quality Document-workflow_state'				
				
            ]]
        ]
    },
    {
        "dt": "Role",
        "filters": [
            ["name", "in", [
                "Approver","Creator","Verifier","Quality Consultant","Technician","Radiologist","Medical assistant","quality leader",
            ]]
        ]
    },
    {
        "dt": "Workflow State",
        "filters": [
            ["name", "in", [
                "Being Updated","Minor Edit","Verified","To be verified","In Progress","In-Progress","Draft","Outdated"
            ]]
        ]
    },
    {
        "dt": "Workflow Action Master",
        "filters": [
            ["name", "in", [
                "Minor Edit","Update"
            ]]
        ]
    },
    {
        "dt": "Print Format",
        "filters": [
            ["name", "in", [
                "Cirra Quality Document"
            ]]
        ]
    },
    {
        "dt": "Workflow",
        "filters": [
            ["name", "in", [
                "Quality Document -QD"
            ]]
        ]
    },
    {
        "dt": "Property Setter",
        "filters": [
            ["name", "in", [
                'Employee-erpnext_user-label',
                'Cirra Task-task_name-in_list_view',
                'Client Event-event_name-in_list_view',
                'Quality Document-main-default_print_format',
                'Client Event-crex_meeting-in_list_view',
                'Client Event-type_of_event-in_list_view',
                'Client Event-status-in_list_view',
                'Workspace Chart-chart_name-label',
                'Quality Document-subject-in_list_view',
                'Healthcare Service Unit-service_unit_type-depends_on',
                'Quality Document-naming_series-options',
                'Quality Document-main-track_views',
                'Quality Document-project-label',
                'Quality Document-project-hidden',
                'File-main-track_views',
                'Customer-naming_series-hidden',
                'Customer-naming_series-reqd',
                'Employee-employee_number-hidden',
                'Employee-employee_number-reqd',
                'Employee-naming_series-reqd',
                'Employee-naming_series-hidden',


			]]
        ]
    },
    {
        "dt": "Translation",
        "filters": [
            ["name", "in", [
                "3484bb05cb"
            ]]
        ]     
    }
]


# Includes in <head>
# ------------------

# include js, css files in header of desk.html
app_include_css = "/assets/cirra_360/css/cirra_360.css"
# app_include_js = "/assets/cirra_360/js/cirra_360.js"

# include js, css files in header of web template
# web_include_css = "/assets/cirra_360/css/cirra_360.css"
# web_include_js = "/assets/cirra_360/js/cirra_360.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "cirra_360/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "cirra_360.install.before_install"
# after_install = "cirra_360.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "cirra_360.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	# "Customer": {
	# 	"on_update": "cirra_360.events.customer.on_customer_on_save"
	# },
	"Employee": {
		"on_update": "cirra_360.events.employee.on_update_employee"
	}
}

# Scheduled Tasks
# ---------------

scheduler_events = {
	"hourly": [
		"cirra_360.cirra_360.doctype.cirra_task.cirra_task.update_action_hours_cron"
	],
	"daily": [
		"cirra_360.cirra_360.doctype.cirra_task.cirra_task.update_action_daily_cron",
        "cirra_360.cirra_360.doctype.quality_document.quality_document.update_outdate_for_approved_quality_document"
	]
}

# Testing
# -------

# before_tests = "cirra_360.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "cirra_360.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "cirra_360.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]


# User Data Protection
# --------------------

user_data_fields = [
	{
		"doctype": "{doctype_1}",
		"filter_by": "{filter_by}",
		"redact_fields": ["{field_1}", "{field_2}"],
		"partial": 1,
	},
	{
		"doctype": "{doctype_2}",
		"filter_by": "{filter_by}",
		"partial": 1,
	},
	{
		"doctype": "{doctype_3}",
		"strict": False,
	},
	{
		"doctype": "{doctype_4}"
	}
]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"cirra_360.auth.validate"
# ]

website_context = {
	"favicon": "/assets/cirra_360/images/Cirralogo1.png",
	"splash_image": "/assets/cirra_360/images/Cirralogo.png"
}
