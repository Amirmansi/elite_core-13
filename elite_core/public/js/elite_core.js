$(window).on('load', function() {
    frappe.after_ajax(function () {
        $('.dropdown-help').attr('style', 'display: none !important');
        if (frappe.boot.elite_core.show_help_menu) {
            // $('.dropdown-help').css('display','block');
            $('.dropdown-help').attr('style', 'display: block !important');
        }
        if (frappe.boot.elite_core.logo_width) {
            $('.app-logo').css('width',frappe.boot.elite_core.logo_width+'px');
        }
        if (frappe.boot.elite_core.logo_height) {
            $('.app-logo').css('height',frappe.boot.elite_core.logo_height+'px');
            $('.app-logo').attr('style', 'max-height: 40px !important');
        }
        if (frappe.boot.elite_core.navbar_background_color) {
            $('.navbar').css('background-color',frappe.boot.elite_core.navbar_background_color)
        }
        if (frappe.boot.elite_core.custom_navbar_title_style && frappe.boot.elite_core.custom_navbar_title) {
            $(`<span style=${frappe.boot.elite_core.custom_navbar_title_style.replace('\n','')} class="hidden-xs hidden-sm">${frappe.boot.elite_core.custom_navbar_title}</span>`).insertAfter("#navbar-breadcrumbs")
        }
    })
})
