DOMAIN = "entsoe_prijzen"
CONF_API_TOKEN = "api_token"
CONF_DOMAIN_ID = "domain_id"
CONF_SCAN_INTERVAL = "scan_interval"

DEFAULT_SCAN_INTERVAL = 3600  # 1x per uur updaten is genoeg voor day-ahead

DOMAINS = {
    "10YNL----------L": "NL - Nederland (15 min)",
    "10YBE----------2": "BE - België",
    "10YCB-GERMANY--8": "DE - Duitsland",
    "10YFR-RTE------C": "FR - Frankrijk",
    "10YGB----------A": "GB - Groot-Brittannië",
    "10YGR-HTSO-----Y": "GR - Griekenland",
    "10YIT-GRTN-----B": "IT - Italië",
}

PLATFORMS = ["sensor"]
