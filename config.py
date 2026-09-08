"""
Central place for constants used across the app.
Change wage/sanctioned amounts here if they're ever revised — every
module imports from here rather than hardcoding its own copy.
"""

MONTHS = ["JANUARY", "FEBRUARY", "MARCH", "APRIL", "MAY", "JUNE",
          "JULY", "AUGUST", "SEPTEMBER", "OCTOBER", "NOVEMBER", "DECEMBER"]

SANCTIONED_AMOUNT = 25000
DAILY_WAGE = 380

# Where month-to-month closing balances are persisted (see core/balance_store.py)
BALANCE_STORE_PATH = "imprest_balances.ini"

# Template file paths — single station (SETTIHALLI), fixed template set
TEMPLATE_DIR = "templates"
TEMPLATES = {
    "annex1_3v":            f"{TEMPLATE_DIR}/ANNEXURE 1 WITH 3 VOUCHERS.docx",
    "annex1_4v_stationery": f"{TEMPLATE_DIR}/ANNEXURE 1 WITH 4 VOUCHERS With Stationery.docx",
    "annex1_4v_no_stationery": f"{TEMPLATE_DIR}/ANNEXURE 1 WITH 4 VOUCHERS Without Stationery.docx",
    "labour_3v": f"{TEMPLATE_DIR}/ANNEXTURE II LABOUR 3 VOUCHERS.docx",
    "labour_4v": f"{TEMPLATE_DIR}/ANNEXTURE II LABOUR 4 VOUCHERS.docx",
}