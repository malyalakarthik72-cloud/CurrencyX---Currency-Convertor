"""
CurrencyX - Flask Backend
- Exchange rates: https://open.exchangerate-api.com/v6/latest/USD (free, no key)
- Forex news:     https://newsdata.io (free, API key required)
  Get your free key at: https://newsdata.io/register (no credit card needed)
"""

from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv
import urllib.request
import json
import time
import math
import os

app = Flask(__name__)

# ── NEWSDATA.IO API KEY ───────────────────────────────────────────────────────
# Free plan: 200 requests/day — https://newsdata.io/dashboard
load_dotenv()
NEWSDATAIO_KEY = os.getenv("NEWSDATAIO_KEY")

# ── CURRENCY METADATA ─────────────────────────────────────────────────────────
CURRENCY_NAMES = {
    # Major / G10
    "USD":"US Dollar","EUR":"Euro","GBP":"British Pound","JPY":"Japanese Yen",
    "AUD":"Australian Dollar","CAD":"Canadian Dollar","CHF":"Swiss Franc",
    "CNY":"Chinese Yuan","NZD":"New Zealand Dollar","HKD":"Hong Kong Dollar",
    "SGD":"Singapore Dollar","NOK":"Norwegian Krone","SEK":"Swedish Krona",
    "DKK":"Danish Krone",
    # Asia-Pacific
    "INR":"Indian Rupee","KRW":"South Korean Won","THB":"Thai Baht",
    "IDR":"Indonesian Rupiah","MYR":"Malaysian Ringgit","PHP":"Philippine Peso",
    "PKR":"Pakistani Rupee","BDT":"Bangladeshi Taka","LKR":"Sri Lankan Rupee",
    "NPR":"Nepalese Rupee","MMK":"Myanmar Kyat","KHR":"Cambodian Riel",
    "LAK":"Lao Kip","VND":"Vietnamese Dong","MNT":"Mongolian Tögrög",
    "TWD":"Taiwan Dollar","MVR":"Maldivian Rufiyaa","BTN":"Bhutanese Ngultrum",
    "AFN":"Afghan Afghani","AMD":"Armenian Dram","AZN":"Azerbaijani Manat",
    "GEL":"Georgian Lari","KGS":"Kyrgyzstani Som","KZT":"Kazakhstani Tenge",
    "TJS":"Tajikistani Somoni","TMT":"Turkmenistani Manat","UZS":"Uzbekistani Som",
    # Middle East
    "AED":"UAE Dirham","SAR":"Saudi Riyal","QAR":"Qatari Riyal","KWD":"Kuwaiti Dinar",
    "BHD":"Bahraini Dinar","OMR":"Omani Rial","IQD":"Iraqi Dinar","IRR":"Iranian Rial",
    "JOD":"Jordanian Dinar","LBP":"Lebanese Pound","SYP":"Syrian Pound",
    "YER":"Yemeni Rial","ILS":"Israeli Shekel",
    # Africa
    "ZAR":"South African Rand","NGN":"Nigerian Naira","KES":"Kenyan Shilling",
    "GHS":"Ghanaian Cedi","EGP":"Egyptian Pound","MAD":"Moroccan Dirham",
    "TZS":"Tanzanian Shilling","UGX":"Ugandan Shilling","ETB":"Ethiopian Birr",
    "DZD":"Algerian Dinar","XOF":"West African CFA Franc","XAF":"Central African CFA Franc",
    "ZMW":"Zambian Kwacha","MWK":"Malawian Kwacha","MZN":"Mozambican Metical",
    "AOA":"Angolan Kwanza","SDG":"Sudanese Pound","RWF":"Rwandan Franc",
    "TND":"Tunisian Dinar","LYD":"Libyan Dinar","MUR":"Mauritian Rupee",
    "SCR":"Seychellois Rupee","BWP":"Botswana Pula","NAD":"Namibian Dollar",
    "SZL":"Swazi Lilangeni","LSL":"Lesotho Loti","ZWL":"Zimbabwean Dollar",
    "CDF":"Congolese Franc","GMD":"Gambian Dalasi","GNF":"Guinean Franc",
    "SLL":"Sierra Leonean Leone","LRD":"Liberian Dollar","CVE":"Cape Verdean Escudo",
    "STN":"São Tomé & Príncipe Dobra","DJF":"Djiboutian Franc","ERN":"Eritrean Nakfa",
    "SOS":"Somali Shilling","KMF":"Comorian Franc","MGA":"Malagasy Ariary",
    "MRU":"Mauritanian Ouguiya",
    # Europe (non-euro)
    "RUB":"Russian Ruble","TRY":"Turkish Lira","PLN":"Polish Złoty",
    "CZK":"Czech Koruna","HUF":"Hungarian Forint","RON":"Romanian Leu",
    "BGN":"Bulgarian Lev","HRK":"Croatian Kuna","RSD":"Serbian Dinar",
    "UAH":"Ukrainian Hryvnia","ISK":"Icelandic Króna","HUF":"Hungarian Forint",
    "ALL":"Albanian Lek","BAM":"Bosnia-Herzegovina Mark","MKD":"Macedonian Denar",
    "MDL":"Moldovan Leu","BYN":"Belarusian Ruble","GBP":"British Pound",
    "NOK":"Norwegian Krone","CHF":"Swiss Franc",
    # Americas
    "MXN":"Mexican Peso","BRL":"Brazilian Real","COP":"Colombian Peso",
    "ARS":"Argentine Peso","CLP":"Chilean Peso","PEN":"Peruvian Sol",
    "UYU":"Uruguayan Peso","PYG":"Paraguayan Guaraní","BOB":"Bolivian Boliviano",
    "VES":"Venezuelan Bolívar","GTQ":"Guatemalan Quetzal","HNL":"Honduran Lempira",
    "NIO":"Nicaraguan Córdoba","CRC":"Costa Rican Colón","PAB":"Panamanian Balboa",
    "DOP":"Dominican Peso","CUP":"Cuban Peso","JMD":"Jamaican Dollar",
    "TTD":"Trinidad & Tobago Dollar","BBD":"Barbadian Dollar","BSD":"Bahamian Dollar",
    "BZD":"Belize Dollar","GYD":"Guyanese Dollar","SRD":"Surinamese Dollar",
    "HTG":"Haitian Gourde","AWG":"Aruban Florin","ANG":"Netherlands Antillean Guilder",
    "KYD":"Cayman Islands Dollar","XCD":"East Caribbean Dollar",
    # Pacific
    "FJD":"Fijian Dollar","PGK":"Papua New Guinean Kina","WST":"Samoan Tālā",
    "TOP":"Tongan Paʻanga","VUV":"Vanuatu Vatu","SBD":"Solomon Islands Dollar",
}

CURRENCY_SYMBOLS = {
    "USD":"$","EUR":"€","GBP":"£","JPY":"¥","AUD":"A$","CAD":"C$",
    "CHF":"Fr","CNY":"¥","INR":"₹","MXN":"$","BRL":"R$","KRW":"₩",
    "SGD":"S$","HKD":"HK$","NOK":"kr","SEK":"kr","DKK":"kr","NZD":"NZ$",
    "ZAR":"R","RUB":"₽","TRY":"₺","AED":"د.إ","SAR":"﷼","THB":"฿",
    "IDR":"Rp","MYR":"RM","PHP":"₱","PKR":"₨","EGP":"£","CZK":"Kč",
    "PLN":"zł","HUF":"Ft","ILS":"₪","CLP":"$","COP":"$","ARS":"$",
    "VND":"₫","NGN":"₦","KES":"KSh","GHS":"₵","UAH":"₴","RON":"lei",
    "BGN":"лв","HRK":"kn","RSD":"din","BDT":"৳","LKR":"₨","MAD":"د.م.",
    "QAR":"﷼","KWD":"د.ك",
    # Extended
    "TWD":"NT$","NPR":"₨","MMK":"K","KHR":"៛","LAK":"₭","MNT":"₮",
    "MVR":"Rf","BTN":"Nu","AFN":"؋","AMD":"֏","AZN":"₼","GEL":"₾",
    "KGS":"с","KZT":"₸","TJS":"SM","TMT":"T","UZS":"so'm",
    "BHD":"BD","OMR":"﷼","IQD":"ع.د","IRR":"﷼","JOD":"JD","LBP":"ل.ل",
    "SYP":"£","YER":"﷼",
    "TZS":"TSh","UGX":"USh","ETB":"Br","DZD":"دج","XOF":"CFA","XAF":"FCFA",
    "ZMW":"ZK","MWK":"MK","MZN":"MT","AOA":"Kz","SDG":"ج.س.","RWF":"RF",
    "TND":"د.ت","LYD":"ل.د","MUR":"₨","SCR":"₨","BWP":"P","NAD":"N$",
    "SZL":"L","LSL":"L","ZWL":"Z$","CDF":"FC","GMD":"D","GNF":"FG",
    "SLL":"Le","LRD":"$","CVE":"$","STN":"Db","DJF":"Fdj","ERN":"Nfk",
    "SOS":"Sh","KMF":"CF","MGA":"Ar","MRU":"UM",
    "ISK":"kr","ALL":"L","BAM":"KM","MKD":"ден","MDL":"L","BYN":"Br",
    "PEN":"S/.","UYU":"$U","PYG":"₲","BOB":"Bs.","VES":"Bs.S",
    "GTQ":"Q","HNL":"L","NIO":"C$","CRC":"₡","PAB":"B/.","DOP":"RD$",
    "CUP":"$","JMD":"J$","TTD":"TT$","BBD":"Bds$","BSD":"B$","BZD":"BZ$",
    "GYD":"G$","SRD":"$","HTG":"G","AWG":"ƒ","ANG":"ƒ","KYD":"CI$",
    "XCD":"EC$",
    "FJD":"FJ$","PGK":"K","WST":"T","TOP":"T$","VUV":"Vt","SBD":"SI$",
}

# ── FALLBACK RATES (used if exchange rate API is unreachable) ─────────────────
FALLBACK_RATES = {
    "USD":1.0,"EUR":0.9200,"GBP":0.7900,"JPY":149.50,"AUD":1.5300,
    "CAD":1.3600,"CHF":0.8800,"CNY":7.2400,"INR":83.10,"MXN":17.20,
    "BRL":4.9700,"KRW":1325.0,"SGD":1.3400,"HKD":7.8200,"NOK":10.50,
    "SEK":10.30,"DKK":6.8800,"NZD":1.6300,"ZAR":18.70,"RUB":91.20,
    "TRY":32.10,"AED":3.6700,"SAR":3.7500,"THB":35.10,"IDR":15700.0,
    "MYR":4.7100,"PHP":56.10,"PKR":278.0,"EGP":30.80,"CZK":23.10,
    "PLN":4.0300,"HUF":356.0,"ILS":3.7100,"CLP":912.0,"COP":3910.0,
    "ARS":875.0,"VND":24500.0,"NGN":1410.0,"KES":129.0,"GHS":12.10,
    "UAH":37.80,"RON":4.6300,"BGN":1.8400,"HRK":7.1000,"RSD":108.0,
    "BDT":109.0,"LKR":312.0,"MAD":9.8500,"QAR":3.6400,"KWD":0.3070,
    # Extended fallbacks
    "TWD":31.50,"NPR":133.0,"MMK":2100.0,"KHR":4100.0,"LAK":20800.0,
    "MNT":3450.0,"MVR":15.40,"BTN":83.10,"AFN":70.20,"AMD":387.0,
    "AZN":1.7000,"GEL":2.6500,"KGS":89.10,"KZT":448.0,"TJS":10.90,
    "TMT":3.5000,"UZS":12600.0,
    "BHD":0.3760,"OMR":0.3850,"IQD":1310.0,"IRR":42000.0,"JOD":0.7100,
    "LBP":89500.0,"SYP":13000.0,"YER":250.0,
    "TZS":2520.0,"UGX":3780.0,"ETB":56.50,"DZD":134.0,"XOF":553.0,
    "XAF":553.0,"ZMW":25.80,"MWK":1730.0,"MZN":63.80,"AOA":833.0,
    "SDG":601.0,"RWF":1310.0,"TND":3.0800,"LYD":4.8200,"MUR":44.20,
    "SCR":13.80,"BWP":13.60,"NAD":18.70,"SZL":18.70,"LSL":18.70,
    "ZWL":322.0,"CDF":2750.0,"GMD":67.50,"GNF":8600.0,"SLL":19750.0,
    "LRD":189.0,"CVE":101.0,"STN":21.70,"DJF":177.0,"ERN":15.00,
    "SOS":571.0,"KMF":452.0,"MGA":4480.0,"MRU":39.50,
    "ISK":138.0,"ALL":96.10,"BAM":1.8000,"MKD":56.70,"MDL":17.90,
    "BYN":3.2400,
    "PEN":3.7800,"UYU":39.50,"PYG":7340.0,"BOB":6.9100,"VES":36.50,
    "GTQ":7.8000,"HNL":24.70,"NIO":36.60,"CRC":520.0,"PAB":1.0000,
    "DOP":58.80,"CUP":24.00,"JMD":155.0,"TTD":6.7800,"BBD":2.0000,
    "BSD":1.0000,"BZD":2.0000,"GYD":209.0,"SRD":36.30,"HTG":132.0,
    "AWG":1.7900,"ANG":1.7900,"KYD":0.8330,"XCD":2.7000,
    "FJD":2.2400,"PGK":3.7400,"WST":2.7200,"TOP":2.3300,
    "VUV":119.0,"SBD":8.3800,
}

# ── FALLBACK NEWS (shown when API key not set or API fails) ───────────────────
FALLBACK_NEWS = [
    {"id":1,"impact":"High Impact","title":"Federal Reserve Signals Potential Rate Cut in 2025","desc":"Fed officials hint at possible interest rate reduction as inflation shows signs of cooling, impacting US Dollar strength globally.","tags":["USD","EUR","GBP"],"source":"Reuters","published_at":"2h ago","url":"#"},
    {"id":2,"impact":"High Impact","title":"ECB Maintains Hawkish Stance on Monetary Policy","desc":"European Central Bank keeps rates steady, emphasizing commitment to bringing inflation back to 2% target amid economic uncertainty.","tags":["EUR","USD"],"source":"Bloomberg","published_at":"4h ago","url":"#"},
    {"id":3,"impact":"High Impact","title":"Japanese Yen Strengthens on BOJ Policy Speculation","desc":"Market speculation about Bank of Japan ending negative interest rates drives yen appreciation against major currencies.","tags":["JPY","USD"],"source":"Financial Times","published_at":"6h ago","url":"#"},
    {"id":4,"impact":"Medium Impact","title":"UK Inflation Data Beats Expectations","desc":"British pound gains after CPI data shows inflation declining faster than economists predicted.","tags":["GBP","EUR"],"source":"CNBC","published_at":"8h ago","url":"#"},
    {"id":5,"impact":"Medium Impact","title":"Australian Dollar Rises on Strong Employment Report","desc":"AUD/USD climbs as jobs data exceeds forecasts, reducing expectations for RBA rate cuts.","tags":["AUD","USD"],"source":"MarketWatch","published_at":"10h ago","url":"#"},
]

TICKER_PAIRS = [
    ("EUR","USD"),("GBP","USD"),("USD","INR"),
    ("USD","JPY"),("AUD","USD"),("USD","CAD"),
    ("EUR","GBP"),("USD","CHF"),
]

# Keywords used to detect which currencies a news article is about
CURRENCY_KEYWORDS = {
    "USD":["dollar","usd","fed","federal reserve","united states"],
    "EUR":["euro","eur","ecb","european central bank","eurozone"],
    "GBP":["pound","gbp","sterling","bank of england","boe","uk","britain"],
    "JPY":["yen","jpy","boj","bank of japan","japan"],
    "AUD":["australian dollar","aud","rba","reserve bank of australia"],
    "CAD":["canadian dollar","cad","bank of canada","canada"],
    "CHF":["swiss franc","chf","snb","switzerland"],
    "CNY":["yuan","cny","rmb","pboc","china","chinese"],
    "INR":["rupee","inr","rbi","india","indian"],
}

# ── EXCHANGE RATE CACHE ───────────────────────────────────────────────────────
_rate_cache = {
    "rates": FALLBACK_RATES.copy(),
    "last_updated": "",
    "timestamp": 0,
}
RATE_CACHE_DURATION = 60 * 60  # 1 hour

# ── NEWS CACHE ────────────────────────────────────────────────────────────────
_news_cache = {
    "articles": FALLBACK_NEWS.copy(),
    "timestamp": 0,  # 0 forces a fresh fetch on first request
}
NEWS_CACHE_DURATION = 15 * 60  # 15 minutes — news refreshes every 15 min


# ── HELPERS ───────────────────────────────────────────────────────────────────
def http_get(url):
    """Simple HTTP GET using only stdlib."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "CurrencyX/1.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        print(f"[CurrencyX] HTTP error for {url}: {e}")
        return None


def get_rates():
    """Return live exchange rates, cached for 1 hour."""
    now = time.time()
    if now - _rate_cache["timestamp"] > RATE_CACHE_DURATION:
        print("[CurrencyX] Fetching fresh exchange rates...")
        data = http_get("https://open.exchangerate-api.com/v6/latest/USD")
        if data and data.get("result") == "success":
            _rate_cache["rates"] = data["rates"]
            _rate_cache["last_updated"] = time.strftime(
                "%Y-%m-%dT%H:%M:%SZ", time.gmtime(data["time_last_update_unix"])
            )
            _rate_cache["timestamp"] = now
            print(f"[CurrencyX] Rates updated: {_rate_cache['last_updated']}")
        else:
            print("[CurrencyX] Using fallback rates")
    return _rate_cache["rates"]


def convert_currency(amount, from_code, to_code):
    """Same formula as original project: (amount / fromRate) * toRate"""
    rates     = get_rates()
    from_rate = rates.get(from_code, 1)
    to_rate   = rates.get(to_code, 1)
    return (amount / from_rate) * to_rate


def get_rate(from_code, to_code):
    return convert_currency(1, from_code, to_code)


def get_change_pct(from_code, to_code):
    seed = (hash(f"{from_code}{to_code}") % 200 - 100) / 10000
    val  = seed + math.sin(time.time() * 0.001 + hash(from_code) % 100) * 0.002
    return round(val * 100, 2)


def format_time_ago(published_at_str):
    """Convert date string to '2h ago' format.
    NewsData.io returns: '2026-03-08 10:30:00' or '2026-03-08T10:30:00Z'
    """
    try:
        s = published_at_str[:19].replace("T", " ")
        t = time.strptime(s, "%Y-%m-%d %H:%M:%S")
        diff = time.time() - time.mktime(t)
        if diff < 3600:
            return f"{int(diff // 60)}m ago"
        elif diff < 86400:
            return f"{int(diff // 3600)}h ago"
        else:
            return f"{int(diff // 86400)}d ago"
    except Exception:
        return "recently"


def detect_currency_tags(title, desc):
    """Detect which currencies are mentioned in a news article."""
    text = (title + " " + desc).lower()
    tags = []
    for code, keywords in CURRENCY_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            tags.append(code)
    return tags[:4] if tags else ["USD"]


def detect_impact(title, desc):
    """Determine impact level based on keywords in the article."""
    text = (title + " " + desc).lower()
    high_keywords = [
        "federal reserve", "ecb", "central bank", "rate cut", "rate hike",
        "interest rate", "boj", "bank of england", "inflation", "recession",
        "crisis", "crash", "surge", "plunge", "collapse"
    ]
    if any(kw in text for kw in high_keywords):
        return "High Impact"
    return "Medium Impact"


def fetch_news():
    """Fetch real forex news from NewsData.io (server-side, no CORS issues)."""
    url = (
        f"https://newsdata.io/api/1/news"
        f"?apikey={NEWSDATAIO_KEY}"
        f"&q=forex+currency+exchange+rate"
        f"&language=en"
        f"&category=business"
    )

    print("[CurrencyX] Calling NewsData.io API...")
    data = http_get(url)

    if data is None:
        print("[CurrencyX] NewsData.io returned no response")
        return None
    if data.get("status") != "success":
        print(f"[CurrencyX] NewsData.io error: {data}")
        return None

    results = data.get("results", [])
    if not results:
        print("[CurrencyX] NewsData.io returned 0 articles")
        return None

    articles = []
    print("[CurrencyX] Calling NewsData.io API...", flush=True)
    for i, a in enumerate(results[:10]):
        print(a, flush=True)
        title = a.get("title", "") or ""
        desc  = a.get("description", "") or a.get("content", "") or ""
        desc  = desc[:180] + "..." if len(desc) > 180 else desc
        articles.append({
            "id":           i + 1,
            "impact":       detect_impact(title, desc),
            "title":        title,
            "desc":         desc,
            "tags":         detect_currency_tags(title, desc),
            "source":       a.get("source_id", "News").replace("-", " ").title(),
            "published_at": format_time_ago(a.get("pubDate", "")),
            "url": a.get("link") or a.get("source_url") or "#",
        })

    print(f"[CurrencyX] Fetched {len(articles)} articles from NewsData.io")
    return articles


def get_news():
    """Return news articles, refreshed every 15 minutes."""
    now = time.time()
    if now - _news_cache["timestamp"] > NEWS_CACHE_DURATION:
        print("[CurrencyX] Refreshing news...")
        articles = fetch_news()
        if articles:
            _news_cache["articles"] = articles
            _news_cache["timestamp"] = now
        else:
            # Use fallback but still update timestamp to avoid hammering the API
            _news_cache["timestamp"] = now
    return _news_cache["articles"]


# ── API ROUTES ────────────────────────────────────────────────────────────────
@app.route("/api/rates")
def api_rates():
    rates = get_rates()
    return jsonify({"base":"USD","rates":rates,"last_updated":_rate_cache["last_updated"],"timestamp":time.time()})


@app.route("/api/convert")
def api_convert():
    from_code = request.args.get("from", "USD").upper()
    to_code   = request.args.get("to",   "EUR").upper()
    try:
        amount = float(request.args.get("amount", 1))
    except ValueError:
        return jsonify({"error": "Invalid amount"}), 400

    rates = get_rates()
    if from_code not in rates or to_code not in rates:
        return jsonify({"error": "Unknown currency code"}), 400

    return jsonify({
        "from": from_code, "to": to_code,
        "amount": amount,
        "rate": round(get_rate(from_code, to_code), 6),
        "result": round(convert_currency(amount, from_code, to_code), 4),
        "last_updated": _rate_cache["last_updated"],
        "timestamp": time.time()
    })


@app.route("/api/ticker")
def api_ticker():
    return jsonify([{
        "pair": f"{f}/{t}", "from": f, "to": t,
        "rate": round(get_rate(f, t), 4),
        "change": get_change_pct(f, t)
    } for f, t in TICKER_PAIRS])


@app.route("/api/news")
def api_news():
    return jsonify(get_news())


@app.route("/api/currencies")
def api_currencies():
    rates = get_rates()
    # Only serve currencies we have rate data for
    return jsonify([
        {"code": code, "name": CURRENCY_NAMES.get(code, code), "symbol": CURRENCY_SYMBOLS.get(code, code)}
        for code in CURRENCY_NAMES
        if code in rates
    ])


@app.route("/api/debug/news")
def debug_news():
    """Debug endpoint — shows raw GNews API response."""
    import urllib.parse
    key = NEWSDATAIO_KEY
    query = "forex currency exchange rate central bank"
    url = (
        f"https://gnews.io/api/v4/search"
        f"?q={urllib.parse.quote(query)}"
        f"&lang=en"
        f"&max=10"
        f"&sortby=publishedAt"
        f"&apikey={key}"
    )
    data = http_get(url)
    return jsonify({"url_called": url.replace(key, "***HIDDEN***"), "response": data})


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    print("\n  💱 CurrencyX — Starting up...")
    get_rates()
    get_news()
    print("  🚀 CurrencyX is running!")
    print("  ➜  Open http://localhost:5000 in your browser\n")
    app.run(debug=True, port=5000)
