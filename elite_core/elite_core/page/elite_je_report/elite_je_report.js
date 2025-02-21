frappe.pages['elite-je-report'].on_page_load = function(wrapper) {
	frappe.require('/assets/elite_core/js/je-report.js');
	frappe.require('/assets/elite_core/css/je-report.css');
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Journal Entry Report',
		single_column: true
	});
	const container = $(wrapper).find('.layout-main-section');
	container.append(`<je-report message token="${frappe.csrf_token}"></je-report>`)
}
