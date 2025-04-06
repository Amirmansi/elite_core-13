# Copyright (c) 2021, Elite Business and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt
from frappe.model.document import Document
from frappe import _

class ExpenseEntry(Document):
	def validate(self):
		if not flt(self.total_of_mode_of_payment) == flt(self.total_amount):
			frappe.throw(_("Total Mode of Payment Must Be Equal To Net Total Expense"))

		self.calculate_expense_total()
		self.calculate_mode_of_payment_total()
	
	def on_submit(self):
		make_journal_entry(self)
		# self.journal_entry = res.name
	
	def on_cancel(self):
		if frappe.db.exists("Journal Entry",self.journal_entry):
			jounal_entry = frappe.get_doc("Journal Entry",self.journal_entry)
			jounal_entry.cancel()
	
	def on_trash(self):
		if frappe.db.exists("Journal Entry",self.journal_entry):
			frappe.delete_doc("Journal Entry",self.journal_entry,force=True)

	@frappe.whitelist()
	def calculate_expense_total(self):
		self.total_amount = self.net_total = self.total_vat = 0
		for expense in self.expense_entry_account:
			if expense.amount and expense.rate: 
				expense.net_amount = expense.amount / (100 + expense.rate) * 100
				expense.vat_amount = expense.amount - expense.net_amount
			else:
				expense.vat_amount = 0
				expense.net_amount = expense.amount
			
			self.total_amount += expense.amount
			self.net_total += expense.net_amount
			self.total_vat += expense.vat_amount
		self.total_expense = self.net_total
		self.main_total_vat = self.total_vat
	
	@frappe.whitelist()
	def calculate_mode_of_payment_total(self):
		self.total_of_mode_of_payment = 0
		for payment in self.expense_entry_mode_of_payment:
			if payment.amount:
				self.total_of_mode_of_payment += flt(payment.amount)
		self.total_paid = self.total_of_mode_of_payment


def make_journal_entry(self):
	jv_doc = frappe.new_doc("Journal Entry")
	jv_doc.entry_type = "Journal Entry"
	jv_doc.company = self.company
	jv_doc.posting_date = self.date
	jv_doc.cheque_no = self.ref_no
	jv_doc.cheque_date = self.ref_date
	jv_doc.user_remark = self.remarks
	for payment in self.expense_entry_mode_of_payment: 
		jv_doc.append("accounts",dict(
			account = payment.mode_of_payment_account,
			credit_in_account_currency = payment.amount
		))
	vat_row = {}
	for expense in self.expense_entry_account:
		jv_doc.append("accounts",dict(
			account = expense.account,
			debit_in_account_currency = expense.net_amount,
			user_remark = expense.description
		))
		if expense.include_vat:
			if vat_row.get(expense.vat_account):
				vat_row[expense.vat_account] = flt(vat_row.get(expense.vat_account)) + flt(expense.vat_amount)
			else:
				vat_row[expense.vat_account] = expense.vat_amount
	if vat_row:
		for account,amount in vat_row.items():
			jv_doc.append("accounts",dict(
				account = account,
				debit_in_account_currency = amount
			))
	res = jv_doc.insert()
	frappe.db.set_value(self.doctype,self.name,"journal_entry",res.name)
	self.journal_entry = res.name
	res.submit()

@frappe.whitelist()
def get_vat_account_details(vat_type):
	return frappe.get_all("Sales Taxes and Charges",filters={"parent":vat_type},fields=["account_head","rate"])

@frappe.whitelist()
def get_default_vate_template(company):
	return frappe.get_all("Sales Taxes and Charges Template",filters={"is_default":1,"company":company},fields=["name"])

@frappe.whitelist()
def get_account_from_mode_of_payment(mode_of_payment,company):
	return frappe.get_all("Mode of Payment Account",filters={"parent":mode_of_payment,"company":company},fields=["default_account"])