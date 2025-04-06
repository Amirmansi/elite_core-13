from __future__ import unicode_literals

import json
import frappe
from frappe import _
from frappe.utils import cint, floor, flt, today

@frappe.whitelist()
def get_price_list_rate_for(args, item_code):
	"""
		:param customer: link to Customer DocType
		:param supplier: link to Supplier DocType
		:param price_list: str (Standard Buying or Standard Selling)
		:param item_code: str, Item Doctype field item_code
		:param qty: Desired Qty
		:param transaction_date: Date of the price
	"""
	from six import string_types, iteritems
	if isinstance(args, string_types):
		args = json.loads(args)

	args = frappe._dict(args)

	item_price_args = {
			"item_code": item_code,
			"price_list": args.get('price_list'),
			"customer": args.get('customer'),
			"supplier": args.get('supplier'),
			"uom": args.get('uom'),
			"transaction_date": args.get('transaction_date'),
			"posting_date": args.get('posting_date'),
			"batch_no": args.get('batch_no'),
			"charactristics": args.get('charactristics')
	}

	item_price_data = 0
	price_list_rate = get_item_price(item_price_args, item_code)
	if price_list_rate:
		desired_qty = args.get("qty")
		if desired_qty and check_packing_list(price_list_rate[0][0], desired_qty, item_code):
			item_price_data = price_list_rate
	else:
		for field in ["customer", "supplier"]:
			del item_price_args[field]

		general_price_list_rate = get_item_price(item_price_args, item_code,
			ignore_party=args.get("ignore_party"))

		if not general_price_list_rate and args.get("uom") != args.get("stock_uom"):
			item_price_args["uom"] = args.get("stock_uom")
			general_price_list_rate = get_item_price(item_price_args, item_code, ignore_party=args.get("ignore_party"))

		if general_price_list_rate:
			item_price_data = general_price_list_rate

	if item_price_data:
		if item_price_data[0][2] == args.get("uom"):
			return item_price_data[0][1]
		elif not args.get('price_list_uom_dependant'):
			return flt(item_price_data[0][1] * flt(args.get("conversion_factor", 1)))
		else:
			return item_price_data[0][1]

def get_item_price(args, item_code, ignore_party=False):
	"""
		Get name, price_list_rate from Item Price based on conditions
			Check if the desired qty is within the increment of the packing list.
		:param args: dict (or frappe._dict) with mandatory fields price_list, uom
			optional fields transaction_date, customer, supplier
		:param item_code: str, Item Doctype field item_code
	"""

	args['item_code'] = item_code

	conditions = """where item_code=%(item_code)s
		and price_list=%(price_list)s
		and ifnull(uom, '') in ('', %(uom)s)"""

	conditions += "and ifnull(batch_no, '') in ('', %(batch_no)s)"

	if not ignore_party:
		if args.get("customer"):
			conditions += " and customer=%(customer)s"
		elif args.get("supplier"):
			conditions += " and supplier=%(supplier)s"
		else:
			conditions += "and (customer is null or customer = '') and (supplier is null or supplier = '')"
	if args.get("charactristics"):
		conditions += " and charactristics=%(charactristics)s"
	if not args.get("charactristics"):
		conditions += " and charactristics is null"
	if args.get('transaction_date'):
		conditions += """ and %(transaction_date)s between
			ifnull(valid_from, '2000-01-01') and ifnull(valid_upto, '2500-12-31')"""

	if args.get('posting_date'):
		conditions += """ and %(posting_date)s between
			ifnull(valid_from, '2000-01-01') and ifnull(valid_upto, '2500-12-31')"""

	return frappe.db.sql(""" select name, price_list_rate, uom
		from `tabItem Price` {conditions}
		order by valid_from desc, batch_no desc, uom desc """.format(conditions=conditions), args)


@frappe.whitelist()
def make_dox_sales_return(source_name, target_doc=None):
	source_doc = frappe.get_doc("Sales Invoice",source_name)
	from erpnext.controllers.sales_and_purchase_return import make_return_doc
	return make_return_doc("Sales Invoice", source_name, target_doc)


