"""
Build the list of new southern Chinese restaurants in Paris (+ halal sub-list).

    # full run: web agent -> Paris location check -> report
    python run.py

    # re-use a saved candidate list instead of calling the agent
    python run.py --input candidates.json

    # only keep places within 3 km of a point (address or 'lat,lon')
    python run.py --input candidates.json --near "Châtelet, Paris" --radius-km 3

Outputs in --out (default ./output): restaurants.json, restaurants.csv, report.html
"""

import argparse
import csv
import html
import json
import os
import unicodedata

import location

FIELDS = ["name", "address", "arrondissement", "cuisine", "region", "southern", "opened",
          "new_confidence", "price", "halal", "halal_note", "distance_km", "lat", "lon",
          "summary", "sources"]


def _key(name):
    s = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode().lower()
    return "".join(ch for ch in s if ch.isalnum())


def dedupe(entries):
    seen = {}
    for e in entries:
        k = _key(e["name"])
        if k in seen:
            seen[k]["sources"] = sorted(set(seen[k]["sources"]) | set(e.get("sources", [])))
        else:
            seen[k] = dict(e)
    return list(seen.values())


def localize_all(entries, near=None, radius_km=None):
    """Geocode each entry; drop anything outside Paris (or outside the radius)."""
    kept, dropped = [], []
    for e in entries:
        loc = location.localize(e.get("address"), e.get("name"), near)
        e.update(lat=loc["lat"], lon=loc["lon"], distance_km=loc["distance_km"])
        e["arrondissement"] = loc["arrondissement"] or e.get("arrondissement")
        if loc["in_paris"] is False:
            dropped.append((e["name"], "outside Paris: " + loc["osm_address"]))
        elif radius_km is not None and loc["distance_km"] is not None and loc["distance_km"] > radius_km:
            dropped.append((e["name"], f"{loc['distance_km']} km away"))
        else:
            # not geocoded -> keep but flag, so a human can check the address
            e["location_checked"] = loc["geocoded"]
            kept.append(e)
    return kept, dropped


def write_csv(entries, path):
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS + ["list"], extrasaction="ignore")
        w.writeheader()
        for e in entries:
            w.writerow({**e, "sources": " | ".join(e.get("sources", [])), "list": e["list"]})


def _rows(entries):
    out = []
    for e in entries:
        links = " ".join(f'<a href="{html.escape(u)}" target="_blank" rel="noopener">[{i + 1}]</a>'
                         for i, u in enumerate(e.get("sources", [])))
        arr = f"{e['arrondissement']}e" if e.get("arrondissement") else "?"
        maps = (f' <a href="https://www.openstreetmap.org/?mlat={e["lat"]}&mlon={e["lon"]}#map=18/'
                f'{e["lat"]}/{e["lon"]}" target="_blank" rel="noopener">map</a>') if e.get("lat") else ""
        flag = "" if e.get("location_checked", True) else ' <span class="warn">address not verified</span>'
        halal = e.get("halal", "unknown")
        dist = f"<br><small>{e['distance_km']} km</small>" if e.get("distance_km") is not None else ""
        out.append(
            f"<tr><td><strong>{html.escape(e['name'])}</strong><br><small>{html.escape(e.get('summary') or '')}</small></td>"
            f"<td data-sort=\"{e.get('arrondissement') or 99:02d}\">{arr}{dist}</td>"
            f"<td>{html.escape(e.get('cuisine') or '')}<br><small>{html.escape(e.get('region') or '')}</small></td>"
            f"<td>{html.escape(e.get('opened') or '?')}<br><small>confidence: {e.get('new_confidence', '?')}</small></td>"
            f"<td>{html.escape(e.get('price') or '')}</td>"
            f"<td><span class=\"tag {halal}\">{halal}</span><br><small>{html.escape(e.get('halal_note') or '')}</small></td>"
            f"<td><small>{html.escape(e.get('address') or '')}</small>{maps}{flag}</td>"
            f"<td>{links}</td></tr>"
        )
    return "\n".join(out)


TABLE_HEAD = ("<thead><tr><th>Restaurant</th><th>Arr.</th><th>Cuisine</th><th>Opened</th>"
              "<th>Price</th><th>Halal</th><th>Address</th><th>Sources</th></tr></thead>")


def write_html(southern, halal, path, generated):
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "report_template.html"),
              encoding="utf-8") as f:
        tpl = f.read()
    page = (tpl.replace("{{GENERATED}}", html.escape(generated))
               .replace("{{N_SOUTH}}", str(len(southern)))
               .replace("{{N_HALAL}}", str(len(halal)))
               .replace("{{HEAD}}", TABLE_HEAD)
               .replace("{{SOUTH_ROWS}}", _rows(southern))
               .replace("{{HALAL_ROWS}}", _rows(halal)))
    with open(path, "w", encoding="utf-8") as f:
        f.write(page)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--input", help="JSON list of candidates (skips the web agent)")
    ap.add_argument("--months", type=int, default=18, help="how recent counts as 'new' (agent only)")
    ap.add_argument("--max-searches", type=int, default=25)
    ap.add_argument("--near", help="reference point: address or 'lat,lon'")
    ap.add_argument("--radius-km", type=float)
    ap.add_argument("--out", default="output")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)

    if args.input:
        with open(args.input, encoding="utf-8") as f:
            entries = json.load(f)
    else:
        import agent
        entries, notes = agent.run(args.months, args.max_searches)
        with open(os.path.join(args.out, "agent_notes.md"), "w", encoding="utf-8") as f:
            f.write(notes)

    near = location.parse_point(args.near) if args.near else None
    entries, dropped = localize_all(dedupe(entries), near, args.radius_km)
    for name, why in dropped:
        print(f"dropped {name}: {why}")

    def by_area(e):
        return (e.get("distance_km") or 0, e.get("arrondissement") or 99, e["name"])

    southern = sorted((e for e in entries if e.get("southern")), key=by_area)
    halal = sorted((e for e in entries if e.get("halal") in ("certified", "claimed")),
                   key=lambda e: (e["halal"] != "certified",) + by_area(e))
    for e in entries:
        e["list"] = "+".join(n for n, l in (("southern", southern), ("halal", halal)) if e in l) or "other"

    import datetime
    generated = datetime.date.today().isoformat()
    if near:
        generated += f" · within {args.radius_km} km of {args.near}" if args.radius_km else f" · distances from {args.near}"
    with open(os.path.join(args.out, "restaurants.json"), "w", encoding="utf-8") as f:
        json.dump({"southern": southern, "halal": halal, "dropped": dropped}, f, ensure_ascii=False, indent=2)
    write_csv(entries, os.path.join(args.out, "restaurants.csv"))
    write_html(southern, halal, os.path.join(args.out, "report.html"), generated)
    print(f"{len(southern)} southern Chinese, {len(halal)} halal -> {args.out}/report.html")


if __name__ == "__main__":
    main()
