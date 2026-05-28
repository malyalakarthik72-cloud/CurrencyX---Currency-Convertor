# CurrencyX 💱

A real-time currency converter web application built with Flask and Python, featuring live exchange rates, forex news integration, and support for 145+ world currencies.

---

## 🚀 Features

- **Real-time Exchange Rates** — Fetches live rates from Open Exchange Rate API with 1-hour server-side caching
- **145+ Currencies** — Covers major, minor, and exotic currencies across all regions
- **Forex News** — Live forex news powered by NewsData.io, refreshed every 15 minutes
- **Fallback System** — Graceful fallback rates and news when APIs are unavailable
- **Currency Ticker** — Live ticker showing major currency pairs with change percentages
- **Conversion History** — Tracks recent conversions in the session
- **Responsive UI** — Clean, modern interface built with HTML, CSS, and JavaScript

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask |
| Frontend | HTML, CSS, JavaScript |
| Exchange Rates API | Open Exchange Rate API (free, no key needed) |
| News API | NewsData.io (free tier, 200 req/day) |
| Production Server | Gunicorn |
| Containerization | Docker |
| Deployment | Render |

---

## 📁 Project Structure

```
CurrencyX/
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── Dockerfile              # Docker container configuration
├── .dockerignore           # Files excluded from Docker image
├── static/
│   ├── style.css           # Application styles
│   └── script.js           # Frontend logic
└── templates/
    └── index.html          # Main HTML template
```

---

## ⚙️ How It Works

### Exchange Rates
- Fetches USD-based rates from `open.exchangerate-api.com` (free, no API key required)
- Rates are cached server-side for 1 hour to minimize API calls
- Falls back to hardcoded rates if API is unreachable

### Forex News
- Fetches live forex/currency news from NewsData.io
- Server-side caching for 15 minutes
- Automatically detects which currencies each article is about
- Classifies articles as High Impact or Medium Impact based on keywords
- Falls back to static news if API fails

### Currency Conversion Formula
```
result = (amount / fromRate) * toRate
```
All rates are USD-based, so conversion goes through USD as the base.

---

## 🏃 Running Locally

### Prerequisites
- Python 3.12+
- pip

### Steps

```bash
# Clone the repository
git clone https://github.com/yourusername/currencyX.git
cd currencyX

# Install dependencies
pip install -r requirements.txt

# Set your NewsData.io API key
# Get a free key at https://newsdata.io/register

# On Windows
set NEWSDATAIO_KEY=your_api_key_here

# On Linux/Mac
export NEWSDATAIO_KEY=your_api_key_here

# Run the app
python app.py
```

Open `http://localhost:5000` in your browser.

---

## 🐳 Running with Docker

### Prerequisites
- Docker Desktop installed

### Build and Run

```bash
# Build the Docker image
docker build -t currencyx .

# Run the container
docker run -p 5000:5000 -e NEWSDATAIO_KEY=your_api_key_here currencyx
```

Open `http://localhost:5000` in your browser.

### Useful Docker Commands

```bash
# Check running containers
docker ps

# View container logs
docker logs <container_id>

# Stop the container
docker stop <container_id>

# Remove the container
docker rm <container_id>
```

---

## ☁️ Deployment (Render)

CurrencyX is deployed on Render using the following architecture:

```
User → Render → Gunicorn → Flask App
```

- Deployed as a **Web Service** on Render
- Render automatically detects the `Dockerfile` and builds the container
- **Gunicorn** serves the Flask app with 4 worker processes
- Environment variables (API keys) set securely via Render dashboard

---

## 🌍 Supported Currency Regions

- **Major / G10** — USD, EUR, GBP, JPY, AUD, CAD, CHF, CNY, NZD, HKD
- **Asia-Pacific** — INR, KRW, THB, IDR, MYR, PHP, SGD, TWD and more
- **Middle East** — AED, SAR, QAR, KWD, BHD, OMR and more
- **Africa** — ZAR, NGN, KES, GHS, EGP, MAD and more
- **Europe (non-euro)** — RUB, TRY, PLN, CZK, HUF, RON and more
- **Americas** — MXN, BRL, COP, ARS, CLP, PEN and more
- **Pacific** — FJD, PGK, WST, TOP and more

---

## 📡 API Endpoints

| Endpoint | Description |
|---|---|
| `GET /` | Main application page |
| `GET /api/rates` | All exchange rates (USD base) |
| `GET /api/convert?from=USD&to=INR&amount=100` | Convert currency |
| `GET /api/ticker` | Major currency pair ticker |
| `GET /api/news` | Latest forex news |
| `GET /api/currencies` | List of all supported currencies |

---

## 🔑 Environment Variables

| Variable | Description | Required |
|---|---|---|
| `NEWSDATAIO_KEY` | NewsData.io API key for live news | Optional (falls back to static news) |

---


## 📄 License

This project is built for academic purposes as part of the B.Tech CSE curriculum at Sreyas Institute of Engineering and Technology.
