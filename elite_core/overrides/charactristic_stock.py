import json
import os

import frappe
from frappe import _
from frappe.utils import cint, floor, flt, today
from six import iteritems

def custom_get_bin(item_code, warehouse,char_group=None,char_value=None):
	filters = {
		"item_code": item_code,
		"warehouse": warehouse,
	}
	if char_group and char_value:
		filters["for_charactristic"] = 1
		filters["charactristics_group"] = char_group
		filters["charactristics"] = char_value
	else:
		filters["for_charactristic"] = 0
	bin = frappe.db.get_value("Bin", filters)
	if not bin:
		bin_obj = frappe.get_doc({
			"doctype": "Bin",
			"item_code": item_code,
			"warehouse": warehouse,
		})
		if char_group and char_value:
			bin_obj.for_charactristic = 1
			bin_obj.charactristics_group = char_group
			bin_obj.charactristics = char_value
		bin_obj.flags.ignore_permissions = 1
		bin_obj.insert()
	else:
		bin_obj = frappe.get_doc('Bin', bin, for_update=True)
	bin_obj.flags.ignore_permissions = True
	return bin_obj

def custom_update_bin(self):
	# update bin for each warehouse
	for warehouse, data in iteritems(self.data):
		char_group = frappe.db.get_value("Stock Ledger Entry",self.args.sle_id,"charactristics_group")
		char_val = frappe.db.get_value("Stock Ledger Entry",self.args.sle_id,"charactristics")
		bin_doc = custom_get_bin(self.item_code, warehouse,char_group,char_val)
		bin_doc.update({
			"valuation_rate": data.valuation_rate,
			"actual_qty": data.qty_after_transaction,
			"stock_value": data.stock_value
		})
		bin_doc.flags.via_stock_ledger_entry = True
		bin_doc.save(ignore_permissions=True)
	
def custom_get_previous_sle_of_current_voucher(args, exclude_current_voucher=False):
	from erpnext.stock import stock_ledger
	"""get stock ledger entries filtered by specific posting datetime conditions"""

	args['time_format'] = '%H:%i:%s'
	if not args.get("posting_date"):
		args["posting_date"] = "1900-01-01"
	if not args.get("posting_time"):
		args["posting_time"] = "00:00"
	char_group = frappe.db.get_value("Stock Ledger Entry",args.get('sle_id'),"charactristics_group")
	char_val = frappe.db.get_value("Stock Ledger Entry",args.get('sle_id'),"charactristics")
	voucher_condition = ""
	if exclude_current_voucher:
		voucher_no = args.get("voucher_no")
		voucher_condition = f"and voucher_no != '{voucher_no}'"
	if char_group and char_val:
		voucher_condition = f"and charactristics_group = '{char_group}' and charactristics = '{char_val}'"
	sle = frappe.db.sql("""
		select *, timestamp(posting_date, posting_time) as "timestamp"
		from `tabStock Ledger Entry`
		where item_code = %(item_code)s
			and warehouse = %(warehouse)s
			and is_cancelled = 0
			{voucher_condition}
			and timestamp(posting_date, time_format(posting_time, %(time_format)s)) < timestamp(%(posting_date)s, time_format(%(posting_time)s, %(time_format)s))
		order by timestamp(posting_date, posting_time) desc, creation desc
		limit 1
		for update""".format(voucher_condition=voucher_condition), args, as_dict=1)

	return sle[0] if sle else frappe._dict()
		