// Copyright (c) 2021, Elite Business and contributors
// For license information, please see license.txt

frappe.ui.form.on('Expense Entry', {
	onload:function(frm,cdt,cdn) {
		if(frm.doc.__islocal){
			frappe.model.set_value(cdt,cdn,"journal_entry","")
		}
	},
	setup:function(frm) {
		frm.set_query("mode_of_payment_account", "expense_entry_mode_of_payment", function(doc, cdt, cdn) {
			return {
				filters: {
					'company': frm.doc.company,
					'is_group':0
				}
			};
		})
		frm.set_query("account", "expense_entry_account", function(doc, cdt, cdn) {
			return {
				filters: {
					'company': frm.doc.company,
					'is_group':0
				}
			};
		})
	},
	refresh: function(frm) {
		if(frm.doc.docstatus == 1) {
			frm.add_custom_button(__('Ledger'), function () {
				frappe.route_options = {
					"voucher_no": frm.doc.journal_entry,
					"from_date": frappe.sys_defaults.year_start_date,
					"to_date": frappe.sys_defaults.year_end_date,
					"company": frm.doc.company
				};
				frappe.set_route("query-report", "General Ledger");
			});
		}
	},
	calculate_expense_total:function(frm){
		frm.call({
			method:"calculate_expense_total",
			doc:frm.doc,
			callback:function(r){

			}
		})
	},
	calculate_mode_of_payment_total:function(frm){
		frm.call({
			method:"calculate_mode_of_payment_total",
			doc:frm.doc,
			callback:function(r){

			}
		})
	},
	expense_entry_account_remove:function(frm) {
		frm.trigger("calculate_expense_total")
	},
	expense_entry_mode_of_payment_remove:function(frm) {
		frm.trigger("calculate_mode_of_payment_total")
	}
});


frappe.ui.form.on('Expense Entry Account', {
	include_vat: function(frm,cdt,cdn) {
		var doc = locals[cdt][cdn];
		if(doc.include_vat) {
			frappe.call({
				method:"elite_core.elite_core.doctype.expense_entry.expense_entry.get_default_vate_template",
				args:{'company':cur_frm.doc.company},
				async:false,
				callback:function(r){
					if(r.message){
						frappe.model.set_value(cdt,cdn,"vat_type",r.message[0].name)
						frm.trigger("calculate_expense_total")
					}
				}
			})
		} else{
			frappe.model.set_value(cdt,cdn,"vat_type","")
			frappe.model.set_value(cdt,cdn,"vat_account","")
			frappe.model.set_value(cdt,cdn,"rate",0)
			frm.trigger("calculate_expense_total")

		}
	},
	vat_type: function(frm,cdt,cdn) {
		var doc = locals[cdt][cdn];
		if(doc.vat_type){
			frappe.call({
				method:"elite_core.elite_core.doctype.expense_entry.expense_entry.get_vat_account_details",
				args:{'vat_type':doc.vat_type},
				async:false,
				callback:function(r){
					if(r.message){
						frappe.model.set_value(cdt,cdn,"vat_account",r.message[0].account_head)
						frappe.model.set_value(cdt,cdn,"rate",r.message[0].rate)
						frm.trigger("calculate_expense_total")
					}
				}
			})
		}else{
			frappe.model.set_value(cdt,cdn,"vat_account","")
			frappe.model.set_value(cdt,cdn,"rate",0)
			frm.trigger("calculate_expense_total")
		}
	},
	amount:function(frm,cdt,cdn){
		var doc = locals[cdt][cdn];
		if(doc.amount){
			frm.trigger("calculate_expense_total")
		}
	}
});

frappe.ui.form.on('Expense Entry Mode of Payment', {
	amount:function(frm,cdt,cdn){
		frm.trigger("calculate_mode_of_payment_total")
	},
	mode_of_payment:function(frm,cdt,cdn){
		var doc = locals[cdt][cdn];
		if(doc.mode_of_payment) {
			frappe.call({
				method:"elite_core.elite_core.doctype.expense_entry.expense_entry.get_account_from_mode_of_payment",
				args:{'mode_of_payment':doc.mode_of_payment,'company':cur_frm.doc.company},
				async:false,
				callback:function(r){
					if(r.message){
						frappe.model.set_value(cdt,cdn,"mode_of_payment_account",r.message[0].default_account)
					}
				}
			})
		}

	}
})