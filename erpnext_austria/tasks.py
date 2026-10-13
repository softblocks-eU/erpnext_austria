import frappe
from dateutil.relativedelta import relativedelta
from erpnext import get_default_company
from frappe.query_builder import DocType
from frappe.utils import now_datetime
from pypika import functions as fn

# Time after the last check until a party is checked again, per status of the last check.
# "Invalid Input" is not checked again automatically. A changed VAT ID is checked when it is saved.
RECHECK_INTERVALS = {
	"Planned": relativedelta(days=1),
	"Running": relativedelta(days=1),
	"Completed": relativedelta(months=3),
	"Service Unavailable": relativedelta(hours=2),
	"Error": relativedelta(weeks=1),
}


def all():
	check_some_parties()


def get_parties(party_type: str, batch_size=4):
	"""Return a list of n customers or suppliers whose VAT ID is due for a check."""
	parties = DocType(party_type)
	vat_id_checks = DocType("VAT ID Check")
	last_check = get_last_check_query(party_type)

	# Compare with the time of the system, like the creation of a document. NOW() of the
	# database can be in another time zone.
	now = now_datetime()
	is_due = last_check.creation.isnull()
	for status, interval in RECHECK_INTERVALS.items():
		is_due |= (vat_id_checks.status == status) & (vat_id_checks.creation < now - interval)

	return (
		frappe.qb.from_(parties)
		.left_join(last_check)
		.on(parties.name == last_check.party)
		.left_join(vat_id_checks)
		.on(
			(vat_id_checks.party_type == party_type)
			& (vat_id_checks.party == last_check.party)
			& (vat_id_checks.creation == last_check.creation)
		)
		.select(
			fn.LiteralValue(f"'{party_type}'"),
			parties.name,
			parties[f"{frappe.scrub(party_type)}_name"],
			parties[f"{frappe.scrub(party_type)}_primary_address"],
			parties.tax_id,
		)
		.where(parties.tax_id.notnull() & (parties.tax_id != "") & (parties.disabled == 0) & is_due)
		.limit(batch_size)
		.run()
	)


def get_last_check_query(party_type: str):
	vat_id_checks = DocType("VAT ID Check")
	return (
		frappe.qb.from_(vat_id_checks)
		.select(
			vat_id_checks.party,
			fn.Max(vat_id_checks.creation).as_("creation"),
		)
		.where(vat_id_checks.party_type == party_type)
		.groupby(vat_id_checks.party)
	)


def check_some_parties():
	"""Check VAT IDs of customers and suppliers whose last check is due for a repetition."""
	for party in get_parties("Customer") + get_parties("Supplier"):
		create_vat_id_check(*party)


def create_vat_id_check(party_type, party, party_name, primary_address, vat_id):
	"""Create a VAT ID Check for the party. The check itself runs in the background."""
	doc = frappe.new_doc("VAT ID Check")
	doc.party_type = party_type
	doc.party = party
	doc.trader_name = party_name
	doc.party_vat_id = vat_id
	if company := get_default_company():
		doc.company = company
		doc.requester_vat_id = frappe.get_cached_value("Company", company, "tax_id")

	if primary_address:
		address = frappe.get_doc("Address", primary_address)
		doc.trader_street = address.address_line1
		doc.trader_postcode = address.pincode
		doc.trader_city = address.city

	doc.insert(ignore_permissions=True)
