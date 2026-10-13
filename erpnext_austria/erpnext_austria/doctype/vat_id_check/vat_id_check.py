# Copyright (c) 2023, ALYF GmbH and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from requests.exceptions import RequestException
from tenacity import RetryError
from zeep.exceptions import TransportError

from erpnext_austria.utils.eu_vat import check_vat_approx, parse_vat_id

# Match code of VIES for a matching name or address. "2" means no match, "3" not processed.
MATCH_VALID = "1"


class VATIDCheck(Document):
	def before_insert(self):
		# Invalid VAT IDs are kept as entered. run_check sets the status, so that saving a
		# customer or the scheduler does not fail.
		self.requester_vat_id = normalize_vat_id(self.requester_vat_id)
		self.party_vat_id = normalize_vat_id(self.party_vat_id)

	def after_insert(self):
		frappe.enqueue(
			run_check,
			doc=self,
			queue="long",
			now=frappe.conf.developer_mode or frappe.in_test,
			enqueue_after_commit=True,
		)


def normalize_vat_id(vat_id: str | None) -> str | None:
	"""Return the VAT ID without spaces and in upper case, or unchanged if it is invalid."""
	if not vat_id:
		return vat_id

	try:
		country_code, vat_number = parse_vat_id(vat_id)
	except ValueError:
		return vat_id

	return f"{country_code}{vat_number}"


def run_check(doc: VATIDCheck):
	doc.db_set("status", "Running", notify=True)
	requester_country_code, requester_vat_number = None, None
	if doc.requester_vat_id:
		try:
			requester_country_code, requester_vat_number = parse_vat_id(doc.requester_vat_id)
		except ValueError:
			# The own VAT ID is wrong, not the one of the party. The party is checked again later.
			doc.db_set({"status": "Error"}, notify=True)
			frappe.log_error(
				"VAT ID Check Error",
				_("The VAT ID {0} of the company is invalid.").format(doc.requester_vat_id),
			)
			return

	try:
		country_code, vat_number = parse_vat_id(doc.party_vat_id)
	except ValueError:
		doc.db_set({"status": "Invalid Input", "is_valid": False}, notify=True)
		return

	try:
		result = check_vat_approx(
			country_code=country_code,
			vat_number=vat_number,
			trader_name=doc.trader_name,
			trader_street=doc.trader_street,
			trader_postcode=doc.trader_postcode,
			trader_city=doc.trader_city,
			requester_country_code=requester_country_code,
			requester_vat_number=requester_vat_number,
		)
	except (RetryError, RequestException, TransportError):
		doc.db_set("status", "Service Unavailable", notify=True)
		return
	except Exception as e:
		if hasattr(e, "message") and e.message.upper() == "INVALID_INPUT":
			doc.db_set({"status": "Invalid Input", "is_valid": False}, notify=True)
		else:
			doc.db_set({"status": "Error"}, notify=True)
			frappe.log_error("VAT ID Check Error", frappe.get_traceback())

		return

	doc.db_set(
		{
			"status": "Completed",
			"is_valid": result.valid,
			"trader_name_match": result.traderNameMatch == MATCH_VALID,
			"trader_street_match": result.traderStreetMatch == MATCH_VALID,
			"trader_postcode_match": result.traderPostcodeMatch == MATCH_VALID,
			"trader_city_match": result.traderCityMatch == MATCH_VALID,
			"request_id": result.requestIdentifier,
			"actual_trader_name": result.traderName,
			"actual_trader_address": result.traderAddress,
		},
		notify=True,
	)
