# ModuleDrill

> **Disclosure:** this is not an original idea — it's a practice interface over College Board's
> own published question bank — and most of the code was written with Claude Code. I designed
> what it should do, tested it, and use it myself, and I'm responsible for how it behaves.
> Not affiliated with, endorsed by, or connected to College Board.

Timed digital-SAT practice modules built on the **SAT Suite Educator Question Bank** —
over 3,300 official questions with College Board's own explanations, laid out and timed the way
Bluebook does it.

I built this because I was practising in sets of ten questions and tracking my mistakes in a
spreadsheet, which tells you nothing about pacing, and because I didn't want to burn one of
my six real practice tests every time I wanted to try a new approach.

**[Open it →](https://moduledrill.com)**

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
  the app then works with no connection at all — questions, timer, results and all. The one
  exception is the calculator, which is Desmos's site and can't be cached with everything
  else; with no connection it says so rather than showing an empty panel.

## Exclude active questions ← the important one

College Board flags **roughly two thirds** of the questions as *active* — still in use on test forms,
and therefore the ones that can spoil a practice test you haven't taken yet. Their own bank UI
has an "Exclude Active Questions" checkbox for exactly this reason.

This app has the same switch, and it is **on by default.** With it on you practise only from
retired questions — comfortably more than 20 modules of each section
before anything repeats. The flags are re-fetched weekly, because College Board rotates which
items are active and a frozen copy quietly stops protecting you.

Turning it off warns you. Don't, unless you've already used every practice test.

## What you get

**Full length** — a complete 98-question test: R&W Module 1 + 2, a 10-minute break, Math
Module 1 + 2, at real timing (32 / 32 / 35 / 35 minutes).

**Single module** — one module on its own, correct length and clock.

**Custom drill** — pick section, domains, individual skills, difficulty, question count and
time limit. Skill counts are shown per chip, so you can see before starting whether a narrow
skill has enough retired questions to fill the drill.

**Your mistakes** — questions you got wrong, collected so you can drill them again. Answer one
correctly anywhere and it leaves the list.

**Vocabulary** — a three-minute word drill, described below.

Modules follow the real blueprint rather than drawing at random:

| | Reading and Writing | Math |
|---|---|---|
| Questions | 27 | 22 |
| Domain split | 7 Craft and Structure / 6 Information and Ideas / 8 Standard English Conventions / 6 Expression of Ideas | 7 Algebra / 7 Advanced Math / 4 Problem-Solving and Data Analysis / 4 Geometry and Trigonometry |
| Order | grouped by domain, easy→hard within each | mixed domains, roughly ascending difficulty |
| Grid-ins | — | 6, placed at the end |

## Vocabulary drill

Twelve questions, about three minutes, alternating between *what does this word mean?* and
*which word means this?*

The useful part is where the wrong answers come from. Every "Words in Context" question ships
four options that College Board's writers chose to be confusable with each other, so each
question becomes a ready-made four-way vocabulary item with professionally written
distractors. Ask what *invalidate* means and the decoys are *underscore*, *dispute* and
*withdraw* — *dispute* is a genuine near-miss. Pairing a word with three random others never
produces that.

**83 groups, 322 words**, drawn only from retired questions. A bare word isn't a spoiler, but
a group of four is a fingerprint of one specific question, so the same exclusion applies here
as everywhere else.

The definitions are written for the **SAT sense**, which is usually not a dictionary's first
one: *arbitrary* as "based on whim rather than reason", *facile* as "easy in a way that is
shallow". That distinction is the whole point of writing them for this project rather than
pulling from a dictionary API, which picks the wrong sense often enough to teach the wrong
thing. Like the rest of the code they were drafted with AI assistance and are still being
reviewed — corrections welcome.

Progress is a Leitner box per word: three correct in a row counts as known, one wrong sends it
back to the start. Each session is roughly a third new words and two thirds review, weighted
towards whatever you're weakest on — the first version took every new word before revisiting
any, which is a shuffled deck rather than spaced repetition.

`vocab.js` holds the words and their definitions and nothing else. **No College Board text is
stored**, and the sentences the words came from are deliberately left out: showing the sentence
*is* the question, so practising vocabulary would spoil it for you later in a module.

## Bluebook behaviour

- Countdown timer with hide/show, red under 5:00 — and it only starts once questions are
  actually on screen, so loading never eats your clock
- Mark for Review, and the question-navigator grid
- The **ABC** answer eliminator
- "Check Your Work" review page before you commit to a module
- Grid-in entry with answer preview, accepting fractions or decimals — including a repeating
  value truncated *or* rounded to fill the field, which is the real rule
- Math reference sheet, and College Board's own Desmos build in a draggable, resizable
  panel over the question — no tab switching. It loads only when you first open it, and
  remembers where you put it.
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
- No annotation/highlighter tool.
- The embedded calculator is the one part that needs a connection, and it's a third-party
  frame, so Desmos sees the visitor's IP like any embed would.
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

## Privacy

Your practice history, settings and cached questions live in **your own browser** —
IndexedDB and localStorage — and are never sent anywhere. There are no accounts and no
server, so there is nothing for me to see even if I wanted to.

The site uses Cloudflare Web Analytics, which is cookieless and counts page views,
referrers and countries without identifying anyone. That's the whole of the data
collection. Questions are requested by your browser from College Board directly, so those
requests go to them and not through this site.

## Content and licensing

The **code** in this repo is MIT licensed — see `LICENSE`.

The **questions are not mine and are not covered by that licence.** They're College Board's,
published for educator use, and they're fetched by your browser from College Board rather
than served from here. SAT® and Bluebook™ are registered trademarks of College Board, which
has no involvement in this project.
