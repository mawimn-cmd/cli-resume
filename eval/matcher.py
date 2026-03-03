"""
Python port of CLI Resume chat matching logic from index.html (lines 1330-1454).
Faithfully replicates: tokenMatchesKeyword, sectionFallback, findAnswer.

Keep in sync with index.html — any JS change must be mirrored here.
"""

import re

# --- Constants (exact copies from index.html lines 1333-1339) ---

SECTION_KEYWORDS = {
  "experience": ["experience", "work", "job", "role", "career", "company", "position", "worked"],
  "skills": ["skills", "tech", "stack", "know", "technologies", "proficient", "languages", "tools"],
  "education": ["education", "school", "degree", "study", "university", "college", "studied", "academic"],
  "projects": ["projects", "project", "built", "portfolio", "build", "made", "created", "side project"],
  "contact": ["contact", "email", "reach", "connect", "linkedin", "github", "hire", "touch"],
  "about": ["who are you", "yourself", "bio", "introduction", "background", "summary"],
}

STOP_WORDS = {
  "tell", "me", "about", "a", "an", "the", "is", "are", "was", "were",
  "be", "do", "does", "did", "have", "has", "had", "will", "would", "could", "should", "can",
  "may", "might", "to", "of", "in", "for", "on", "with", "at", "by", "from", "and", "or",
  "but", "not", "no", "so", "if", "what", "which", "how", "when", "where", "why",
  "i", "you", "your", "my", "we", "they", "he", "she", "it", "this", "that",
}


# --- Functions ---

def token_matches_keyword(token, keyword):
  """Port of tokenMatchesKeyword (line 1391)."""
  if token == keyword:
    return True
  shorter = token if len(token) <= len(keyword) else keyword
  longer = token if len(token) > len(keyword) else keyword
  if len(shorter) < 4:
    return False
  if len(shorter) / len(longer) < 0.7:
    return False
  return shorter in longer


def section_fallback(query, resume_data):
  """Port of sectionFallback (line 1342). Returns (layer, content) or None."""
  lower = query.lower()
  d = resume_data

  for section, keywords in SECTION_KEYWORDS.items():
    matched = any(kw in lower for kw in keywords)
    if not matched:
      continue

    if section == "experience":
      parts = []
      for exp in d.get("experience", []):
        header = f"{exp['role']} at {exp['company']} ({exp['period']})"
        bullets = exp.get("bullets") or []
        bullet_lines = "\n".join(f"  \u2022 {b}" for b in bullets)
        parts.append(f"{header}\n{bullet_lines}" if bullet_lines else header)
      content = "\n\n".join(parts)
      return ("section", content)

    elif section == "skills":
      skill_lines = []
      for cat, items in d.get("skills", {}).items():
        skill_lines.append(f"{cat}: {', '.join(items)}")
      content = "Here are my skills:\n\n" + "\n".join(skill_lines)
      return ("section", content)

    elif section == "education":
      parts = []
      for edu in d.get("education", []):
        line = f"{edu['degree']} \u2014 {edu['school']} ({edu['period']})"
        if edu.get("details"):
          line += f"\n  {edu['details']}"
        parts.append(line)
      content = "\n\n".join(parts)
      return ("section", content)

    elif section == "projects":
      parts = []
      for proj in d.get("projects", []):
        line = f"{proj['name']}: {proj['description']}"
        if proj.get("tech"):
          line += f"\n  Tech: {proj['tech']}"
        if proj.get("url"):
          line += f"\n  {proj['url']}"
        parts.append(line)
      content = "\n\n".join(parts)
      return ("section", content)

    elif section == "contact":
      lines = []
      contact = d.get("contact", {})
      if contact.get("email"):
        lines.append(f"Email: {contact['email']}")
      if contact.get("linkedin"):
        lines.append(f"LinkedIn: {contact['linkedin']}")
      if contact.get("github"):
        lines.append(f"GitHub: {contact['github']}")
      if contact.get("website"):
        lines.append(f"Website: {contact['website']}")
      content = "Here's how to reach me:\n\n" + "\n".join(lines)
      return ("section", content)

    elif section == "about":
      bio = d.get("bio", [])
      content = "\n".join(bio)
      return ("section", content)

  return None


def find_answer(query, resume_data):
  """
  Port of findAnswer (line 1402).
  Returns (layer, content) where layer is "exact", "section", "keyword", or None.
  """
  clean_query = re.sub(r"[?!.,;:'\"]+", "", query.lower()).strip()
  tokens = [t for t in clean_query.split() if t]

  # 1. Exact question match
  qa_pairs = resume_data.get("qaPairs", [])
  for pair in qa_pairs:
    pair_q = re.sub(r"[?!.,;:'\"]+", "", pair["question"].lower()).strip()
    if pair_q == clean_query:
      return ("exact", pair["answer"])

  # 2. Section-aware fallback
  # JS returns content string directly; empty string is falsy and falls through.
  # Our port returns a tuple, so check content is non-empty to match JS behavior.
  section_result = section_fallback(query, resume_data)
  if section_result and section_result[1]:
    return section_result

  # 3. Q&A keyword scoring
  content_tokens = [t for t in tokens if t not in STOP_WORDS and len(t) > 2]

  best_match = None
  best_score = 0
  if qa_pairs and content_tokens:
    for pair in qa_pairs:
      score = 0
      for token in content_tokens:
        for keyword in pair.get("keywords", []):
          if token_matches_keyword(token, keyword):
            score += 1
      normalized = score / max(len(content_tokens), 1)
      if normalized > best_score:
        best_score = normalized
        best_match = pair
    if best_match and best_score >= 0.3:
      return ("keyword", best_match["answer"])

  # 4. No match
  return (None, None)
