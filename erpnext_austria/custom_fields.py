def _(message: str) -> str:
	return message


def get_custom_fields():
	return {
		("Quotation", "Sales Order", "Sales Invoice"): [
			{
				"label": _("Tax Exemption Reason"),
				"fieldtype": "Small Text",
				"fieldname": "tax_exemption_reason",
				"fetch_from": "taxes_and_charges.tax_exemption_reason",
				"depends_on": "tax_exemption_reason",
				"insert_after": "taxes_and_charges",
				"translatable": 0,
			}
		],
		"Sales Taxes and Charges Template": [
			{
				"label": _("Tax Exemption Reason"),
				"fieldtype": "Small Text",
				"fieldname": "tax_exemption_reason",
				"insert_after": "tax_category",
				"translatable": 0,
			}
		],
	}
