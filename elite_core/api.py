# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import csv
import json
import os

import frappe
from frappe import _
from frappe.utils import cint, floor, flt, today


def elite_core_patch():
	# update app name
	update_app_name()
	# delete erpnext welcome page
	frappe.delete_doc_if_exists("Page", "welcome-to-erpnext", force=1)
	# update Welcome Blog Post
	if frappe.db.exists("Blog Post", "Welcome"):
		frappe.db.set_value("Blog Post", "Welcome", "content", "")
	update_field_label()
	# if cint(get_frappe_version()) >= 13 and not frappe.get_conf().get(
	# 	"ignore_onboard_elite_core"
	# ):
	update_onboard_details()
	create_default_data()


def update_field_label():
	"""Update label of section break in employee doctype"""
	frappe.db.sql(
		"""Update `tabDocField` set label='ERP' where fieldname='erpnext_user' and parent='Employee'"""
	)


def get_frappe_version():
	return frappe.db.get_value(
		"Installed Application", {"app_name": "frappe"}, "app_version"
	).split(".")[0]


def update_onboard_details():
	update_onboard_module()
	update_onborad_steps()


def update_onboard_module():
	onboard_module_details = frappe.get_all(
		"Module Onboarding", filters={}, fields=["name"]
	)
	for row in onboard_module_details:
		doc = frappe.get_doc("Module Onboarding", row.name)
		doc.documentation_url = ""
		doc.flags.ignore_mandatory = True
		doc.save(ignore_permissions=True)


def update_onborad_steps():
	onboard_steps_details = frappe.get_all(
		"Onboarding Step", filters={}, fields=["name"]
	)
	for row in onboard_steps_details:
		doc = frappe.get_doc("Onboarding Step", row.name)
		doc.intro_video_url = ""
		doc.video_url = ""
		doc.description = ""
		doc.flags.ignore_mandatory = True
		doc.save(ignore_permissions=True)


def boot_session(bootinfo):
	"""boot session - send website info if guest"""
	if frappe.session["user"] != "Guest":

		bootinfo.elite_core = frappe.get_conf().get("elite_core", {})
		bootinfo['change_log'] = []

@frappe.whitelist()
def ignore_update_popup():
	if not frappe.get_conf().get("disable_new_update_popup"):
		show_update_popup_update()


@frappe.whitelist()
def show_update_popup_update():
	cache = frappe.cache()
	user = frappe.session.user
	update_info = cache.get_value("update-info")
	if not update_info:
		return

	updates = json.loads(update_info)

	# Check if user is int the set of users to send update message to
	update_message = ""
	if cache.sismember("update-user-set", user):
		for update_type in updates:
			release_links = ""
			for app in updates[update_type]:
				app = frappe._dict(app)
				release_links += "<b>{title}</b>: <a href='https://github.com/{org_name}/{app_name}/releases/tag/v{available_version}'>v{available_version}</a><br>".format(
					available_version=app.available_version,
					org_name=app.org_name,
					app_name=app.app_name,
					title=app.title,
				)
			if release_links:
				message = _(
					"New {} releases for the following apps are available"
				).format(_(update_type))
				update_message += "<div class='new-version-log'>{0}<div class='new-version-links'>{1}</div></div>".format(
					message, release_links
				)

	if update_message:
		frappe.msgprint(
			update_message, title=_("New updates are available"), indicator="green"
		)
		cache.srem("update-user-set", user)


def update_app_name():
	app_name = frappe.get_conf().get("elite_core_app_name", "DoxERP")
	saved_app_name = frappe.get_value("System Settings", "System Settings", "app_name")
	if saved_app_name != app_name:
		frappe.db.sql(
			"UPDATE `tabSingles` SET value = %s WHERE field='app_name' AND doctype='System Settings'",
			(app_name),
		)


def add_translation(force=None):
	app_path = frappe.get_app_path("elite_core")
	path = app_path + "/elite_translations/"
	translations = os.listdir(path)

	for lang_file in translations:
		language = lang_file.split(".")[0]
		with open((path + lang_file), "r") as translation_file:
			reader = csv.reader(translation_file)
			for row in reader:
				exist = frappe.db.exists(
					{"doctype": "Translation", "source_text": row[0]}
				)
				exist_langs = []
				if exist:
					for i in exist:
						existing_doc = frappe.get_doc("Translation", i[0])
						exist_langs.append(existing_doc.language)

					if language in exist_langs and force:
						existing_doc.language = language
						existing_doc.source_text = row[0]
						existing_doc.translated_text = row[1]
						existing_doc.save()
						frappe.db.commit()
						continue
					elif language in exist_langs and not force:
						continue
				else:
					doc = frappe.new_doc("Translation")
					doc.language = language
					doc.source_text = row[0]
					doc.translated_text = row[1]
					doc.insert()
					frappe.db.commit()

def delete_language_after_migrate():
	languages = frappe.get_all("Language", filters={}, fields=["name"])
	for lan in languages:
		if not lan.name in ["ar","en"]:
			frappe.delete_doc("Language", lan.name, ignore_missing=True, force=True)


@frappe.whitelist()
def get_all_vouchers(limit,offset,company):
	company_name =  frappe.get_value("Company", company, "name")

	try:
		limit = int(limit)
		offset = int(offset)
	except ValueError:
		frappe.throw("Limit and Offset should be number")
	
	length = frappe.db.sql(f'SELECT COUNT(*) FROM `tabGL Entry` where company= "{company}"')

	if  limit > 0:
		if company == company_name:
			gl_entry_query = f'select `tabGL Entry`.voucher_type, `tabGL Entry`.voucher_no, `tabGL Entry`.remarks, `tabDocType`.module FROM `tabGL Entry` INNER JOIN tabDocType ON `tabGL Entry`.voucher_type=tabDocType.name where `tabGL Entry`.company= "{company}" LIMIT {limit} OFFSET {offset}'
			doc_1 = frappe.db.sql(gl_entry_query, as_dict=True)
			amount_mapping = {"Sales Invoice":"grand_total","Purchase Invoice":"grand_total","Journal Entry":"total_debit","Payment Entry":"docstatus"}
			docs=[]

			for i in doc_1:

				if i.voucher_type in amount_mapping:
					amount = amount_mapping[i.voucher_type]
					amount_query = frappe.db.sql(f'select {amount} from `tab{i.voucher_type}` where name = "{i.voucher_no}"')
					doc_2 = {"amount":amount_query[0][0]}
					i.update(doc_2)
				else:
					frappe.throw(_(f"amount field for {i.voucher_type} not found"))
					

				status_exist = frappe.db.sql(f'SHOW COLUMNS FROM `tab{i.voucher_type}` LIKE "status"')
				if status_exist:
					status = frappe.db.sql(f'select status from `tab{i.voucher_type}` where name = "{i.voucher_no}"')
					doc_3 = {"status":status[0][0]}
					
				else:
					docstatus = frappe.db.sql(f'select docstatus from `tab{i.voucher_type}` where name = "{i.voucher_no}"')
					if docstatus[0][0] == 0:
						doc_3 = {"status":"Pending"}
					elif docstatus[0][0] == 1:
						doc_3 = {"status":"Submitted"}

				docs.append(i.update(doc_3))

			return{"docs":docs,"offset":offset,"length":length[0][0]}
		else:
			frappe.throw(_("Invalid Company"))
	else:
			frappe.throw(_("Limit should be greater than 0"))

@frappe.whitelist()
def get_gl_entries_for(limit,offset,voucher_no):
	length = frappe.db.sql(f'SELECT COUNT(*) FROM `tabGL Entry` where voucher_no = "{voucher_no}"')
	query ='select account,party_type,party,debit,credit,remarks from `tabGL Entry` WHERE voucher_no = %s LIMIT %s OFFSET %s'
	docs = frappe.db.sql(query,(voucher_no,int(limit),int(offset)),as_dict=True)
	return{"docs":docs,"offset":offset,"length":length[0][0]}


@frappe.whitelist()
def get_arabic_party_name(party_type,party):
	ar_field = {
		"Employee":"employee_name_in_arabic",
		"Customer":"customer_name_in_arabic",
		"Supplier":"supplier_name_in_arabic"
	}
	return frappe.db.get_value(party_type,party,ar_field.get(party_type))


#move in core directory
@frappe.whitelist()
def charactristics_update(self,method):
	self.production_year = frappe.db.get_value("Purchase Receipt Item",self.voucher_detail_no,"production_year")

# @frappe.whitelist()
# def get_item_price_from_charactristics(item_code,charactristics):

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

def custom_get_change_log(user=None):
	return []
	# if not frappe.get_conf().get("disable_new_update_popup"):
	# 	if not user: user = frappe.session.user

	# 	last_known_versions = frappe._dict(json.loads(frappe.db.get_value("User",
	# 		user, "last_known_versions") or "{}"))
	# 	current_versions = get_versions()

	# 	if not last_known_versions:
	# 		update_last_known_versions()
	# 		return []

	# 	change_log = []
	# 	def set_in_change_log(app, opts, change_log):
	# 		from_version = last_known_versions.get(app, {}).get("version") or "0.0.1"
	# 		to_version = opts["version"]

	# 		if from_version != to_version:
	# 			app_change_log = get_change_log_for_app(app, from_version=from_version, to_version=to_version)

	# 			if app_change_log:
	# 				change_log.append({
	# 					"title": opts["title"],
	# 					"description": opts["description"],
	# 					"version": to_version,
	# 					"change_log": app_change_log
	# 				})

	# 	for app, opts in current_versions.items():
	# 		if app != "frappe":
	# 			set_in_change_log(app, opts, change_log)

	# 	if "frappe" in current_versions:
	# 		set_in_change_log("frappe", current_versions["frappe"], change_log)

	# 	return change_log
	# else:
	# 	return []

def create_default_data():
	create_invoice_type()

def create_invoice_type():
	invoice_type = {
		"Credit Note": "اشعار دائن",
		"Debit Note":"اشعار مدين",
		"Tax Invoice":"فاتورة ضريبية"
	}
	for row,value in invoice_type.items():
		if not frappe.db.exists("Sales Invoice Type",row):
			doc = frappe.get_doc(dict(
				doctype = "Sales Invoice Type",
				invoice_type = row,
				invoice_type_in_arabic = value
			)).insert(ignore_permissions = True)
