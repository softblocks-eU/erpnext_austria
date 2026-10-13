# Copyright (c) 2026, softblocks e.U. and contributors
# See license.txt

import unittest
from datetime import date

import frappe
from erpnext.accounts.doctype.journal_entry.test_journal_entry import make_journal_entry

from erpnext_austria.tests.utils import ERPNextAustriaTestSuite

from .summen__und_saldenliste import execute, get_month_range


class TestSummenUndSaldenliste(unittest.TestCase):
	def test_month_range_calendar_year(self):
		self.assertEqual(get_month_range(date(2026, 1, 1), 2), (date(2026, 2, 1), date(2026, 2, 28)))

	def test_month_range_fiscal_year(self):
		"""Months before the start month belong to the next calendar year."""
		fy_start = date(2025, 4, 1)
		self.assertEqual(get_month_range(fy_start, 4), (date(2025, 4, 1), date(2025, 4, 30)))
		self.assertEqual(get_month_range(fy_start, 12), (date(2025, 12, 1), date(2025, 12, 31)))
		self.assertEqual(get_month_range(fy_start, 2), (date(2026, 2, 1), date(2026, 2, 28)))
		self.assertEqual(get_month_range(fy_start, 3), (date(2026, 3, 1), date(2026, 3, 31)))


class TestSummenUndSaldenlisteData(ERPNextAustriaTestSuite):
	def test_accounts_without_entries_in_month(self):
		"""Accounts with a balance, but without entries in the month are included."""
		make_journal_entry("Cash - _TC", "_Test Cash - _TC", 500, posting_date="2025-06-01", submit=True)
		make_journal_entry(
			"_Test Bank - _TC", "_Test Cash - _TC", 1000, posting_date="2026-01-15", submit=True
		)
		fiscal_year = frappe.db.get_value("Fiscal Year", {"year_start_date": "2026-01-01"})

		_, data = execute(frappe._dict(company="_Test Company", fiscal_year=fiscal_year, month=2))

		rows = {row[0]: row for row in data}
		# Opening balance only
		self.assertEqual(rows["Cash - _TC"][2], 500)
		self.assertEqual(rows["Cash - _TC"][8], 500)
		# Entries before the month only
		self.assertEqual(rows["_Test Bank - _TC"][4], 1000)
		self.assertEqual(rows["_Test Bank - _TC"][8], 1000)
		# Both
		self.assertEqual(rows["_Test Cash - _TC"][8], -1500)


class TestSummenUndSaldenlisteOpening(ERPNextAustriaTestSuite):
	def test_opening_entries(self):
		"""Opening entries belong to the opening balance, not to the entries of the month."""
		journal_entry = make_journal_entry("Cash - _TC", "_Test Bank - _TC", 700, posting_date="2026-01-01")
		journal_entry.is_opening = "Yes"
		journal_entry.submit()
		fiscal_year = frappe.db.get_value("Fiscal Year", {"year_start_date": "2026-01-01"})

		_, data = execute(frappe._dict(company="_Test Company", fiscal_year=fiscal_year, month=1))

		rows = {row[0]: row for row in data}
		self.assertEqual(rows["Cash - _TC"][2], 700)
		self.assertIsNone(rows["Cash - _TC"][6])
		self.assertEqual(rows["Cash - _TC"][8], 700)
