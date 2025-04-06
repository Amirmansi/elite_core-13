import frappe
from erpnext.portal.doctype.homepage.homepage import Homepage


class CustomHomepage(Homepage):
	def validate(self):
		if not self.description:
			self.description = frappe._("This is an example website auto-generated from DoxERP")
		return super().validate()
