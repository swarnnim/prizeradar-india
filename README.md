# 🎯 PrizeRadar India

A SerpApi-powered radar for prize opportunities open to people in India —
hackathons, coding contests, quizzes, pitch competitions. Live Google Search
data (via SerpApi) is the core: every opportunity in the report originates
from a SerpApi search response. Prize money and deadlines are extracted
heuristically, ranked by prize-per-day until deadline, and rendered as a
deadline-sorted HTML report.

Built for the **SerpApi India Hackathon 2026** (submit by Oct 10, 2026 23:59 IST).

## Setup

No dependencies beyond Python 3.8+ (stdlib only).

**Demo mode (no key needed):**
```bash
python3 prizeradar.py --demo
```
Uses bundled `demo_data/*.json` sample SerpApi responses (fixtures, clearly
labelled — not live data).

**Live mode (free SerpApi account):**
1. Create a free account at https://serpapi.com (250 searches/month, no card).
2. Copy your API key from the dashboard.
3. Run:
```bash
export SERPAPI_API_KEY="your_key_here"
python3 prizeradar.py --live            # 4 queries = 4 credits
python3 prizeradar.py --live --max 2    # fewer queries, fewer credits
```

Output:
- Ranked table printed to the terminal
- `prize_radar_report.html` — deadline-sorted report (open in any browser)

## How it works

1. `QUERIES` — a small, deliberate set of Google searches (each costs 1 credit).
2. `serpapi_search()` — calls `serpapi.com/search.json` with `gl=in, hl=en`.
3. `extract_prize_inr()` / `extract_deadline()` — heuristic parsing of
   ₹/INR/$/lakh/crore amounts and deadline dates from titles + snippets.
4. `score()` — prize-per-day until deadline, with a closing-soon (≤3d) boost.
5. `render_html()` — self-contained report, no server needed.

> Parsing is heuristic — always verify prize + deadline on the official page
> before acting. The report says this on every row it can't parse.

## AI tools used

Built with AI-assisted development: **Muse** (Meta's personal AI assistant)
wrote the code from a human-directed spec. No other AI tools.

## License

MIT — do what you want with it.
