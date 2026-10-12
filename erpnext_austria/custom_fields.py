from .constants import REGISTER_COURTS


def _(message: str) -> str:
	return message


def get_register_fields(insert_after: str):
	return [
		{
			"fieldtype": "Section Break",
			"fieldname": "register_sb_1",
			"label": _("Register Information"),
			"insert_after": insert_after,
			"collapsible": 1,
		},
		{
			"fieldtype": "Select",
			"fieldname": "register_type",
			"label": _("Register Type"),
			"insert_after": "register_sb_1",
			"options": "\nFN\nZVR",
			"translatable": 0,
		},
		{
			"fieldtype": "Column Break",
			"fieldname": "register_cb_1",
			"insert_after": "register_type",
		},
		{
			"fieldtype": "Data",
			"fieldname": "register_number",
			"label": _("Register Number"),
			"insert_after": "register_cb_1",
			"translatable": 0,
		},
		{
			"fieldtype": "Column Break",
			"fieldname": "register_cb_2",
			"insert_after": "register_number",
		},
		{
			"fieldtype": "Select",
			"fieldname": "register_court",
			"label": _("Register Court"),
			"insert_after": "register_cb_2",
			"options": "\n".join(["", *REGISTER_COURTS]),  # empty string to be able to select nothing
			"depends_on": 'eval:doc.register_type == "FN"',
			"translatable": 0,
		},
	]


def get_custom_fields():
	return {
		"Company": get_register_fields(insert_after="registration_details"),
		"Customer": get_register_fields(insert_after="customer_details"),
		"Supplier": get_register_fields(insert_after="language"),
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
