# Copyright (c) 2026, softblocks e.U. and contributors
# For license information, please see license.txt

# Recapitulative statement (Zusammenfassende Meldung) for Austria
# ===============================================================
# Lists one line per VAT ID and transaction type with the sum of the net amounts, as
# required by form U 13 in FinanzOnline. The transaction type comes from the Sales Taxes
# and Charges Template of the invoice. The posting date decides the reporting period.

import calendar
from datetime import date
from decimal import ROUND_HALF_UP, Decimal

import frappe
from frappe import _

from erpnext_austria.constants import EU_VAT_PREFIXES, ZM_OTHER_SERVICE, ZM_TRIANGULAR_TRANSACTION
from erpnext_austria.utils.eu_vat import parse_vat_id

QUARTERS = {"Q1": (1, 3), "Q2": (4, 6), "Q3": (7, 9), "Q4": (10, 12)}


def execute(filters=None):
	filters = frappe._dict(filters or {})
	from_date, to_date = get_date_range(int(filters.year), filters.period)
	invoices = get_invoices(filters.company, from_date, to_date)
	data, invalid_invoices = get_statement_lines(invoices)

	return get_columns(), data, get_message(filters.company, invalid_invoices)


def get_date_range(year: int, period: str) -> tuple[date, date]:
	"""Return the first and last day of a month ("1" to "12") or quarter ("Q1" to "Q4")."""
	from_month, to_month = QUARTERS[period] if period in QUARTERS else (int(period), int(period))
	return date(year, from_month, 1), date(year, to_month, calendar.monthrange(year, to_month)[1])


def get_invoices(company: str, from_date: date, to_date: date) -> list[dict]:
	return frappe.get_all(
		"Sales Invoice",
		filters={
			"docstatus": 1,
			"company": company,
			"posting_date": ["between", [from_date, to_date]],
			"zm_type": ["is", "set"],
		},
		fields=["name", "tax_id", "zm_type", "base_net_total"],
		order_by="posting_date, name",
	)


def get_statement_lines(invoices: list[dict]) -> tuple[list[dict], list[str]]:
	"""Sum up the invoices per VAT ID and transaction type.

	Return the statement lines and the names of the invoices without a VAT ID of another
	EU member state. Credit notes have a negative net total and reduce the sum.
	"""
	totals = {}
	invalid_invoices = []
	for invoice in invoices:
		vat_id = get_eu_vat_id(invoice["tax_id"])
		if not vat_id:
			invalid_invoices.append(invoice["name"])
			continue

		key = (vat_id, invoice["zm_type"])
		totals[key] = totals.get(key, Decimal(0)) + Decimal(str(invoice["base_net_total"] or 0))

	lines = []
	for (vat_id, zm_type), total in sorted(totals.items()):
		amount = int(total.quantize(Decimal(1), rounding=ROUND_HALF_UP))
		if not amount:
			continue

		lines.append(
			{
				"vat_id": vat_id,
				"amount": amount,
				"triangular_transaction": "J" if zm_type == ZM_TRIANGULAR_TRANSACTION else "",
				"other_service": "J" if zm_type == ZM_OTHER_SERVICE else "",
			}
		)

	return lines, invalid_invoices


def get_eu_vat_id(tax_id: str | None) -> str | None:
	"""Return the normalized VAT ID if it belongs to another EU member state."""
	if not tax_id:
		return None

	try:
		country_code, vat_number = parse_vat_id(tax_id)
	except ValueError:
		return None

	if country_code not in EU_VAT_PREFIXES:
		return None

	return f"{country_code}{vat_number}"


def get_columns() -> list[dict]:
	return [
		{"fieldname": "vat_id", "label": _("VAT ID"), "fieldtype": "Data", "width": 180},
		{
			"fieldname": "amount",
			"label": _("Sum of Taxable Amounts in Euro"),
			"fieldtype": "Int",
			"width": 220,
		},
		{
			"fieldname": "triangular_transaction",
			"label": _(ZM_TRIANGULAR_TRANSACTION),
			"fieldtype": "Data",
			"width": 160,
		},
		{"fieldname": "other_service", "label": _(ZM_OTHER_SERVICE), "fieldtype": "Data", "width": 160},
	]


def get_message(company: str, invalid_invoices: list[str]) -> str | None:
	messages = []
	currency = frappe.get_cached_value("Company", company, "default_currency")
	if currency != "EUR":
		messages.append(
			_("The currency of {0} is {1}. The recapitulative statement is reported in Euro.").format(
				company, currency
			)
		)

	if invalid_invoices:
		links = ", ".join(frappe.utils.get_link_to_form("Sales Invoice", name) for name in invalid_invoices)
		messages.append(
			_(
				"These invoices have a recapitulative statement type, but no VAT ID of another EU member state. They are not included: {0}"
			).format(links)
		)

	return "<br><br>".join(messages) or None
