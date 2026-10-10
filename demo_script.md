# Demo video script — PrizeRadar India (target ≤ 2:30, hard cap 3:00)

Simple screen recording. Narration optional; on-screen text is enough.
"Video quality does not affect judging" — clarity of the working features does.

## Shot list

**0:00–0:15 — The problem (terminal or README on screen)**
> "Prize money in India is scattered across hackathon sites, myGov quizzes,
> coding contests. Deadlines get missed. PrizeRadar finds them with live
> search and ranks what to hit first."

**0:15–0:45 — Demo mode run**
- Terminal: `python3 prizeradar.py --demo`
- Show the ranked table printing: 8 opportunities, prizes in INR, deadlines,
  closing-today items boosted to the top.
- Say/show: "Demo mode uses bundled sample SerpApi responses — same schema
  as the live API."

**0:45–1:30 — Live mode (needs SERPAPI_API_KEY)**
- `export SERPAPI_API_KEY=...` then `python3 prizeradar.py --live --max 2`
- Show the real SerpApi queries going out and fresh results arriving.
- Point out: 2 queries = 2 of the 250 free monthly credits.

**1:30–2:10 — The HTML report**
- Open `prize_radar_report.html` in the browser.
- Scroll the deadline-sorted table; click one link to show it goes to the
  real opportunity page.
- Note the honesty line: unparseable rows say "verify on page".

**2:10–2:30 — Close**
- "Every row comes from live SerpApi search data — without it there is no
  radar. Code is MIT, stdlib-only Python, on GitHub."
- End screen: repo URL.

## Recording notes
- Record at 1080p, terminal font ≥ 16pt.
- If live mode isn't possible at record time, demo mode alone still shows
  all core functionality (say so on screen).
- Upload as public or unlisted; test the link in an incognito window.
