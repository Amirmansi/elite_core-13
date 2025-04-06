import frappe

@frappe.whitelist()
def get_options(doctype):
	if frappe.get_meta(doctype).get_field("naming_series"):
		return frappe.get_meta(doctype).get_field("naming_series").options.split('\n')

def set_naming_series(self,method):
    if self.doctype in ["Sales Invoice","Sales Order","Purchase Invoice","Purchase Order","Quotation","Payment Entry","Delivery Note"]:
        meta = frappe.get_meta('Company')
        for field in meta.get_table_fields():
            if field.fieldname == 'naming_series_company':
                series = get_naming_series(self)
                if series:
                    self.naming_series = series
                break

def get_naming_series(self):
    condition = ""
    condition += " ref_doctype='{0}'".format(self.doctype)
    condition += " and parent='{0}'".format(self.company)
    if self.doctype in ["Sales Invoice","Purchase Invoice","Delivery Note"]:
        if self.is_return == 1:
            condition += " and for_return=1"
    series = frappe.db.sql("""select series from `tabNaming Series Company` where {0}""".format(condition),as_dict=1,debug=1)
    if len(series) >= 1:
        return series[0].series
    else:
        return False

