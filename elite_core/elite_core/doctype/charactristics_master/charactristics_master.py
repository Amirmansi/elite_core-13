# Copyright (c) 2021, Elite Business and contributors
# For license information, please see license.txt

import frappe
from frappe import _, scrub
from frappe.custom.doctype.custom_field.custom_field import create_custom_field
from frappe.model import core_doctypes_list
from frappe.model.document import Document
from frappe.utils import cstr

class CharactristicsMaster(Document):
	def before_insert(self):
		self.set_fieldname_and_label()
		make_dimension_in_accounting_doctypes(self)

	def set_fieldname_and_label(self):
		self.fieldname = scrub(self.charactristics_name)

	def on_trash(self):
		delete_accounting_dimension(doc=self)


def make_dimension_in_accounting_doctypes(doc, doclist=None):
	if not doclist:
		doclist = ["Sales Invoice Item","Delivery Note Item","Purchase Invoice Item","Purchase Receipt Item","Stock Entry Detail","Stock Ledger Entry"]

	doc_count = len(get_stock_dimensions())
	count = 0

	for doctype in doclist:

		if (doc_count + 1) % 2 == 0:
			insert_after_field = 'stock_dimensions_section'
		else:
			insert_after_field = 'stock_dimension_col_break'

		df = {
			"fieldname": doc.fieldname,
			"label": doc.charactristics_name,
			"fieldtype": "Link",
			"options": doc.reference_document_type,
			"insert_after": insert_after_field,
			"owner": "Administrator"
		}

		meta = frappe.get_meta(doctype, cached=False)
		fieldnames = [d.fieldname for d in meta.get("fields")]

		if df['fieldname'] not in fieldnames:
				create_custom_field(doctype, df)

		count += 1

		frappe.publish_progress(count*100/len(doclist), title = _("Creating Fields..."))
		frappe.clear_cache(doctype=doctype)

def get_stock_dimensions():
	return frappe.get_all("Charactristics Master",filters={},fields=["name"])

def delete_accounting_dimension(doc):
	doclist = ["Sales Invoice Doctype","Delivery Note Item","Purchase Invoice Item","Purchase Receipt Item","Stock Entry Detail","Stock Ledger Entry"]

	frappe.db.sql("""
		DELETE FROM `tabCustom Field`
		WHERE fieldname = %s
		AND dt IN (%s)""" %			#nosec
		('%s', ', '.join(['%s']* len(doclist))), tuple([doc.fieldname] + doclist))

	frappe.db.sql("""
		DELETE FROM `tabProperty Setter`
		WHERE field_name = %s
		AND doc_type IN (%s)""" %		#nosec
		('%s', ', '.join(['%s']* len(doclist))), tuple([doc.fieldname] + doclist))

	for doctype in doclist:
		frappe.clear_cache(doctype=doctype)