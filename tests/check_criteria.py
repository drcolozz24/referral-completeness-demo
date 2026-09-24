#!/usr/bin/env python3
"""
Agent 2 — consistency check between the demo's rule data and the published NSW page.

Usage:
  python3 tests/check_criteria.py <demo.html> <fetched_nsw_page.json>

<fetched_nsw_page.json> is produced by whoever fetched the live NSW page and must have the shape:
  {
    "url": "...",
    "fetched_on": "YYYY-MM-DD",
    "current_as_at": "10 September 2026",          # the date NSW prints on the page
    "required": ["Reason for referral", ...],       # verbatim bullets, in page order
    "if_available": ["Cardiovascular disease risk assessment", ...],
    "triage": ["Category 1 — Recommended to be seen within 30 calendar days — <text>", ...]   # optional
  }

The script extracts the REQUIRED / IF_AVAILABLE arrays from the demo's <script>, normalises
whitespace/case/punctuation lightly, and reports:
  - items on the NSW page that the demo lacks
  - items in the demo that are not on the NSW page
  - items whose wording differs (fuzzy match) — shown side by side
  - whether the 'current as at' date on the page differs from the one the demo displays
Exit code 0 = consistent, 1 = differences found, 2 = could not run.
"""
import json, re, sys, difflib, html as htmlmod

def norm(s):
    s = htmlmod.unescape(s)
    s = s.replace('’', "'").replace('–', '-').replace('—', '-')
    s = re.sub(r'\s+', ' ', s).strip().lower().rstrip('.')
    return s

def extract_array(src, name):
    m = re.search(r'const\s+' + name + r'\s*=\s*\[(.*?)\];', src, re.S)
    if not m:
        raise SystemExit(f'could not find {name} in demo')
    return [htmlmod.unescape(t) for t in re.findall(r"text\s*:\s*'((?:[^'\\]|\\.)*)'", m.group(1))]

def compare(label, demo_items, page_items, out):
    d = {norm(x): x for x in demo_items}
    p = {norm(x): x for x in page_items}
    exact = set(d) & set(p)
    only_demo = [d[k] for k in d if k not in p]
    only_page = [p[k] for k in p if k not in d]
    # fuzzy pairing of leftovers
    reworded = []
    for od in list(only_demo):
        best = difflib.get_close_matches(norm(od), [norm(x) for x in only_page], n=1, cutoff=0.6)
        if best:
            match = next(x for x in only_page if norm(x) == best[0])
            reworded.append((od, match))
            only_demo.remove(od); only_page.remove(match)
    out.append(f'\n== {label} ==  demo: {len(demo_items)}  page: {len(page_items)}  identical: {len(exact)}')
    for od, pg in reworded:
        out.append(f'  REWORDED\n    demo: {od}\n    page: {pg}')
    for x in only_page:
        out.append(f'  MISSING FROM DEMO (on page): {x}')
    for x in only_demo:
        out.append(f'  NOT ON PAGE (in demo):       {x}')
    return bool(reworded or only_demo or only_page)

def main():
    if len(sys.argv) != 3:
        print(__doc__); sys.exit(2)
    demo = open(sys.argv[1], encoding='utf8').read()
    page = json.load(open(sys.argv[2], encoding='utf8'))
    out = [f"Criteria consistency check — demo: {sys.argv[1]} — NSW page fetched {page.get('fetched_on','?')}",
           f"Source: {page.get('url','?')}"]
    diff = False
    diff |= compare('REQUIRED', extract_array(demo, 'REQUIRED'), page['required'], out)
    diff |= compare('IF AVAILABLE', extract_array(demo, 'IF_AVAILABLE'), page['if_available'], out)
    if 'triage' in page:
        demo_triage = re.findall(r'<div class="requirement-item">(Category \d — .*?)</div>', demo)
        diff |= compare('TRIAGE CATEGORIES', demo_triage, page['triage'], out)
    m = re.search(r'current as at (\d{1,2} \w+ \d{4})', demo, re.I)
    demo_date = m.group(1) if m else None
    page_date = page.get('current_as_at')
    out.append(f"\n== DATE ==  demo displays: {demo_date}   page shows: {page_date}")
    if demo_date and page_date and norm(demo_date) != norm(page_date):
        out.append('  DATE CHANGED — NSW has updated the page since the demo was published. Re-check every item and update the displayed date.')
        diff = True
    if demo_date and demo.count(demo_date) < 3:
        out.append(f'  NOTE: the date appears only {demo.count(demo_date)} time(s) in the demo; it should be on the result screen, the list screen and in the code comment.')
    out.append('\nRESULT: ' + ('DIFFERENCES FOUND — review and correct' if diff else 'CONSISTENT with the fetched page'))
    print('\n'.join(out))
    sys.exit(1 if diff else 0)

if __name__ == '__main__':
    main()
