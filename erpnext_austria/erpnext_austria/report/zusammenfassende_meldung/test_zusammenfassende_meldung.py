# Copyright (c) 2026, softblocks e.U. and contributors
# See license.txt

import unittest
from datetime import date

from erpnext_austria.constants import (
	ZM_INTRA_COMMUNITY_SUPPLY,
	ZM_OTHER_SERVICE,
	ZM_TRIANGULAR_TRANSACTION,
)

from .zusammenfassende_meldung import get_date_range, get_statement_lines


def invoice(name, tax_id, zm_type, base_net_total):
	return {"name": name, "tax_id": tax_id, "zm_type": zm_type, "base_net_total": base_net_total}


def line(vat_id, amount, triangular_transaction="", other_service=""):
	return {
		"vat_id": vat_id,
		"amount": amount,
		"triangular_transaction": triangular_transaction,
		"other_service": other_service,
	}


class TestZusammenfassendeMeldung(unittest.TestCase):
	def test_intra_community_supply(self):
		"""Sum up the supplies per VAT ID and normalize the VAT ID."""
		lines, invalid = get_statement_lines(
			[
				invoice("SI-1", "DE329035522", ZM_INTRA_COMMUNITY_SUPPLY, 1000.40),
				invoice("SI-2", "de 329 035 522", ZM_INTRA_COMMUNITY_SUPPLY, 500.20),
			]
		)
		self.assertEqual(lines, [line("DE329035522", 1501)])
		self.assertEqual(invalid, [])

	def test_other_service(self):
		lines, _ = get_statement_lines([invoice("SI-1", "FR12345678901", ZM_OTHER_SERVICE, 2000)])
		self.assertEqual(lines, [line("FR12345678901", 2000, other_service="J")])

	def test_triangular_transaction(self):
		lines, _ = get_statement_lines([invoice("SI-1", "LU99999999", ZM_TRIANGULAR_TRANSACTION, 20000)])
		self.assertEqual(lines, [line("LU99999999", 20000, triangular_transaction="J")])

	def test_one_line_per_transaction_type(self):
		lines, _ = get_statement_lines(
			[
				invoice("SI-1", "DE329035522", ZM_INTRA_COMMUNITY_SUPPLY, 100),
				invoice("SI-2", "DE329035522", ZM_OTHER_SERVICE, 200),
			]
		)
		self.assertEqual(
			lines,
			[line("DE329035522", 100), line("DE329035522", 200, other_service="J")],
		)

	def test_credit_note(self):
		"""Credit notes reduce the sum. A negative sum is reported, a sum of zero is not."""
		lines, _ = get_statement_lines(
			[
				invoice("SI-1", "DE329035522", ZM_INTRA_COMMUNITY_SUPPLY, 1000),
				invoice("SI-2", "DE329035522", ZM_INTRA_COMMUNITY_SUPPLY, -1200),
				invoice("SI-3", "NL123456789B01", ZM_INTRA_COMMUNITY_SUPPLY, 300),
				invoice("SI-4", "NL123456789B01", ZM_INTRA_COMMUNITY_SUPPLY, -300),
			]
		)
		self.assertEqual(lines, [line("DE329035522", -200)])

	def test_rounding(self):
		"""Round half up to whole Euro, also for sums of several invoices."""
		lines, _ = get_statement_lines(
			[
				invoice("SI-1", "DE329035522", ZM_INTRA_COMMUNITY_SUPPLY, 0.25),
				invoice("SI-2", "DE329035522", ZM_INTRA_COMMUNITY_SUPPLY, 2.25),
			]
		)
		self.assertEqual(lines, [line("DE329035522", 3)])

	def test_greece_and_northern_ireland(self):
		lines, invalid = get_statement_lines(
			[
				invoice("SI-1", "EL123456789", ZM_INTRA_COMMUNITY_SUPPLY, 100),
				invoice("SI-2", "XI123456789", ZM_INTRA_COMMUNITY_SUPPLY, 100),
			]
		)
		self.assertEqual(lines, [line("EL123456789", 100), line("XI123456789", 100)])
		self.assertEqual(invalid, [])

	def test_northern_ireland_other_service(self):
		"""Northern Ireland belongs to the single market for goods only."""
		lines, invalid = get_statement_lines([invoice("SI-1", "XI123456789", ZM_OTHER_SERVICE, 100)])
		self.assertEqual(lines, [])
		self.assertEqual(invalid, ["SI-1"])

	def test_invalid_vat_ids(self):
		"""Austrian, non-EU, malformed and missing VAT IDs are not reported."""
		lines, invalid = get_statement_lines(
			[
				invoice("SI-1", "ATU37866403", ZM_INTRA_COMMUNITY_SUPPLY, 100),
				invoice("SI-2", "CHE123456789", ZM_OTHER_SERVICE, 100),
				invoice("SI-3", "GB123456789", ZM_OTHER_SERVICE, 100),
				invoice("SI-4", "D-123", ZM_INTRA_COMMUNITY_SUPPLY, 100),
				invoice("SI-5", None, ZM_INTRA_COMMUNITY_SUPPLY, 100),
			]
		)
		self.assertEqual(lines, [])
		self.assertEqual(invalid, ["SI-1", "SI-2", "SI-3", "SI-4", "SI-5"])

	def test_date_range(self):
		self.assertEqual(get_date_range(2026, "2"), (date(2026, 2, 1), date(2026, 2, 28)))
		self.assertEqual(get_date_range(2024, "2"), (date(2024, 2, 1), date(2024, 2, 29)))
		self.assertEqual(get_date_range(2026, "Q4"), (date(2026, 10, 1), date(2026, 12, 31)))
