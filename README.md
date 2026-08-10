# SAT module simulator

> **Disclosure:** this is not an original idea — it's a practice interface over College Board's
> own published question bank — and most of the code was written with Claude Code. I designed
> what it should do, tested it, and use it myself, and I'm responsible for how it behaves.
> Not affiliated with, endorsed by, or connected to College Board.

Timed digital-SAT practice modules built on the **SAT Suite Educator Question Bank** —
3,255 official questions with College Board's own explanations, laid out and timed the way
Bluebook does it.

I built this because I was practising in sets of ten questions and tracking my mistakes in a
spreadsheet, which tells you nothing about pacing, and because I didn't want to burn one of
my six real practice tests every time I wanted to try a new approach.

**[Open it →](#)** *(add your URL here)*

---

## It doesn't host any questions

The app ships as a single HTML page with no question data in it. Your browser fetches
questions from College Board's public question-bank API directly and caches them locally, so
this is a **client, not a mirror** — it never stores or redistributes their content.

- **First visit:** 3 requests — two metadata lists and the active-items lookup — which is
  enough to build any module.
- **Starting a module:** only the questions you're about to see get fetched. 27 for a Reading
  and Writing module, 98 for a whole test. Takes a second or two.
- **After that:** everything is cached in IndexedDB, so a returning visit re-fetches nothing.
- **Optional:** "Cache everything for offline" pulls the whole bank in about two minutes and
  the app then works with no connection at all.

## Exclude active questions ← the important one

College Board flags **2,022 of the 3,255** questions as *active* — still in use on test forms,
and therefore the ones that can spoil a practice test you haven't taken yet. Their own bank UI
has an "Exclude Active Questions" checkbox for exactly this reason.

This app has the same switch, and it is **on by default.** With it on you practise from the
1,233 retired questions (746 R&W, 487 Math) — roughly 27 R&W modules and 22 Math modules
before anything repeats. The flags are re-fetched weekly, because College Board rotates which
items are active and a frozen copy quietly stops protecting you.

Turning it off warns you. Don't, unless you've already used every practice test.

## What you get

**Full length** — a complete 98-question test: R&W Module 1 + 2, a 10-minute break, Math
Module 1 + 2, at real timing (32 / 32 / 35 / 35 minutes).

**Single module** — one module on its own, correct length and clock.

**Custom drill** — pick section, domains, difficulty, question count and time limit.

Modules follow the real blueprint rather than drawing at random:

| | Reading and Writing | Math |
|---|---|---|
| Questions | 27 | 22 |
| Domain split | 7 Craft and Structure / 6 Information and Ideas / 8 Standard English Conventions / 6 Expression of Ideas | 7 Algebra / 7 Advanced Math / 4 Problem-Solving and Data Analysis / 4 Geometry and Trigonometry |
| Order | grouped by domain, easy→hard within each | mixed domains, roughly ascending difficulty |
| Grid-ins | — | 6, placed at the end |

## Bluebook behaviour

- Countdown timer with hide/show, red under 5:00 — and it only starts once questions are
  actually on screen, so loading never eats your clock
- Mark for Review, and the question-navigator grid
- The **ABC** answer eliminator
- "Check Your Work" review page before you commit to a module
- Grid-in entry with answer preview, accepting fractions or decimals — including a repeating
  value truncated *or* rounded to fill the field, which is the real rule
- Math reference sheet; the Calculator button opens Desmos test mode
- Keyboard: `A`–`D` to answer, `←`/`→` to move, `M` to mark

## Results

Raw score, accuracy, and breakdowns by domain, by skill, and by difficulty — then every
question you missed with the official explanation. History is kept locally, and new sessions
prefer questions you haven't seen.

**There is deliberately no 200–800 score.** The bank is a flat pool: not adaptive, not equated.
Any scaled number derived from it would be invented, and an invented score is worse than no
score. Read the domain table instead.

## Honest limitations

- **Module 2 is an approximation.** The real test adapts to your Module 1 performance. Here
  it's a difficulty-weighted draw: ≥60% on Module 1 routes you to the harder set. It's
  labelled in the UI so you always know which route you're on.
- **"Active" is College Board's label**, and it's the best signal available — but it's their
  flag, not a guarantee about any specific Bluebook form.
- 459 items are skipped because they embed their math as images rather than text. Those come
  from the disclosed paper tests, so leaving them out is a second layer of spoiler protection.
- No Desmos embedded, no annotation/highlighter tool.
- If College Board changes or closes the API, the app breaks. See below.

## Running it locally

No build step, no dependencies. Serve the folder over HTTP (the API needs a real origin, so
`file://` won't do):

```bash
python3 -m http.server 8000
```

Then open `http://localhost:8000`.

## If the API ever goes away

`refresh_questions.py` downloads the whole bank into a `questions.js` bundle:

```bash
python3 refresh_questions.py questions.js
```

The hosted app never uses that file — but if College Board adds authentication or blocks
cross-origin requests, the error screen offers a file picker that loads your bundle instead,
and everything keeps working. A bundle is treated as a lifeboat: once the API is reachable
again the app goes back to the live bank on its own.

`questions.js` is **gitignored on purpose.** It contains College Board's copyrighted content;
committing it would turn this repo into the mirror this design exists to avoid.

Refresh just the active-question flags (a few seconds, no content re-downloaded):

```bash
python3 refresh_questions.py questions.js --annotate
```

## The API

Undocumented, public, unauthenticated, and `Access-Control-Allow-Origin: *`, which is what
makes the no-backend design possible.

| Endpoint | Purpose |
|---|---|
| `POST .../questionbank/digital/get-questions` | `{"asmtEventId":99,"test":1\|2,"domain":"..."}` — metadata for every question |
| `POST .../questionbank/digital/get-question` | `{"external_id":"..."}` — one question's content |
| `GET .../questionbank/lookup` | `readingLiveItems` / `mathLiveItems` — the active-question ids |

Base: `https://qbank-api.collegeboard.org/msreportingquestionbank-prod`

Two things worth knowing if you build on this:

- The metadata does **not** say whether a question is multiple-choice or a grid-in, but module
  building needs that before fetching content. `gridins.js` is a 4.5 KB list of math grid-in
  *identifiers* (no content) used to seed the guess; the app corrects itself from the real
  content as it loads.
- Question content uses MathML with `<mfenced>`, which was dropped from MathML Core — Chrome
  and Safari won't render it. It has to be rewritten into explicit `<mo>` delimiters or half
  the math silently loses its parentheses.

Please be gentle with their servers: this app caches aggressively and fetches at most a
module at a time for exactly that reason.

## Content and licensing

The **code** in this repo is MIT licensed — see `LICENSE`.

The **questions are not mine and are not covered by that licence.** They're College Board's,
published for educator use, and they're fetched by your browser from College Board rather
than served from here. SAT® and Bluebook™ are registered trademarks of College Board, which
has no involvement in this project.
