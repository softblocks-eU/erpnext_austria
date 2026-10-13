import frappe
from frappe.model.document import Document

from erpnext_austria.tasks import create_vat_id_check


def on_update(doc: Document, event: str | None = None) -> None:
	"""Check a new or changed VAT ID of a customer or supplier at once.

	Also check on reactivation, because a VAT ID changed while disabled is not checked.
	"""
	if doc.disabled or not doc.tax_id:
		return

	if not (doc.has_value_changed("tax_id") or doc.has_value_changed("disabled")):
		return

	# customer_name or supplier_name, customer_primary_address or supplier_primary_address
	prefix = frappe.scrub(doc.doctype)
	create_vat_id_check(
		doc.doctype, doc.name, doc.get(f"{prefix}_name"), doc.get(f"{prefix}_primary_address"), doc.tax_id
	)
