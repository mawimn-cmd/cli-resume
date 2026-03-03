# CLI Resume — Project Overview

## Level 1: What It Is

CLI Resume is a **zero-dependency, static resume website** that looks like a terminal. Two files do all the work:

- **`index.html`** (54 KB) — The resume itself. Left panel shows your resume, right panel is an AI chat where recruiters can ask questions about you.
- **`setup.html`** (48 KB) — A wizard that parses your resume (via Gemini), lets you answer 20 recruiter questions, and deploys to GitHub Pages.
- **`data.json`** — The only thing that changes per user. Contains all resume data, Q&A pairs, and an optional Gemini API key.

The key insight: **the chat is the product differentiator**. Lots of resume sites exist. This one lets a recruiter have a conversation with your resume. The 4-layer matching system (`exact → section → keyword → Gemini`) tries to answer locally first, only calling Gemini as a last resort — so it's fast for common questions and intelligent for unusual ones.

The eval harness (`resume/eval/`) protects that matching logic from regressions.

### File Structure

```
resume/
├── index.html              ← main resume app (terminal UI + chat)
├── setup.html              ← wizard for resume parsing & Q&A input
├── data.json               ← current resume data (per user)
├── data.example.json       ← schema reference
└── eval/
    ├── matcher.py          ← Python port of chat matching logic
    ├── test_cases.json     ← 30 test cases (5 categories)
    ├── run_eval.py         ← test runner with color-coded report
    └── results/            ← JSON history from eval runs
```

### Deployment

- **Repo:** https://github.com/mawimn-cmd/cli-resume
- **Live:** https://mawimn-cmd.github.io/cli-resume/
- **Runtime:** Zero build tools. No backend. No dependencies. Pure HTML/CSS/JS.

---

## Level 2: How the Systems Connect

### Chat Matching Flow

```
Recruiter types "What are your skills?"
        │
        ▼
   ┌─ Layer 1: Exact Match ──── "What are your skills?" ≠ any qaPairs question
   │                             (no exact match after punctuation strip)
   │
   ├─ Layer 2: Section ──────── "skills" found in SECTION_KEYWORDS.skills
   │                             → returns formatted skills block ✓ DONE
   │
   ├─ Layer 3: Keyword ──────── (never reached)
   │
   └─ Layer 4: Gemini API ───── (never reached)
```

**Why this ordering matters:** Section fallback (layer 2) runs before keyword scoring (layer 3). This was a bug we fixed — "what are your skills" used to match the "Tell me about yourself" Q&A pair via substring ("yourself" contains "your"). By checking section keywords first, "skills" routes correctly.

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    index.html (54 KB)                       │
│  ┌──────────────────────┬──────────────────────────────────┐│
│  │   Left Panel (60%)   │    Right Panel (40%)             ││
│  │  Resume Renderer     │    Chat Engine (4-layer)         ││
│  │  ├─ Photo circle     │    ├─ Boot sequence animation    ││
│  │  ├─ Header           │    ├─ Welcome + suggested chips  ││
│  │  ├─ About            │    ├─ Message history            ││
│  │  ├─ Experience       │    ├─ Input field                ││
│  │  ├─ Projects         │    └─ Follow-up suggestions      ││
│  │  ├─ Skills           │                                  ││
│  │  ├─ Education        │    Matching Logic:               ││
│  │  └─ Contact          │    1. Exact Q&A match            ││
│  │                      │    2. Section keywords           ││
│  │  Mobile: stacked     │    3. Q&A keyword scoring        ││
│  │  + floating FAB      │    4. Gemini API call            ││
│  │                      │    5. Fallback chips             ││
│  └──────────────────────┴──────────────────────────────────┘│
│  Theme System (5 themes, localStorage)                      │
│  Data Source: data.json (loaded via fetch)                  │
└─────────────────────────────────────────────────────────────┘
```

### Eval System

- `matcher.py` is a line-by-line Python port of the JS matching functions
- `test_cases.json` has tests for each layer + the specific bugs we've fixed
- `run_eval.py` checks both the layer that fired AND the content returned

**The sync gap:** The eval tests the Python port, not the JS directly. If you change `index.html` and forget to update `matcher.py`, evals pass but prod breaks. Treat them as a pair — see Sync Protocol below.

---

## Level 3: The Engineering Decisions

### Why 4 layers instead of just Gemini?

- **Latency.** Layers 1-3 are instant (string matching). Gemini adds 1-2 seconds.
- **Cost.** Every Gemini call uses API credits. Most recruiter questions are predictable.
- **Reliability.** If the API key expires or Gemini is down, layers 1-3 still work.
- **Control.** Q&A pairs give exact control over answers. Gemini might rephrase or hallucinate.

### Why `tokenMatchesKeyword` has a 70% length ratio check

```
"your" (4 chars) vs "yourself" (8 chars) → 4/8 = 0.5 < 0.7 → NO match
"ambition" (8) vs "ambitions" (9) → 8/9 = 0.89 → YES match
```

Without this, short common words like "your", "me", "work" would match longer keywords via substring, causing false positives everywhere. The 0.7 threshold catches plurals and verb forms while blocking unrelated short words.

### Why the eval is a Python port (not browser-based JS tests)

- Python runs anywhere with no browser/Node setup
- JSON test cases are easy to read and extend
- The matching logic is pure functions (no DOM, no network) — perfect for porting
- Trade-off: sync risk for simplicity. A more robust approach would extract matching logic into a separate `.js` module and test with Node — but that restructures the single-file architecture.

### The `data.json` API key encoding

GitHub scans pushes for API keys and blocks them. Base64 encoding (`btoa(key)` → stored → `atob(key)` at runtime) bypasses the scanner. It's not encryption — anyone reading `data.json` can decode it. But it solves GitHub rejecting your push. The real security boundary is that this is a client-side app — the key is visible in the browser anyway.

---

## Sync Protocol

When matching logic in `index.html` changes:

1. Update `matcher.py` to match
2. Add a regression test case for the bug that prompted the change
3. Run evals before pushing: `python resume/eval/run_eval.py`
