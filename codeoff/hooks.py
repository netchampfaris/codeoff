app_name = "codeoff"
app_title = "Code Off"
app_publisher = "Frappe"
app_description = "Leetcode style live contests"
app_email = "faris@frappe.io"
app_license = "agpl-3.0"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "codeoff",
# 		"logo": "/assets/codeoff/logo.png",
# 		"title": "Code Off",
# 		"route": "/codeoff",
# 		"has_permission": "codeoff.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/codeoff/css/codeoff.css"
# app_include_js = "/assets/codeoff/js/codeoff.js"

# include js, css files in header of web template
# web_include_css = "/assets/codeoff/css/codeoff.css"
# web_include_js = "/assets/codeoff/js/codeoff.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "codeoff/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
	"Codeoff Match": "public/js/codeoff_match.js",
	"Codeoff Tournament": "public/js/codeoff_tournament.js",
}
doctype_list_js = {"Codeoff Problem": "public/js/codeoff_problem_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "codeoff/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# automatically load and sync documents of this doctype from downstream apps
# importable_doctypes = [doctype_1]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "codeoff.utils.jinja_methods",
# 	"filters": "codeoff.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "codeoff.install.before_install"
# after_install = "codeoff.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "codeoff.uninstall.before_uninstall"
# after_uninstall = "codeoff.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "codeoff.utils.before_app_install"
# after_app_install = "codeoff.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "codeoff.utils.before_app_uninstall"
# after_app_uninstall = "codeoff.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "codeoff.notifications.get_notification_config"

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

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"codeoff.tasks.all"
# 	],
# 	"daily": [
# 		"codeoff.tasks.daily"
# 	],
# 	"hourly": [
# 		"codeoff.tasks.hourly"
# 	],
# 	"weekly": [
# 		"codeoff.tasks.weekly"
# 	],
# 	"monthly": [
# 		"codeoff.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "codeoff.install.before_tests"

# Extend DocType Class
# ------------------------------
#
# Specify custom mixins to extend the standard doctype controller.
# extend_doctype_class = {
# 	"Task": "codeoff.custom.task.CustomTaskMixin"
# }

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "codeoff.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "codeoff.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["codeoff.utils.before_request"]
# after_request = ["codeoff.utils.after_request"]

# Job Events
# ----------
# before_job = ["codeoff.utils.before_job"]
# after_job = ["codeoff.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"codeoff.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
export_python_type_annotations = True

# Require all whitelisted methods to have type annotations
require_type_annotated_api_methods = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []


website_route_rules = [
	{"from_route": "/codeoff/<path:app_path>", "to_route": "codeoff"},
]

website_redirects = [
	{"source": "/", "target": "/codeoff"},
]
