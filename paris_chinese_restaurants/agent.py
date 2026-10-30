"""
Web research agent: asks Claude (with Anthropic's server-side web search and
web fetch tools) to find newly opened southern Chinese restaurants in Paris,
plus halal Chinese options, then turns its notes into structured JSON.

Needs Anthropic API credentials (ANTHROPIC_API_KEY or an `ant auth login` profile).

TripAdvisor blocks automated page fetches, so the agent is told to use
search-result snippets for it and cross-check with press / guide sites.
"""

import datetime
import json

import anthropic

MODEL = "claude-opus-5-5"
BETAS = ["server-side-fallback-2026-07-01"]  # re-run on a fallback model if a request is declined

SOURCES = [
    "tripadvisor.fr / tripadvisor.com",
    "lefooding.com",
    "timeout.fr / timeout.com/paris",
    "sortiraparis.com",
    "pariszigzag.fr",
    "lefigaro.fr, leparisien.fr, telerama.fr (food sections)",
    "thefork.fr",
]

RESEARCH_PROMPT = """Today is {today}. Find Chinese restaurants in Paris intra-muros (the 20 \
arrondissements, postcodes 75001-75020 / 75116) that opened in the last {months} months.

Focus on SOUTHERN Chinese cuisines: Cantonese (dim sum, siu mei, roast meats), Hong Kong \
(cha chaan teng), Teochew/Chaozhou, Hakka, Fujian/Hokkien, Hainanese, Guangxi (luosifen, \
Guilin rice noodles), Yunnan. Hunan counts as south-central: include it but say so.

Separately, find HALAL Chinese restaurants in Paris (any region, e.g. Hui / Lanzhou lamian, \
Uyghur), new ones first. For each, say whether halal is certified (name the certifier) or only \
claimed (menu, reviews, social media).

Start with TripAdvisor (use search results; do not try to get around any blocking), then \
cross-check on: {sources}. Search in French and English.

For every restaurant give: name, full street address with postcode, cuisine and region, \
approximate opening date and which source says so, price range, halal status, and 1-3 source \
URLs. Do not invent details; say "unknown" instead. Skip places outside Paris city limits."""

ENTRY_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "address": {"type": ["string", "null"]},
        "cuisine": {"type": "string"},
        "region": {"type": "string"},
        "southern": {"type": "boolean"},
        "opened": {"type": ["string", "null"]},
        "new_confidence": {"type": "string", "enum": ["high", "medium", "low"]},
        "price": {"type": ["string", "null"]},
        "halal": {"type": "string", "enum": ["certified", "claimed", "no", "unknown"]},
        "halal_note": {"type": ["string", "null"]},
        "summary": {"type": "string"},
        "sources": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["name", "address", "cuisine", "region", "southern", "opened", "new_confidence",
                 "price", "halal", "halal_note", "summary", "sources"],
    "additionalProperties": False,
}

RESULT_SCHEMA = {
    "type": "object",
    "properties": {"restaurants": {"type": "array", "items": ENTRY_SCHEMA}},
    "required": ["restaurants"],
    "additionalProperties": False,
}


def _check(response):
    if response.stop_reason == "refusal":
        raise RuntimeError(f"Request declined: {response.stop_details}")
    if response.stop_reason == "max_tokens":
        raise RuntimeError("Response hit max_tokens before finishing")


def research(client, months=18, max_searches=25):
    """Phase 1: let Claude search and read the web. Returns its notes as text."""
    prompt = RESEARCH_PROMPT.format(today=datetime.date.today().isoformat(), months=months,
                                    sources=", ".join(SOURCES))
    tools = [
        {"type": "web_search_20260209", "name": "web_search", "max_uses": max_searches,
         "user_location": {"type": "approximate", "city": "Paris", "country": "FR",
                           "timezone": "Europe/Paris"}},
        {"type": "web_fetch_20260209", "name": "web_fetch", "max_uses": max_searches,
         "blocked_domains": ["tripadvisor.fr", "tripadvisor.com"]},
    ]
    messages = [{"role": "user", "content": prompt}]
    while True:
        with client.beta.messages.stream(
            model=MODEL, max_tokens=64000, betas=BETAS, fallbacks="default",
            output_config={"effort": "high"}, tools=tools, messages=messages,
        ) as stream:
            response = stream.get_final_message()
        if response.stop_reason == "pause_turn":
            # Server tools paused a long turn: send it back so the server continues
            messages.append({"role": "assistant", "content": response.content})
            continue
        _check(response)
        break
    return "\n".join(b.text for b in response.content if b.type == "text")


def structure(client, notes):
    """Phase 2: turn the research notes into validated JSON entries."""
    response = client.beta.messages.create(
        model=MODEL, max_tokens=16000, betas=BETAS, fallbacks="default",
        output_config={"effort": "low", "format": {"type": "json_schema", "schema": RESULT_SCHEMA}},
        messages=[{"role": "user", "content":
                   "Convert these research notes into the JSON schema. One entry per restaurant; "
                   "keep only facts present in the notes; use null when unknown.\n\n" + notes}],
    )
    _check(response)
    text = next(b.text for b in response.content if b.type == "text")
    return json.loads(text)["restaurants"]


def run(months=18, max_searches=25):
    client = anthropic.Anthropic()
    notes = research(client, months, max_searches)
    return structure(client, notes), notes
