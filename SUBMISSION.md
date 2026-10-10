# SerpApi India Hackathon 2026 — submission fields (pre-drafted)

Official page: https://serpapi.github.io/serpapi-india-hackathon-2026/
Deadline: **October 10, 2026 at 23:59 IST** (verified on the official site, 2026-10-10)
Submit via: sign in with GitHub on the site → submission dashboard → "Submit project"

## Project

- **Name:** PrizeRadar India
- **Tagline:** A SerpApi-powered radar that finds prize hackathons, contests and
  quizzes open in India, extracts prize money + deadlines from live search data,
  and ranks what to hit first.
- **Track:** Research & AI
  (alternatives on the form, pick one: Travel & planning, Shopping & prices,
  Jobs & automation, Video & creators, SEO & search visibility)
- **Repo:** public GitHub repo (to be pushed — suggested name `prizeradar-india`)
  with README setup instructions. ✅ ready locally at ~/workspace/serpapi-prizeradar/
- **Demo video:** under 3 minutes, screen recording of the project running locally,
  public or unlisted link. Script ready in `demo_script.md`. ⏳ to be recorded.
- **Description (for the form):**
  > PrizeRadar India solves a real, personal problem: prize opportunities for
  > Indian students and builders — hackathons, coding contests, myGov quizzes,
  > pitch competitions — are scattered across dozens of sites, and deadlines get
  > missed. PrizeRadar queries live Google Search through SerpApi, extracts prize
  > amounts (₹/INR/$/lakh/crore) and deadline dates from the results, scores each
  > opportunity by prize-per-day until deadline with a closing-soon boost, and
  > renders a deadline-sorted HTML report. SerpApi is the core data source: every
  > row in the report originates from a SerpApi search response — without search
  > data there is no radar. Stdlib-only Python, no dependencies, MIT licensed.
  > A free SerpApi account (250 searches/month) runs a full radar sweep for
  > under 5 credits.

## Disclosures

- **Existing project?** No — built fresh for this hackathon on 2026-10-10.
- **AI tools used:** Muse (Meta's personal AI assistant) — wrote the code from a
  human-directed spec. (Required disclosure; AI-assisted development is allowed
  and does not affect judging.)

## Participant details (lead fills on the form)

- Name, email, phone, occupation, years of experience — lead participant's own.
- Eligibility: India residents aged 18+. (Confirm on the form.)

## Judging criteria — how this maps

1. **Idea strength:** scattered prize info → one ranked radar. Clear, real pain.
2. **Originality:** deadline-aware expected-value ranking (prize/day + closing-soon
   boost), India-specific, heuristic parsing with honest "verify on page" fallbacks.
3. **Technical complexity:** SerpApi integration, dedupe, regex prize/date extraction
   with INR normalisation, scoring, self-contained HTML report generation.
4. **Usefulness:** directly useful — built by someone actively hunting prizes.
5. **Meaningful SerpApi use:** search data is the entire input; no SerpApi = no product.

## Remaining steps (in order)

1. ⏳ **Sam10's go** — this is the only decision.
2. ⏳ Free SerpApi signup (serpapi.com, ~2 min, no card) → API key → run `--live`
   once to confirm real data flows.
3. ⏳ Push repo to GitHub (public) — GitHub `swarnnim` is signed in the browser.
4. ⏳ Record demo per `demo_script.md` (≤3 min), upload public/unlisted.
5. ⏳ Submit via the hackathon dashboard (GitHub sign-in; draft can be saved first).
