#!/usr/bin/env python3
"""
Fetch the live NSW Health page and write a dated snapshot (schema 2) into tests/fetched/.

Usage:
  python3 tests/fetch_nsw.py [--out-dir tests/fetched] [--from-file saved_page.html] [--date YYYY-MM-DD]

An existing snapshot for the same date is never overwritten (exit 2).

The raw HTML is hashed (SHA-256) and the hash is stored in the snapshot; the raw page itself is
not committed. The snapshot holds only the text the demonstration relies on or watches: the
"current as at" date, the headings, the Emergency section, the Required and If-available lists
and the three triage categories.

Exit code 0 = snapshot written (its path is printed on the last line), 2 = could not fetch or
could not find every section. A parse failure is itself information: it usually means NSW has
restructured the page, and a person should look.

No third-party packages are needed.
"""
import datetime
import hashlib
import json
import os
import re
import sys
import urllib.request
from html.parser import HTMLParser

URL = 'https://www.health.nsw.gov.au/outpatients/referrals/Pages/chest-pain-tightness-adult.aspx'
UA = 'referral-completeness-demo monthly consistency check (+https://github.com/drcolozz24/referral-completeness-demo)'
BLOCK = {'p', 'div', 'section', 'article', 'td', 'th', 'tr', 'table', 'ul', 'ol', 'li',
         'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'br', 'button', 'summary', 'details', 'caption'}
SKIP = {'script', 'style', 'noscript', 'template', 'svg', 'nav', 'footer'}
KNOWN_HEADINGS = ['Emergency', 'Criteria to access public outpatient services',
                  'Information to include within a referral', 'Required', 'If available',
                  'Important information for referring health professionals',
                  'Additional cardiology adult conditions']


BR = chr(0)   # marks a line break inside a list item

ZERO_WIDTH = {0x200b: None, 0x200c: None, 0x200d: None, 0x2060: None, 0xfeff: None}


def clean(s):
    """Collapse whitespace. Non-breaking spaces become spaces; zero-width characters (which the
    NSW page scatters through headings and table cells) are removed."""
    return re.sub(r'\s+', ' ', s.translate(ZERO_WIDTH).replace(chr(0xa0), ' ')).strip()


class Blocks(HTMLParser):
    """Turn the page into an ordered list of blocks:
       ('h', text) heading, ('li', depth, text, note) list item, ('row', [cells]) table row,
       ('p', text). depth is how many lists the item sits inside: NSW nests a <ul> directly
       inside a <ul>, not inside the <li>, so depth comes from the lists, not the items.
       note is any text after a line break within an item (NSW attaches "Note: ..." to an
       item that way), or ''."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.blocks = []
        self.buf = []
        self.skip = 0
        self.list_depth = 0
        self.li_stack = []      # one text buffer per open <li>
        self.heading = None
        self.row = None
        self.cell = None

    def flush_p(self):
        t = clean(''.join(self.buf)); self.buf = []
        if t:
            self.blocks.append(('h', t) if t in KNOWN_HEADINGS else ('p', t))

    def flush_li(self):
        """Emit the text gathered so far for the innermost open <li> (its own text, not its children's)."""
        if self.li_stack:
            raw = ''.join(self.li_stack[-1]); self.li_stack[-1] = []
            head, _, tail = raw.partition(BR)
            t, note = clean(head), clean(tail.replace(BR, ' '))
            if not t:
                t, note = note, ''
            if t:
                self.blocks.append(('li', max(1, self.list_depth), t, note))

    def handle_starttag(self, tag, attrs):
        if tag in SKIP:
            self.skip += 1; return
        if self.skip:
            return
        if tag == 'br':
            if self.heading is not None:
                self.heading.append(' ')
            elif self.cell is not None:
                self.cell.append(' ')
            elif self.li_stack:
                self.li_stack[-1].append(BR)
            else:
                self.buf.append(' ')
            return
        if tag in ('ul', 'ol'):
            self.flush_li() if self.li_stack else self.flush_p()
            self.list_depth += 1
        elif tag == 'li':
            self.flush_li() if self.li_stack else self.flush_p()
            self.li_stack.append([])
        elif re.fullmatch(r'h[1-6]', tag):
            self.flush_p(); self.heading = []
        elif tag == 'tr':
            self.flush_p(); self.row = []
        elif tag in ('td', 'th'):
            self.cell = []
        elif tag in BLOCK and not self.li_stack and self.cell is None and self.heading is None:
            self.flush_p()

    def handle_endtag(self, tag):
        if tag in SKIP:
            self.skip = max(0, self.skip - 1); return
        if self.skip:
            return
        if tag == 'li' and self.li_stack:
            self.flush_li(); self.li_stack.pop()
        elif tag in ('ul', 'ol'):
            self.list_depth = max(0, self.list_depth - 1)
        elif re.fullmatch(r'h[1-6]', tag) and self.heading is not None:
            t = clean(''.join(self.heading)); self.heading = None
            if t:
                self.blocks.append(('h', t))
        elif tag in ('td', 'th') and self.cell is not None and self.row is not None:
            self.row.append(clean(''.join(self.cell))); self.cell = None
        elif tag == 'tr' and self.row is not None:
            if any(self.row):
                self.blocks.append(('row', self.row))
            self.row = None
        elif tag in BLOCK and not self.li_stack and self.cell is None and self.heading is None:
            self.flush_p()

    def handle_data(self, data):
        if self.skip:
            return
        if self.heading is not None:
            self.heading.append(data)
        elif self.cell is not None:
            self.cell.append(data)
        elif self.li_stack:
            self.li_stack[-1].append(data)
        else:
            self.buf.append(data)


def section(blocks, heading, stop_at):
    """Blocks after the heading `heading`, up to the next heading named in stop_at (or any heading if None)."""
    out, on = [], False
    for b in blocks:
        if b[0] == 'h':
            if on and (stop_at is None or b[1] in stop_at):
                break
            if b[1] == heading:
                on = True
                continue
        if on:
            out.append(b)
    return out


def nested(items):
    """[('li', depth, text, note), ...] -> [{'text':..., 'note':..., 'children':[...]}, ...] relative to the shallowest depth."""
    lis = [b for b in items if b[0] == 'li']
    if not lis:
        return []
    top = min(b[1] for b in lis)
    out = []
    for _, depth, text, note in lis:
        if depth == top or not out:
            out.append({'text': text})
            if note:
                out[-1]['note'] = note
        else:
            out[-1].setdefault('children', []).append(text if not note else f'{text} [{note}]')
    return out


def parse(html):
    p = Blocks(); p.feed(html); p.close(); p.flush_p()
    blocks = p.blocks
    problems = []
    text_all = ' '.join(b[1] if b[0] in ('h', 'p') else (b[2] if b[0] == 'li' else ' '.join(b[1])) for b in blocks)

    m = re.search(r'Current as at:?\s*(?:[A-Za-z]+day,?\s+)?(\d{1,2} [A-Z][a-z]+ \d{4})', text_all)
    current_as_at = m.group(1) if m else None
    if not current_as_at:
        problems.append('"Current as at" date not found')

    # Headings of the criteria content only: from the page title (first heading) to the last
    # heading this script knows. Site furniture and "related" headings after that are left out.
    headings = [b[1] for b in blocks if b[0] == 'h']
    last_known = max((i for i, h in enumerate(headings) if h in KNOWN_HEADINGS), default=-1)
    headings = headings[:last_known + 1]

    emer = section(blocks, 'Emergency', KNOWN_HEADINGS)
    paras = [b[1] for b in emer if b[0] == 'p']
    emergency = {
        'intro': next((t for t in paras if not t.lower().startswith('note')), ''),
        'items': nested(emer),
        'note': re.sub(r'^note:?\s*', '', next((t for t in paras if t.lower().startswith('note')), ''), flags=re.I),
    }
    if not emergency['items']:
        problems.append('Emergency section not found')

    req_blocks = section(blocks, 'Required', KNOWN_HEADINGS)
    opt_blocks = section(blocks, 'If available', None)
    required = nested(req_blocks)
    if_available = [i if 'note' in i else i['text'] for i in nested(opt_blocks)]
    # Any other paragraph text inside the watched sections, so that an added sentence
    # (a second note, a new instruction) is not silently dropped.
    note_para = next((t for t in paras if t.lower().startswith('note')), None)
    emer_extra, seen = [], set()
    for t in paras:
        if t in (emergency['intro'], note_para) and t not in seen:
            seen.add(t); continue
        emer_extra.append(t)
    extra_text = {
        'emergency': emer_extra,
        'required': [b[1] for b in req_blocks if b[0] == 'p'],
        'if_available': [b[1] for b in opt_blocks if b[0] == 'p'],
        'important_information': [b[1] if b[0] == 'p' else b[2] for b in
                                  section(blocks, 'Important information for referring health professionals', None)
                                  if b[0] in ('p', 'li')],
    }
    if not required:
        problems.append('Required list not found')
    if not if_available:
        problems.append('If-available list not found')

    triage = []
    for b in blocks:
        if b[0] != 'row':
            continue
        joined = ' | '.join(b[1])
        m = re.match(r'(Category \d+)\s*(?:\|\s*)?(Recommended to be seen within[^|]*?)\s*\|\s*(.+)$', joined)
        if m:
            triage.append({'category': m.group(1), 'timeframe': clean(m.group(2)),
                           'criteria': clean(m.group(3).replace(' | ', ' '))})
    if len(triage) != 3:
        problems.append(f'expected 3 triage categories in a table, found {len(triage)}')

    return {'current_as_at': current_as_at, 'headings': headings, 'emergency': emergency,
            'required': required, 'if_available': if_available, 'triage': triage,
            'extra_text': extra_text}, problems


def main():
    args = sys.argv[1:]

    def opt(name, default=None):
        if name in args:
            i = args.index(name); v = args[i + 1]; del args[i:i + 2]; return v
        return default

    out_dir = opt('--out-dir', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fetched'))
    from_file = opt('--from-file')
    date = opt('--date', datetime.date.today().isoformat())

    try:
        if from_file:
            raw = open(from_file, 'rb').read()
            method = f'Raw HTML read from a saved file ({os.path.basename(from_file)}) and parsed by tests/fetch_nsw.py.'
        else:
            req = urllib.request.Request(URL, headers={'User-Agent': UA, 'Accept': 'text/html'})
            with urllib.request.urlopen(req, timeout=60) as r:
                if r.geturl().split('?')[0] != URL:
                    print(f'COULD NOT RUN: the page redirected to {r.geturl()}'); sys.exit(2)
                raw = r.read()
            method = 'Raw HTML downloaded from the live page and parsed by tests/fetch_nsw.py.'
    except Exception as e:  # network errors, HTTP errors, missing file
        print(f'COULD NOT RUN: fetch failed — {e}'); sys.exit(2)

    data, problems = parse(raw.decode('utf-8', errors='replace'))
    if problems:
        print('COULD NOT RUN: the page was fetched but not every section could be read — '
              + '; '.join(problems) + '. NSW may have restructured the page; a person should look.')
        sys.exit(2)

    snap = {'schema': 2, 'url': URL, 'fetched_on': date, 'source_method': method,
            'raw_sha256': hashlib.sha256(raw).hexdigest()}
    snap.update(data)
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f'nsw-chest-pain-adult-{date}.json')
    if os.path.exists(path):
        # Never overwrite a dated record, and never let a snapshot be compared with itself.
        print(f'COULD NOT RUN: a snapshot dated {date} already exists ({os.path.basename(path)}); not overwritten.')
        sys.exit(2)
    with open(path, 'w', encoding='utf8') as f:
        json.dump(snap, f, indent=2, ensure_ascii=False); f.write('\n')
    print(path)


if __name__ == '__main__':
    main()
