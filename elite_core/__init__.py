
import frappe
from erpnext.stock import utils
from erpnext.stock import stock_ledger
from elite_core.overrides import charactristic_stock
from elite_core import api
from frappe.utils import change_log
__version__ = '0.0.1'

utils.get_bin = charactristic_stock.custom_get_bin
stock_ledger.update_entries_after.update_bin = charactristic_stock.custom_update_bin
stock_ledger.get_previous_sle_of_current_voucher = charactristic_stock.custom_get_previous_sle_of_current_voucher
change_log.get_change_log = api.custom_get_change_log