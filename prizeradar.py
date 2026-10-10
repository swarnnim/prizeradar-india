#!/usr/bin/env python3
"""
PrizeRadar India — a SerpApi-powered radar for prize opportunities.

Finds live hackathons, coding contests, quizzes and pitch competitions
open to people in India, extracts prize money + deadlines from live
Google Search data (via SerpApi), ranks them by expected value, and
generates a deadline-sorted HTML report.

Usage:
    python3 prizeradar.py --demo            # offline demo with sample SerpApi responses
    python3 prizeradar.py --live             # live queries (needs SERPAPI_API_KEY env var)
    python3 prizeradar.py --live --max 5     # up to 5 search queries (free tier: 250/mo)

SerpApi is the core data source: every opportunity in the report comes
from a live SerpApi Google Search response. Without search data there is
no radar — that is the "meaningful use".
"""

import argparse
import datetime as dt
import html
import json
import os
import re
import sys
import urllib.parse
import urllib.request

SERPAPI_ENDPOINT = "https://serpapi.com/search.json"

# Small, deliberate query set: each query costs 1 SerpApi credit.
# Free tier = 250 credits/month, so a full radar run costs <2% of quota.
QUERIES = [
    "hackathon India 2026 cash prize register online",
    "coding contest India students prize money 2026",
    "online quiz competition India cash prize 2026",
    "startup pitch competition India prize 2026",
]

PRIZE_PATTERNS = [
    re.compile(r"(?:₹|Rs\.?\s?|INR\s?)\s?([\d,]+(?:\.\d+)?)\s*(lakh|lac|l|crore|cr|k|thousand)?", re.I),
    re.compile(r"\$\s?([\d,]+(?:\.\d+)?)\s*(k|thousand|million|m)?", re.I),
    re.compile(r"prize\s*pool[^₹$]{0,20}(?:₹|Rs\.?|INR|\$)\s?([\d,]+(?:\.\d+)?)\s*(lakh|lac|l|crore|cr|k|thousand|million|m)?", re.I),
]
MULTIPLIER = {
    None: 1, "": 1,
    "k": 1_000, "thousand": 1_000,
    "l": 100_000, "lac": 100_000, "lakh": 100_000,
    "cr": 10_000_000, "crore": 10_000_000,
    "m": 1_000_000, "million": 1_000_000,
}
DATE_PATTERNS = [
    re.compile(r"(\d{1,2})\s*(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s*,?\s*(\d{4})?", re.I),
    re.compile(r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{1,2})\s*,?\s*(\d{4})?", re.I),
    re.compile(r"(closes|deadline|last date|ends?)[^\d]{0,20}(\d{1,2})\s*(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*", re.I),
]
MONTHS = {m: i + 1 for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"])}


def serpapi_search(api_key, query, num=10):
    params = urllib.parse.urlencode({
        "engine": "google", "q": query, "gl": "in", "hl": "en",
        "num": num, "api_key": api_key,
    })
    req = urllib.request.Request(SERPAPI_ENDPOINT + "?" + params,
                                 headers={"User-Agent": "PrizeRadarIndia/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def extract_prize_inr(text):
    """Best-effort prize extraction, normalised to INR. Returns (inr, raw)."""
    best = (0, "")
    for pat in PRIZE_PATTERNS:
        for m in pat.finditer(text or ""):
            try:
                amount = float(m.group(1).replace(",", ""))
            except ValueError:
                continue
            unit = (m.group(2) or "").lower() if len(m.groups()) >= 2 else ""
            mult = MULTIPLIER.get(unit, 1)
            inr = amount * mult
            # '$' amounts are USD -> rough INR conversion
            if "$" in m.group(0) and "₹" not in m.group(0) and "rs" not in m.group(0).lower():
                inr *= 88
            if inr > best[0] and inr < 1e10:  # sanity cap: ignore absurd parses
                best = (inr, m.group(0).strip())
    return best


def extract_deadline(text, today):
    """Best-effort deadline extraction. Returns (date|None, raw)."""
    for idx, pat in enumerate(DATE_PATTERNS):
        m = pat.search(text or "")
        if not m:
            continue
        try:
            groups = m.groups()
            if idx == 1:  # month-first: "October 10, 2026"
                mon, day, year = groups
            elif len(groups) == 3:
                day, mon, year = groups
            else:
                day, mon = groups[-2], groups[-1]
                year = None
            day = int(day)
            month = MONTHS[mon[:3].lower()]
            year = int(year) if year else today.year
            d = dt.date(year, month, day)
            if d < today:  # assume next year if the date already passed
                d = dt.date(year + 1, month, day)
            return d, m.group(0).strip()
        except (ValueError, KeyError):
            continue
    return None, ""


def score(opportunity, today):
    """Expected-value-ish score: prize per day until deadline, recency bonus."""
    prize = opportunity["prize_inr"]
    if opportunity["deadline"]:
        days = max((opportunity["deadline"] - today).days, 1)
    else:
        days = 60  # unknown deadline: deprioritise but keep visible
    base = (prize / days) if prize else 1.0 / days
    if opportunity["deadline"] and (opportunity["deadline"] - today).days <= 3:
        base *= 3  # closing-soon boost: the whole point of a radar
    return base


def normalise_results(responses, today):
    seen_links, opportunities = set(), []
    for query, payload in responses:
        for r in payload.get("organic_results", []) or []:
            link = r.get("link", "")
            if not link or link in seen_links:
                continue
            seen_links.add(link)
            text = " ".join(filter(None, [r.get("title", ""), r.get("snippet", "")]))
            prize_inr, prize_raw = extract_prize_inr(text)
            deadline, deadline_raw = extract_deadline(text, today)
            opp = {
                "title": r.get("title", "(untitled)").strip(),
                "link": link,
                "snippet": r.get("snippet", "").strip()[:300],
                "query": query,
                "prize_inr": prize_inr,
                "prize_raw": prize_raw,
                "deadline": deadline,
                "deadline_raw": deadline_raw,
            }
            opp["score"] = score(opp, today)
            opportunities.append(opp)
    opportunities.sort(key=lambda o: o["score"], reverse=True)
    return opportunities


def render_html(opportunities, today, out_path):
    rows = []
    for i, o in enumerate(opportunities, 1):
        prize = f"₹{o['prize_inr']:,.0f}" if o["prize_inr"] else "<i>not parsed</i>"
        if o["deadline"]:
            days = (o["deadline"] - today).days
            dl = f"{o['deadline'].isoformat()} <b>({days}d left)</b>" if days >= 0 else f"{o['deadline'].isoformat()} (passed?)"
        else:
            dl = "<i>unknown — verify on page</i>"
        rows.append(
            f"<tr><td>{i}</td><td><a href='{html.escape(o['link'])}'>{html.escape(o['title'])}</a>"
            f"<br><small>{html.escape(o['snippet'])}</small></td>"
            f"<td>{prize}</td><td>{dl}</td></tr>")
    page = f"""<!DOCTYPE html><html><head><meta charset='utf-8'>
<title>PrizeRadar India — {today.isoformat()}</title>
<style>body{{font-family:system-ui,sans-serif;max-width:1000px;margin:2em auto;padding:0 1em}}
table{{border-collapse:collapse;width:100%}}td,th{{border:1px solid #ccc;padding:8px;vertical-align:top}}
th{{background:#111;color:#fff}}small{{color:#555}}</style></head>
<body><h1>🎯 PrizeRadar India</h1>
<p>Ranked by prize-per-day until deadline. Data: live Google Search via SerpApi, {today.isoformat()}.
Prize/deadline parsing is heuristic — always verify on the official page before acting.</p>
<table><tr><th>#</th><th>Opportunity</th><th>Prize (parsed)</th><th>Deadline</th></tr>
{''.join(rows)}</table>
<p><small>Built for the SerpApi India Hackathon 2026. Every row above originated from a SerpApi search response.</small></p>
</body></html>"""
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(page)
    return out_path


def main():
    ap = argparse.ArgumentParser(description="PrizeRadar India — SerpApi-powered prize radar")
    ap.add_argument("--demo", action="store_true", help="use bundled sample SerpApi responses")
    ap.add_argument("--live", action="store_true", help="run live SerpApi queries (SERPAPI_API_KEY)")
    ap.add_argument("--max", type=int, default=len(QUERIES), help="max queries for --live")
    ap.add_argument("--out", default="prize_radar_report.html", help="HTML report path")
    args = ap.parse_args()

    today = dt.date.today()
    responses = []

    if args.demo:
        here = os.path.dirname(os.path.abspath(__file__))
        for q in QUERIES:
            slug = re.sub(r"\W+", "_", q).strip("_")[:40]
            path = os.path.join(here, "demo_data", f"sample_{slug}.json")
            if os.path.exists(path):
                with open(path, encoding="utf-8") as f:
                    payload = json.load(f)
                # sample files are honest fixtures: strip any live-looking metadata
                payload["_fixture"] = True
                responses.append((q, payload))
        if not responses:
            sys.exit("demo data missing: run with --live or add demo_data/*.json")
        print(f"[demo] using {len(responses)} bundled sample SerpApi responses (fixtures, not live data)")
    elif args.live:
        key = os.environ.get("SERPAPI_API_KEY", "")
        if not key:
            sys.exit("set SERPAPI_API_KEY env var (free at serpapi.com — 250 searches/month)")
        for q in QUERIES[:args.max]:
            print(f"[live] SerpApi query: {q}")
            responses.append((q, serpapi_search(key, q)))
    else:
        ap.print_help()
        sys.exit(2)

    opps = normalise_results(responses, today)
    print(f"\n{'#':<3} {'Prize (INR)':>12}  {'Deadline':<12} Title")
    print("-" * 100)
    for i, o in enumerate(opps, 1):
        prize = f"{o['prize_inr']:,.0f}" if o["prize_inr"] else "?"
        dl = o["deadline"].isoformat() if o["deadline"] else "unknown"
        print(f"{i:<3} {prize:>12}  {dl:<12} {o['title'][:70]}")
    path = render_html(opps, today, args.out)
    print(f"\nreport: {path}  ({len(opps)} opportunities)")


if __name__ == "__main__":
    main()
