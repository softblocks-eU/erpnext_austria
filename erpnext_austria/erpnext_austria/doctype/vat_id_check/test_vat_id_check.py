# Copyright (c) 2023, ALYF GmbH and Contributors
# See license.txt

from types import SimpleNamespace
from unittest.mock import patch

import frappe
from frappe.utils import add_to_date, now_datetime

from erpnext_austria.tasks import get_parties
from erpnext_austria.tests.utils import ERPNextAustriaTestSuite

CHECK_VAT_APPROX = "erpnext_austria.erpnext_austria.doctype.vat_id_check.vat_id_check.check_vat_approx"


def make_customer(tax_id="DE329035522"):
	return (
		frappe.get_doc({"doctype": "Customer", "customer_name": frappe.generate_hash(), "tax_id": tax_id})
		.insert()
		.name
	)


def make_check(customer, requester_vat_id=None, party_vat_id="DE329035522"):
	return frappe.get_doc(
		{
			"doctype": "VAT ID Check",
			"party_type": "Customer",
			"party": customer,
			"party_vat_id": party_vat_id,
			"requester_vat_id": requester_vat_id,
		}
	).insert()


def add_past_check(customer, status, **age):
	"""Insert a VAT ID Check with the given status and age without running the check."""
	doc = frappe.get_doc(
		{
			"doctype": "VAT ID Check",
			"party_type": "Customer",
			"party": customer,
			"party_vat_id": "DE329035522",
			"status": status,
		}
	)
	doc.name = frappe.generate_hash()
	doc.creation = doc.modified = add_to_date(now_datetime(), **age)
	doc.db_insert()


def is_due(customer):
	return customer in [party[1] for party in get_parties("Customer", batch_size=10000)]


class TestVATIDCheck(ERPNextAustriaTestSuite):
	def test_match_codes(self):
		"""Only "1" is a match. "2" means no match, "3" not processed."""
		result = SimpleNamespace(
			valid=True,
			traderNameMatch="1",
			traderStreetMatch="2",
			traderPostcodeMatch="3",
			traderCityMatch=None,
			requestIdentifier="WAPI000001",
			traderName="Test GmbH",
			traderAddress="Teststraße 1",
		)
		with patch(CHECK_VAT_APPROX, return_value=result):
			check = make_check(make_customer())

		check.reload()
		self.assertEqual(check.status, "Completed")
		self.assertTrue(check.trader_name_match)
		self.assertFalse(check.trader_street_match)
		self.assertFalse(check.trader_postcode_match)
		self.assertFalse(check.trader_city_match)

	def test_invalid_party_vat_id(self):
		"""An invalid VAT ID of the party does not prevent saving."""
		with patch(CHECK_VAT_APPROX) as check_vat_approx:
			check = make_check(make_customer(), party_vat_id="CHE-123.456.789 MWST")

		check.reload()
		self.assertEqual(check.status, "Invalid Input")
		check_vat_approx.assert_not_called()

	def test_invalid_requester_vat_id(self):
		"""An invalid own VAT ID is an error, not an invalid VAT ID of the party."""
		with patch(CHECK_VAT_APPROX) as check_vat_approx:
			check = make_check(make_customer(), requester_vat_id="12/345")

		check.reload()
		self.assertEqual(check.status, "Error")
		self.assertFalse(check.is_valid)
		check_vat_approx.assert_not_called()

	def test_due_without_check(self):
		self.assertTrue(is_due(make_customer()))

	def test_not_due_without_vat_id(self):
		self.assertFalse(is_due(make_customer(tax_id="")))

	def test_due_by_status(self):
		"""The status of the latest check decides when the party is checked again."""
		cases = [
			("Planned", {"hours": -1}, False),
			("Planned", {"days": -2}, True),
			("Running", {"days": -2}, True),
			("Completed", {"months": -2}, False),
			("Completed", {"months": -4}, True),
			("Invalid Input", {"years": -1}, False),
			("Service Unavailable", {"hours": -1}, False),
			("Service Unavailable", {"hours": -3}, True),
			("Error", {"days": -6}, False),
			("Error", {"days": -8}, True),
		]
		for status, age, expected in cases:
			with self.subTest(status=status, age=age):
				customer = make_customer()
				add_past_check(customer, status, **age)
				self.assertEqual(is_due(customer), expected)

	def test_due_by_latest_check(self):
		"""An older check does not count if there is a newer one."""
		customer = make_customer()
		add_past_check(customer, "Completed", months=-4)
		add_past_check(customer, "Completed", days=-1)
		self.assertFalse(is_due(customer))
