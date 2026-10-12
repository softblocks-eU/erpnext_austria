// Copyright (c) 2026, softblocks e.U. and contributors
// For license information, please see license.txt

frappe.query_reports["Zusammenfassende Meldung"] = {
	filters: [
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),
			reqd: 1,
		},
		{
			fieldname: "year",
			label: __("Year"),
			fieldtype: "Int",
			default: new Date().getFullYear(),
			reqd: 1,
		},
		{
			fieldname: "period",
			label: __("Period"),
			fieldtype: "Select",
			options: [
				{ value: "1", label: __("January") },
				{ value: "2", label: __("February") },
				{ value: "3", label: __("March") },
				{ value: "4", label: __("April") },
				{ value: "5", label: __("May") },
				{ value: "6", label: __("June") },
				{ value: "7", label: __("July") },
				{ value: "8", label: __("August") },
				{ value: "9", label: __("September") },
				{ value: "10", label: __("October") },
				{ value: "11", label: __("November") },
				{ value: "12", label: __("December") },
				{ value: "Q1", label: __("First Quarter") },
				{ value: "Q2", label: __("Second Quarter") },
				{ value: "Q3", label: __("Third Quarter") },
				{ value: "Q4", label: __("Fourth Quarter") },
			],
			reqd: 1,
		},
	],
};
