"""
CLI Resume Chat Eval Runner.
Loads data.json + test_cases.json, runs all tests through matcher.py, prints report.

Usage: python resume/eval/run_eval.py
"""

import json
import os
import sys
from datetime import date

# Force UTF-8 output on Windows
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Add eval dir to path so matcher imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from matcher import find_answer

# --- Color helpers ---
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BOLD = "\033[1m"
RESET = "\033[0m"

def green(s): return f"{GREEN}{s}{RESET}"
def red(s): return f"{RED}{s}{RESET}"
def bold(s): return f"{BOLD}{s}{RESET}"

# --- Load data ---
EVAL_DIR = os.path.dirname(os.path.abspath(__file__))
RESUME_DIR = os.path.dirname(EVAL_DIR)

with open(os.path.join(RESUME_DIR, "data.json"), "r", encoding="utf-8") as f:
  resume_data = json.load(f)

with open(os.path.join(EVAL_DIR, "test_cases.json"), "r", encoding="utf-8") as f:
  test_cases = json.load(f)

# --- Run tests ---
results = {}
failures = []
total_pass = 0
total_tests = 0

categories = ["exact_match", "section", "keyword", "no_match", "regression"]

for category in categories:
  cases = test_cases.get(category, [])
  cat_pass = 0
  cat_total = len(cases)

  for tc in cases:
    total_tests += 1
    query = tc["query"]
    expected_layer = tc["expected_layer"]
    content_contains = tc.get("content_contains")

    actual_layer, actual_content = find_answer(query, resume_data)

    # Check layer match
    layer_ok = actual_layer == expected_layer

    # Check content match (only if expected_layer is not None)
    content_ok = True
    if expected_layer is not None and content_contains:
      content_ok = (
        actual_content is not None
        and content_contains.lower() in actual_content.lower()
      )

    passed = layer_ok and content_ok

    if passed:
      cat_pass += 1
      total_pass += 1
    else:
      failures.append({
        "id": tc["id"],
        "category": category,
        "query": query,
        "expected_layer": expected_layer,
        "actual_layer": actual_layer,
        "content_contains": content_contains,
        "actual_content_preview": (actual_content or "")[:120],
        "note": tc.get("note", ""),
      })

  results[category] = {"passed": cat_pass, "total": cat_total}

# --- Print report ---
today = date.today().isoformat()

print(f"\n{bold('=== CLI Resume Chat Eval ===')}")
print(f"Date: {today}\n")
print(f"Overall: {bold(f'{total_pass}/{total_tests}')} passed ({100*total_pass/max(total_tests,1):.1f}%)\n")

for cat in categories:
  r = results[cat]
  label = f"{cat}:"
  count = f"{r['passed']}/{r['total']}"
  mark = green("\u2713") if r["passed"] == r["total"] else red(f"  ({r['total'] - r['passed']} failed)")
  print(f"  {label:<16} {count}  {mark}")

if failures:
  print(f"\n{bold(red('FAILURES:'))}")
  for f in failures:
    print(f"  {red('\u2717')} [{f['id']}] \"{f['query']}\"")
    print(f"    Expected: {f['expected_layer']} | Actual: {f['actual_layer']}")
    if f["actual_content_preview"]:
      print(f"    Content: {f['actual_content_preview']}...")
    if f["note"]:
      print(f"    Note: {f['note']}")
else:
  print(f"\n{green('All tests passed!')}")

# --- Save JSON results ---
results_dir = os.path.join(EVAL_DIR, "results")
os.makedirs(results_dir, exist_ok=True)
results_file = os.path.join(results_dir, f"{today}.json")

output = {
  "date": today,
  "total_pass": total_pass,
  "total_tests": total_tests,
  "categories": results,
  "failures": failures,
}

with open(results_file, "w", encoding="utf-8") as f:
  json.dump(output, f, indent=2)

print(f"\nDone. Results saved to resume/eval/results/{today}.json\n")
