// Copyright (c) 2023, ALYF GmbH and contributors
// For license information, please see license.txt

frappe.ui.form.on("VAT ID Check", {
	setup: function (frm) {
		frm.add_fetch("party", "tax_id", "party_vat_id");

		frm.set_query("party_type", function (doc) {
			return {
				filters: {
					name: ["in", ["Customer", "Supplier"]],
				},
			};
		});

		frm.set_query("party_address", function (doc) {
			return {
				query: "frappe.contacts.doctype.address.address.address_query",
				filters: {
					link_doctype: doc.party_type,
					link_name: doc.party,
				},
			};
		});
	},
	party: function (frm) {
		if (!frm.doc.party_type || !frm.doc.party) {
			return;
		}

		// customer_name or supplier_name
		const name_field = `${frappe.scrub(frm.doc.party_type)}_name`;
		frappe.db.get_value(frm.doc.party_type, frm.doc.party, name_field).then((r) => {
			frm.set_value("trader_name", r.message[name_field]);
		});
	},
});
