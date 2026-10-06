#!/usr/bin/env python3
"""
Agent 2 — consistency check between the demo's rule data and the published NSW page.

Usage:
  python3 tests/check_criteria.py <demo.html> <snapshot.json> [--previous <older_snapshot.json>]

<snapshot.json> is a dated record of the NSW page in tests/fetched/. Two shapes are accepted.

Schema 2 (written by tests/fetch_nsw.py, and by hand for 2026-10-06):
  {
    "schema": 2,
    "url": "...", "fetched_on": "YYYY-MM-DD",
    "source_method": "how the text was obtained",
    "raw_sha256": "<hash of the raw HTML, or null if the raw page was not available>",
    "current_as_at": "10 September 2026",
    "headings": ["...", ...],
    "emergency": {"intro": "...", "items": [{"text": "...", "children": ["...", ...]}, ...], "note": "..."},
    "required": [{"text": "...", "children": ["...", ...]}, ...],
    "if_available": ["...", ...],
    "triage": [{"category": "Category 1", "timeframe": "...", "criteria": "..."}, ...]
  }

Schema 1 (the 2026-09-24 file): flat lists of strings for required / if_available / triage.
Sub-item structure is not recorded in schema 1, so it cannot be checked against it.

What is compared — literally, character for character:
  - REQUIRED and IF_AVAILABLE: wording, order, duplicates and (schema 2) which items are sub-items.
  - The three triage lines on screen 4 ("Category — timeframe — criteria").
  - The "current as at" date: every place the demo, README.md and NOTICE write "as at <date>"
    must equal the date on the NSW page, and it must appear in the demo file at least three
    times (two on screen, one in the code comment). A date written some other way is not seen.
  - Notes that NSW attaches to an item (for example a "Note: refer to ..." line under it) are
    listed; the demo does not reproduce them and must say so.
  - With --previous: the NSW page's headings, Emergency section, other text in the watched
    sections and item notes, snapshot against snapshot.
    The demo does not reproduce these, so a change is reported for the author's review.

A difference in case, spacing, dash type or a trailing full stop is reported as CHARACTER-LEVEL
and counts as a difference. Nothing is normalised away.

Limit: this script reads the text written in the page's source. It does not run the page, so it
would not see text altered by script after loading. tests/test_demo.js covers that: it compares
what the page actually displays with the newest snapshot.

Exit code 0 = consistent, 1 = differences found, 2 = could not run.
"""
import difflib
import html as htmlmod
import json
import os
import re
import sys

DATE_RE = r'(\d{1,2} [A-Z][a-z]+ \d{4})'


def loose(s):
    """Used only to recognise that two differing strings are 'the same item, typed differently'."""
    s = s.replace('’', "'").replace('–', '-').replace('—', '-').replace(' ', ' ')
    return re.sub(r'\s+', ' ', s).strip().lower().rstrip('.')


def fail(msg):
    print('COULD NOT RUN: ' + msg)
    sys.exit(2)


def js_unescape(s):
    return re.sub(r'\\(.)', r'\1', s)


def extract_array(src, name):
    """Return [(text, is_sub), ...] from `const NAME = [ {...}, ... ];` in the demo's script."""
    m = re.search(r'const\s+' + name + r'\s*=\s*\[(.*?)\];', src, re.S)
    if not m:
        fail(f'could not find the {name} array in the demo')
    items = []
    for obj in re.findall(r'\{(.*?)\}', m.group(1), re.S):
        t = re.search(r"text\s*:\s*'((?:[^'\\]|\\.)*)'", obj)
        if not t:
            fail(f'an entry in {name} has no text')
        items.append((htmlmod.unescape(js_unescape(t.group(1))), bool(re.search(r'sub\s*:\s*true', obj))))
    if not items:
        fail(f'{name} is empty in the demo')
    return items


def snapshot_list(entries, schema):
    """Flatten a snapshot list to [(text, is_sub_or_None), ...]. None = structure not recorded (schema 1)."""
    out = []
    for e in entries:
        if isinstance(e, str):
            out.append((e, False if schema >= 2 else None))
        else:
            out.append((e['text'], False))
            out.extend((c, True) for c in e.get('children', []))
    return out


def item_notes(page):
    """Notes NSW attaches to list items (text after a line break inside the item)."""
    out = []
    for key in ('required', 'if_available'):
        for e in page.get(key, []):
            if isinstance(e, dict) and e.get('note'):
                out.append(f"{key}: {e['text']} -> {e['note']}")
    return out


NOTES_DISCLOSURE = 'Notes that NSW attaches to individual items are not reproduced'


def check_notes(demo, page, out):
    notes = item_notes(page)
    if not notes:
        return False
    out.append('\n== NOTES ATTACHED TO ITEMS ON THE NSW PAGE (the demo does not reproduce these) ==')
    out.extend('  ' + n for n in notes)
    if NOTES_DISCLOSURE in demo:
        out.append('  the demo states that such notes are not reproduced: yes')
        return False
    out.append(f'  the demo does not state this. Expected the sentence: "{NOTES_DISCLOSURE}"')
    return True


def snapshot_triage(entries):
    out = []
    for e in entries:
        out.append(e if isinstance(e, str) else f"{e['category']} — {e['timeframe']} — {e['criteria']}")
    return out


def compare(label, demo, page, out):
    """demo and page are [(text, sub)] lists. Returns True if anything differs."""
    d_txt = [t for t, _ in demo]
    p_txt = [t for t, _ in page]
    diff = False
    out.append(f'\n== {label} ==  demo: {len(d_txt)}  page: {len(p_txt)}')

    for name, lst in (('demo', d_txt), ('page', p_txt)):
        dups = sorted({x for x in lst if lst.count(x) > 1})
        for x in dups:
            out.append(f'  DUPLICATE in {name}: {x}')
            diff = True

    identical = [x for x in d_txt if x in p_txt]
    only_demo = [x for x in d_txt if x not in p_txt]
    only_page = [x for x in p_txt if x not in d_txt]
    out.append(f'  identical, character for character: {len(identical)}')

    # same item, typed differently (case, spacing, dash type, trailing full stop)
    for od in list(only_demo):
        match = next((pg for pg in only_page if loose(pg) == loose(od)), None)
        if match is not None:
            out.append(f'  CHARACTER-LEVEL DIFFERENCE\n    demo: {od!r}\n    page: {match!r}')
            only_demo.remove(od); only_page.remove(match); diff = True
    # reworded
    for od in list(only_demo):
        best = difflib.get_close_matches(loose(od), [loose(x) for x in only_page], n=1, cutoff=0.6)
        if best:
            match = next(x for x in only_page if loose(x) == best[0])
            out.append(f'  REWORDED\n    demo: {od}\n    page: {match}')
            only_demo.remove(od); only_page.remove(match); diff = True
    for x in only_page:
        out.append(f'  MISSING FROM DEMO (on page): {x}'); diff = True
    for x in only_demo:
        out.append(f'  NOT ON PAGE (in demo):       {x}'); diff = True

    # order, among the items both sides have
    d_common = [x for x in d_txt if x in p_txt]
    p_common = [x for x in p_txt if x in d_txt]
    if d_common != p_common:
        out.append('  ORDER DIFFERS between demo and page'); diff = True

    # sub-item structure
    p_sub = dict((t, s) for t, s in page)
    if any(s is None for s in p_sub.values()):
        out.append('  note: this snapshot does not record sub-item structure (schema 1); structure not checked')
    else:
        for t, s in demo:
            if t in p_sub and p_sub[t] != s:
                out.append(f'  STRUCTURE DIFFERS: "{t}" is {"a sub-item" if p_sub[t] else "a top-level item"} on the page, '
                           f'{"a sub-item" if s else "a top-level item"} in the demo')
                diff = True
    return diff


def check_dates(demo_path, demo_src, page_date, out):
    diff = False
    page_date = re.sub(r'^[A-Za-z]+day,?\s+', '', (page_date or '').strip())  # drop a leading weekday
    out.append(f'\n== DATE ==  NSW page shows: {page_date or "NOT RECORDED"}')
    if not re.fullmatch(DATE_RE, page_date or ''):
        out.append('  the snapshot has no usable "current as at" date'); return True
    root = os.path.dirname(os.path.abspath(demo_path))
    files = [(os.path.basename(demo_path), demo_src, 3)]
    for name in ('README.md', 'NOTICE'):
        p = os.path.join(root, name)
        if os.path.exists(p):
            files.append((name, open(p, encoding='utf8').read(), 1))
        else:
            out.append(f'  note: {name} not found beside the demo; not checked')
    for name, src, minimum in files:
        found = re.findall(r'as at:?(?:\s|&nbsp;|\u00a0)+(?:[A-Za-z]+day,?\s+)?' + DATE_RE, src, re.I)
        wrong = [d for d in found if d != page_date]
        out.append(f'  {name}: {len(found)} occurrence(s)' + (f' — DIFFERENT: {sorted(set(wrong))}' if wrong else ''))
        if wrong:
            diff = True
        if len(found) < minimum:
            out.append(f'  {name}: expected the date at least {minimum} time(s), found {len(found)}')
            diff = True
    if diff:
        out.append('  If NSW has changed its date, re-check every item and update each place the date appears.')
    return diff


def flat_emergency(e):
    if not e:
        return None
    lines = ['intro: ' + e.get('intro', '')]
    for it in e.get('items', []):
        lines.append('- ' + it['text'])
        lines.extend('  * ' + c for c in it.get('children', []))
    lines.append('note: ' + e.get('note', ''))
    return lines


def compare_previous(page, prev, out):
    diff = False
    out.append(f"\n== NSW PAGE vs PREVIOUS SNAPSHOT ({prev.get('fetched_on', '?')}) — sections the demo does not reproduce ==")
    def extra(s):
        e = s.get('extra_text')
        return None if e is None else [f'{k}: {t}' for k in sorted(e) for t in e[k]] + item_notes(s)
    for key, label, getter in (('headings', 'HEADINGS', lambda s: s.get('headings')),
                               ('emergency', 'EMERGENCY SECTION', lambda s: flat_emergency(s.get('emergency'))),
                               ('extra_text', 'OTHER TEXT IN THE WATCHED SECTIONS, AND NOTES ATTACHED TO ITEMS', extra)):
        now, before = getter(page), getter(prev)
        if now is None:
            out.append(f'  {label}: not recorded in the current snapshot — NOT CHECKED')
            diff = diff or key != 'extra_text'; continue
        if before is None:
            out.append(f'  {label}: not recorded in the previous snapshot; this snapshot becomes the baseline'); continue
        if now == before:
            out.append(f'  {label}: unchanged'); continue
        diff = True
        out.append(f'  {label}: CHANGED — review; the author decides what, if anything, the demo should do')
        for line in difflib.unified_diff(before, now, 'previous', 'current', lineterm='', n=0):
            if not line.startswith(('---', '+++', '@@')):
                out.append('    ' + line)
    return diff


def main():
    args = sys.argv[1:]
    prev_path = None
    if '--previous' in args:
        i = args.index('--previous')
        if i + 1 >= len(args):
            print(__doc__); sys.exit(2)
        prev_path = args[i + 1]
        del args[i:i + 2]
    if len(args) != 2:
        print(__doc__); sys.exit(2)
    try:
        demo = open(args[0], encoding='utf8').read()
        page = json.load(open(args[1], encoding='utf8'))
        prev = json.load(open(prev_path, encoding='utf8')) if prev_path else None
    except (OSError, ValueError) as e:
        fail(str(e))

    out = [f"Criteria consistency check — demo: {args[0]} — NSW snapshot dated {page.get('fetched_on', '?')}",
           f"Source: {page.get('url', '?')}",
           f"How the snapshot was obtained: {page.get('source_method', 'not recorded (schema 1)')}"]
    for key in ('required', 'if_available', 'triage'):
        if not page.get(key):
            fail(f'the snapshot has no "{key}" list')

    schema = int(page.get('schema', 1))
    diff = False
    diff |= compare('REQUIRED', extract_array(demo, 'REQUIRED'), snapshot_list(page['required'], schema), out)
    diff |= compare('IF AVAILABLE', extract_array(demo, 'IF_AVAILABLE'), snapshot_list(page['if_available'], schema), out)
    demo_triage = [htmlmod.unescape(t) for t in
                   re.findall(r'<div class="requirement-item"[^>]*>\s*(Category\b.*?)\s*</div>', demo, re.S)]
    if not demo_triage:
        out.append('\n== TRIAGE CATEGORIES ==\n  no triage lines found in the demo'); diff = True
    else:
        diff |= compare('TRIAGE CATEGORIES', [(t, False) for t in demo_triage],
                        [(t, False) for t in snapshot_triage(page['triage'])], out)
    diff |= check_notes(demo, page, out)
    diff |= check_dates(args[0], demo, page.get('current_as_at'), out)
    if prev is not None:
        diff |= compare_previous(page, prev, out)

    out.append('\nRESULT: ' + ('DIFFERENCES FOUND — review and correct' if diff else 'CONSISTENT with the snapshot'))
    print('\n'.join(out))
    sys.exit(1 if diff else 0)


if __name__ == '__main__':
    main()
