# Austrian company register courts (Firmenbuchgerichte)
REGISTER_COURTS = [
	"Handelsgericht Wien",
	"Landesgericht Eisenstadt",
	"Landesgericht Feldkirch",
	"Landesgericht für Zivilrechtssachen Graz",
	"Landesgericht Innsbruck",
	"Landesgericht Klagenfurt",
	"Landesgericht Korneuburg",
	"Landesgericht Krems an der Donau",
	"Landesgericht Leoben",
	"Landesgericht Linz",
	"Landesgericht Ried im Innkreis",
	"Landesgericht Salzburg",
	"Landesgericht St. Pölten",
	"Landesgericht Steyr",
	"Landesgericht Wels",
	"Landesgericht Wiener Neustadt",
]

# VAT ID prefixes of the other EU member states. Greece uses EL instead of its ISO code GR.
# XI (Northern Ireland) remains part of the EU single market for goods.
EU_VAT_PREFIXES = (
	"BE",
	"BG",
	"CY",
	"CZ",
	"DE",
	"DK",
	"EE",
	"EL",
	"ES",
	"FI",
	"FR",
	"HR",
	"HU",
	"IE",
	"IT",
	"LT",
	"LU",
	"LV",
	"MT",
	"NL",
	"PL",
	"PT",
	"RO",
	"SE",
	"SI",
	"SK",
	"XI",
)


def _(message: str) -> str:
	return message


# Transaction types of the recapitulative statement (Zusammenfassende Meldung).
# The values are stored untranslated, `_` only marks them for translation.
ZM_INTRA_COMMUNITY_SUPPLY = _("Intra-Community Supply")
ZM_OTHER_SERVICE = _("Other Service")
ZM_TRIANGULAR_TRANSACTION = _("Triangular Transaction")
