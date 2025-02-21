frappe.pages['elite-coa'].on_page_load = function(wrapper) {
	frappe.require('/assets/elite_core/js/coa.js');
	frappe.require('/assets/elite_core/css/coa.css');

	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Chart of Accounts',
		single_column: true,
	});

	const container = $(wrapper).find('.layout-main-section');
	container.append(`<div class="coa"></div>`);

	page.company = page.add_field({
		label: 'Company',
		fieldtype: 'Link',
		fieldname: 'company',
		options: 'Company',
		change() {
			const form = $(wrapper).find('.layout-main-section .coa');
			console.log({ form })
			form.empty();
			form.append(`
				<chart-of-accounts
					token="${frappe.csrf_token}"
					company="${page.company.get_value()}">
				</chart-of-accounts>
			`);
		}
	});
}
