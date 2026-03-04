# CLI Resume — Lean PRD

**Date:** 2026-03-04
**Status:** Approved

---

## 1. Problem & Opportunity

Job seekers' resumes are static PDFs that can't provide rich context or a meaningful snapshot of previous experience. Recruiters spend ~7 seconds scanning each one, and the format leaves no room to express personality, creativity, or depth. CLI Resume solves this by turning the resume into a live, interactive experience that stands out and invites exploration. The timing is right — personal brand differentiation is increasingly important in competitive job markets.

**Initial user:** Job seekers who want to provide personality to their resume application and double as a portfolio piece.

---

## 2. Hypothesis

We believe that building an interactive terminal-styled resume for job seekers will increase recruiter engagement and callback rate. We'll know we're right when the interviewee's interview callback rate increases compared to the standard PDF resume.

---

## 3. Solution

CLI Resume is a single-page interactive website styled as a terminal interface, hosted on GitHub Pages. Visitors can type commands or click suggested chips to explore experience, skills, projects, and Q&A — like navigating a real terminal. It's powered by Gemini API for conversational Q&A responses.

---

## 4. Scope

**In:**
- Terminal-styled UI with command input and clickable chips
- Sections: experience, skills, projects, education, contact
- AI-powered Q&A via Gemini API
- Mobile-responsive layout
- GitHub Pages hosting (static, no backend)
- Resume draft generation with AI
- Multiple resume versions (tailored per role/company)
- Multiple color themes

**Out:**
- Analytics/tracking — not validated as needed yet, adds complexity to a static site
- PDF export or download — defeats the purpose of an interactive experience
- Infrastructure layer for non-technical users — adds cost/overhead and not validated with users
- CMS or admin panel — overkill for a solo project, data.json is simple enough to edit directly

---

## 5. User Flow

```
Visit URL → See terminal welcome screen → Type command or click chip → View section content (experience, skills, etc.) → Ask follow-up question via chat → Get AI-generated answer → Explore more sections or exit
```

---

## 6. Key Decisions

- **Gemini over OpenAI:** Chose Gemini API for Q&A because of free tier / lower cost.
- **Static GitHub Pages over hosted backend:** No server needed — API keys stored base64-encoded in data.json, all client-side.
- **Single HTML file over framework (React, etc.):** Simpler deployment, no build step, easier to maintain solo.
- **No infra/hosting layer:** Avoided building a hosted service for other users — adds cost/overhead and not validated with users.
- **10 question limit:** Caps Q&A to 10 questions per session to focus on the most important topics and manage API costs.

---

## 7. Success Metrics

| Metric | Target |
|--------|--------|
| Interview callback rate | Higher than PDF resume baseline |

*Note: No direct attribution is possible. The only signal is if a recruiter mentions the CLI resume during conversation, or if the interviewee explicitly asks. There is no automated way to measure this.*

---

## 8. Open Questions & Assumptions

**Open questions:**
- [ ] Should we add lightweight analytics (e.g., PostHog) to track session duration and engagement?
- [ ] How to A/B test callback rate — PDF vs CLI resume link in applications?
- [ ] Should multiple resume versions be separate deployments or switchable within one page?
- [ ] Should we explore a non-technical user use case (hosted service / templates for non-developers)?

**Assumptions (not yet validated):**
- [ ] Recruiters will click a non-PDF link in an application
- [ ] Terminal aesthetic appeals to non-technical hiring managers
- [ ] 10 questions is enough for a recruiter to get what they need
