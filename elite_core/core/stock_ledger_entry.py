from __future__ import unicode_literals

import json
import frappe
from frappe import _
from frappe.utils import cint, floor, flt, today

@frappe.whitelist()
def update_stock_ledger_entry_for_charactristics(self,method):
    if self.voucher_type == "Stock Entry":
        doctype = self.voucher_type + ' Detail'
    else:
        doctype = self.voucher_type + ' Item'
    if frappe.get_meta(doctype).has_field('charactristics'):
        charactristics_group = frappe.db.get_value(doctype,self.voucher_detail_no,"charactristics_group")
        charactristics = frappe.db.get_value(doctype,self.voucher_detail_no,"charactristics")
        validate_charactristics(self,charactristics_group,charactristics)
        if charactristics_group and charactristics:
            self.charactristics_group = charactristics_group
            self.charactristics = charactristics

def validate_charactristics(self,charactristics_group,charactristics):
    if self.item_code:
        has_charactristics = frappe.db.get_value("Item",self.item_code,"has_charactristics")
        if has_charactristics:
            if not charactristics_group or not charactristics:
                frappe.throw(_("Charactristics Is Mandatory For Item {0}").format(self.item_code))
