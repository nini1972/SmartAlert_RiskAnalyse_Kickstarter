# SmartAlert Risk Analyse Kickstarter

SmartAlert is a Kickstarter investment and risk tracking app with:
- **FastAPI backend** (`backend/server.py`)
- **MongoDB** persistence
- **OpenAI-powered** project/portfolio analysis
- **React frontend** (`frontend/`)

## Run locally

### Backend
1. Create `backend/.env` with:
   - `MONGO_URL`
   - `DB_NAME`
   - `OPENAI_API_KEY`
2. Install Python dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```
3. Start API:
   ```bash
   cd backend
   uvicorn server:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend
```bash
cd frontend
npm install
npm start
```

## Kickstarter scraping approach

Kickstarter scraping now lives in:
- `backend/external_integrations/kickstarter.py`

It uses a resilient 3-layer extraction strategy:
1. **Structured data first**: parse embedded JSON/script payloads (e.g. `application/ld+json`, hydrated script state)
2. **Browser automation fallback**: use Playwright when client-rendered data is needed
3. **BeautifulSoup/lxml fallback**: parse HTML selectors as last resort

Additional reliability features:
- Request timeout handling
- Retry with exponential backoff
- Detailed logging of failures
- Lightweight disk cache (`/tmp/kickstarter_scrape_cache`)
- Pydantic validation (`KickstarterScrapedProject`) before scraped data is returned by the API

## Tests

Focused scraper robustness tests are in:
- `tests/test_kickstarter_scraper.py`
- `tests/fixtures/kickstarter_*.html`
