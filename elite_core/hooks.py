from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "elite_core"
app_title = "Elite Core"
app_publisher = "Elite Business"
app_description = "Frappe Framework extensions by Elite Business"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "support@doxerp.com"
app_license = "MIT"
app_logo_url = '/assets/elite_core/images/dox_erp.png'

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
app_include_css = [
	"/assets/elite_core/css/elite_core.css",
	"/assets/css-rtl/elite_core.css",
	"https://fonts.googleapis.com/icon?family=Material+Icons&display=block",
]
app_include_js = [
	"/assets/elite_core/js/elite_core.js"
]

# include js, css files in header of web template
web_include_css = "/assets/elite_core/css/elite_core_web.css"
fixtures = ["Custom Field","Property Setter"]
# web_include_js = "/assets/elite_core/js/elite_core.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "elite_core/public/scss/website"

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
website_context = {
	"favicon": "/assets/elite_core/images/dox_login.png",
	"splash_image": "/assets/elite_core/images/dox_login.png"
}

after_migrate = [
	'elite_core.api.elite_core_patch',
	'elite_core.api.delete_language_after_migrate'
]

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "elite_core.install.before_install"
#after_install = "elite_core.api.add_translation"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "elite_core.notifications.get_notification_config"

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
# 	"Homepage": "elitecore.overrides.homepage.CustomHomepage"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Stock Ledger Entry": {
		"before_insert": "elite_core.core.stock_ledger_entry.update_stock_ledger_entry_for_charactristics"
	},
	"*": {
		"before_insert": "elite_core.core.naming.set_naming_series"
	}
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"elite_core.tasks.all"
# 	],
# 	"daily": [
# 		"elite_core.tasks.daily"
# 	],
# 	"hourly": [
# 		"elite_core.tasks.hourly"
# 	],
# 	"weekly": [
# 		"elite_core.tasks.weekly"
# 	]
# 	"monthly": [
# 		"elite_core.tasks.monthly"
# 	]
# }

boot_session = "elite_core.api.boot_session"
# Testing
# -------

# before_tests = "elite_core.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "elite_core.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "elite_core.task.get_dashboard_data"
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
# 	"elite_core.auth.validate"
# ]

override_whitelisted_methods = {
	"frappe.utils.change_log.show_update_popup": "elite_core.api.ignore_update_popup"
}
