import frappe
from frappe import _


@frappe.whitelist()
def get_csrf_token():
	if frappe.get_conf().get("staging_mode"):
		return frappe.local.session.data.csrf_token
	else:
		frappe.throw(_("Not Allowed"), exc=frappe.PermissionError)
