# New southern Chinese restaurants in Paris

Agent that searches the web for recently opened **southern Chinese** restaurants in Paris
(Cantonese, Hong Kong, Teochew, Hakka, Fujian, Hainanese, Guangxi, Yunnan; Hunan flagged as
south-central) and builds a separate **halal** sub-list. Every result is geocoded and checked
against the Paris city boundary, so places in the suburbs are dropped.

## Files

| File | What it does |
|---|---|
| `agent.py` | Claude (`claude-opus-5-5`) with server-side web search + web fetch. Starts with TripAdvisor (search results only, it blocks page fetches), then Le Fooding, Time Out, Sortir à Paris, Paris Zigzag, press and TheFork. A second call turns the notes into JSON. |
| `location.py` | Paris location check with OpenStreetMap Nominatim: geocodes the address, tests it against the Paris boundary polygon (OSM relation 7444), works out the arrondissement, and gives the distance from a reference point. Rate limited to 1 request/s and cached in `.geocache.json`. |
| `run.py` | Pipeline: agent (or `--input` JSON), then dedupe, location check, sort, and write `output/restaurants.json`, `restaurants.csv`, `report.html`. |
| `report_template.html` | Template for the HTML report (search box, arrondissement filter, sortable columns). |
| `seed_2026-10.json` | Candidate list researched in October 2026, usable with `--input`. |

## Usage

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=...                     # or `ant auth login`
export NOMINATIM_USER_AGENT="my-app/1.0 (me@example.com)"   # Nominatim asks for a contact

python run.py                                    # full web run (about 25 searches)
python run.py --months 12 --max-searches 40      # stricter "new", deeper search
python run.py --input seed_2026-10.json          # no API call, just location check + report
python run.py --input seed_2026-10.json --near "Châtelet, Paris" --radius-km 3

python location.py "48 avenue d'Ivry 75013"      # check one address
python location.py "Belleville" --near "48.8566,2.3522" --radius-km 2
```

`--near` takes an address or `lat,lon`. With `--radius-km`, places further away are dropped;
without it, the distance is shown and the list is sorted by it.

## Notes

- Opening dates and halal status come from the cited sources. *Certified* means a named
  certifier was found; *claimed* means only the menu, reviews or social media say so.
- Entries whose address could not be geocoded are kept and marked "address not verified".
- The agent uses server-side refusal fallbacks (`fallbacks: "default"`), so a declined request
  is retried on another model automatically.
