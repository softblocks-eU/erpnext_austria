### ERPNext Austria

App to hold regional code for Austria, built on top of ERPNext.

This app is based on [ERPNext Germany](https://github.com/alyf-de/erpnext_germany) by ALYF GmbH.

### Features

- Validation of EU VAT IDs (UID-Nummer) of customers and suppliers, automatically every three months or manually
- Allow deletion of the most recent sales transaction (per naming series and company) only. Applies to **Quotation**, **Sales Order** and **Sales Invoice**.
- Restrict deletion of attachments to submitted transactions
- Tax exemption reason in **Sales Taxes and Charges Template**, **Quotation**, **Sales Order** and **Sales Invoice**
- Create **Business Letters** from a template and print or email them to your customers or suppliers
- Report _Summen- und Saldenliste_
- Report _Zusammenfassende Meldung_ (recapitulative statement) for FinanzOnline

### Zusammenfassende Meldung

The report lists the lines of the recapitulative statement (form U 13) for a month or quarter: one line per VAT ID and transaction type with the sum of the net amounts in whole Euro. You can enter these lines in FinanzOnline.

1. Set the _Recapitulative Statement Type_ in each **Sales Taxes and Charges Template** you use for customers in other EU member states: _Intra-Community Supply_, _Other Service_ or _Triangular Transaction_.
2. **Sales Invoices** take the type from their template. Only submitted invoices with a type and a VAT ID of another EU member state are included. Credit notes reduce the sum.
3. Open the report _Zusammenfassende Meldung_, select company, year and period.

Simplifications:

- The posting date of the invoice decides the reporting period.
- An invoice has one transaction type. Put goods and services for the same customer on separate invoices.
- Transfers of own goods (Verbringen), consignment stock (Konsignationslager) and corrections of a submitted statement are not supported.

### Installation

You can install this app using the [bench](https://github.com/frappe/bench) CLI:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app https://github.com/softblocks-eU/erpnext_austria.git --branch version-16
bench --site $SITE_NAME install-app erpnext_austria
```

### Contributing

This app uses `pre-commit` for code formatting and linting. Please [install pre-commit](https://pre-commit.com/#installation) and enable it for this repository:

```bash
cd apps/erpnext_austria
pre-commit install
```

Pre-commit is configured to use the following tools for checking and formatting your code:

- ruff
- eslint
- prettier
- pyupgrade
### CI

This app can use GitHub Actions for CI. The following workflows are configured:

- CI: Installs this app and runs unit tests on every push to `version-16` branch.
- Linters: Runs [Frappe Semgrep Rules](https://github.com/frappe/semgrep-rules) and [pip-audit](https://pypi.org/project/pip-audit/) on every pull request.


### License

gpl-3.0
