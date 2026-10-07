#!/usr/bin/env python3
"""
Build (or check) the machine-readable copy of the NSW criteria for software and AI agents.

Usage:
  python3 tests/build_data.py            write data/nsw-chest-pain-adult.json from the newest snapshot
  python3 tests/build_data.py --check    exit 1 if the data file's NSW content differs from the newest snapshot
  python3 tests/build_data.py <snapshot.json>   build from a named snapshot

The data file is generated, never hand-edited. Its NSW content (date, lists, notes, triage
categories, emergency criteria) is copied unchanged from a snapshot in tests/fetched/ that was
parsed from the NSW page's own HTML. The monthly check rebuilds it only when that month's
check is CONSISTENT, so "last_verified" is the date of the last successful comparison.
"""
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'data', 'nsw-chest-pain-adult.json')
REPO = 'https://github.com/drcolozz24/referral-completeness-demo'
SITE = 'https://drcolozz24.github.io/referral-completeness-demo'
FAQ = 'https://www.health.nsw.gov.au/outpatients/referrals/Pages/faqs.aspx'
NSW_CONTENT = ('current_as_at', 'required', 'if_available', 'triage_categories', 'emergency', 'other_text')


def items(entries):
    out = []
    for e in entries:
        e = {'text': e} if isinstance(e, str) else e
        item = {'text': e['text']}
        if e.get('note'):
            item['note'] = e['note']
        if e.get('children'):
            item['sub_items'] = [{'text': c} for c in e['children']]
        out.append(item)
    return out


def build(snap):
    if snap.get('schema', 1) < 2 or not snap.get('raw_sha256'):
        sys.exit('COULD NOT RUN: the data file is only built from a snapshot parsed from the NSW page\'s own HTML')
    return {
        'schema': 1,
        'title': 'NSW Statewide Referral Criteria — chest pain, discomfort and/or tightness in adult patients',
        'what_this_is': 'A machine-readable copy of one NSW Health referral-criteria page, published by the '
                        'Referral Completeness Demonstration so that software and AI agents can read the same '
                        'verified text the demonstration page shows. It is a copy; the NSW Health page is authoritative.',
        'jurisdiction': 'New South Wales, Australia',
        'applies_to': 'Referrals of adults with chest pain to NSW public specialist outpatient (cardiology) services',
        'source': {
            'publisher': 'NSW Health',
            'url': snap['url'],
            'attribution': '© State of New South Wales NSW Ministry of Health. For current information go to www.health.nsw.gov.au.',
            'licence': 'Creative Commons Attribution 4.0',
            'licence_url': 'https://creativecommons.org/licenses/by/4.0/',
            'changes_made': 'Wording unchanged. Whitespace collapsed and zero-width characters removed. Lists and the '
                            'triage table are represented as structured data. NSW Health has not reviewed or endorsed this file.',
        },
        'current_as_at': snap['current_as_at'],
        'last_verified': {
            'date': snap['fetched_on'],
            'method': snap.get('source_method', ''),
            'result': 'This file was built from that snapshot. The monthly check rebuilds it only when the '
                      'comparison with the live NSW page is consistent.',
            'record_of_checks': REPO + '/blob/main/tests/fetched/CHECK-LOG.md',
        },
        'use': {
            'read_first': 'Check the emergency criteria before anything else. NSW states that those presentations are '
                          'for emergency care, not for an outpatient referral.',
            'intended_for': 'Discussion, education and research about what referrals contain. Reading this file to '
                            'learn what NSW publishes is the intended use.',
            'not_for': [
                'This is not a clinical tool or a medical device and makes no clinical recommendation.',
                'Do not use it to decide the care of any person, or to assess, score, accept or decline a real referral.',
                'Do not treat it as current without checking current_as_at and last_verified against the NSW page.',
                'It covers one condition in one jurisdiction. It says nothing about other conditions or other states.',
            ],
            'when_quoting': 'Quote items exactly, give the NSW attribution and licence above, and state the current_as_at date.',
        },
        'emergency': snap['emergency'] | {'items': items(snap['emergency']['items'])},
        'triage_categories': snap['triage'],
        'required': items(snap['required']),
        'if_available': items(snap['if_available']),
        'other_text': snap.get('extra_text', {}),
        'nsw_statements_on_missing_information': {
            'source_url': FAQ,
            'source_title': 'Frequently asked questions about state-wide referral criteria',
            'page_dated': '6 June 2025',
            'verified': 'Checked character for character against the page\'s HTML on 7 October 2026. '
                        'Not covered by the monthly check.',
            'statements': [
                {'about': 'the required list',
                 'quote': 'Mandatory information that is to be supplied with referrals to NSW public specialist outpatient services'},
                {'about': 'what follows when the criteria are not referenced',
                 'quote': 'As a result, patients may experience delayed access to care due to NSW public specialist '
                          'outpatient services seeking additional clinical and/or referral information from referring '
                          'health professionals to support referral screening and triage and/or returning the referral '
                          'to referring health professionals with advice of alternative care options.'},
                {'about': 'overriding the criteria',
                 'quote': 'may override the SRC should it be deemed necessary'},
            ],
            'note': 'NSW does not say which outcome applies to a given referral.',
        },
        'published_by': {
            'project': 'Referral Completeness Demonstration',
            'creator': 'Dr Ferney Bernal Buitrago, general practitioner, with AI assistance',
            'page': SITE + '/',
            'repository': REPO,
            'report_an_error': REPO + '/issues',
        },
    }


def newest():
    files = sorted(glob.glob(os.path.join(ROOT, 'tests', 'fetched', 'nsw-chest-pain-adult-*.json')))
    return files[-1] if files else sys.exit('COULD NOT RUN: no snapshot in tests/fetched')


def main():
    args = [a for a in sys.argv[1:] if a != '--check']
    check = '--check' in sys.argv[1:]
    path = args[0] if args else newest()
    data = build(json.load(open(path, encoding='utf8')))
    if check:
        try:
            have = json.load(open(OUT, encoding='utf8'))
        except (OSError, ValueError) as e:
            sys.exit(f'DATA FILE PROBLEM: {e}')
        bad = [k for k in NSW_CONTENT if have.get(k) != data[k]]
        fixed = [k for k in data if k not in NSW_CONTENT and k != 'last_verified' and have.get(k) != data[k]]
        if bad or fixed:
            print(f'DATA FILE DIFFERS from {os.path.basename(path)}: ' + ', '.join(bad + fixed))
            print('NSW content in data/ is copied from the newest snapshot. If NSW has changed its page, the author '
                  'reviews the change first; then rebuild with: python3 tests/build_data.py')
            sys.exit(1)
        print(f'data file matches {os.path.basename(path)}; last verified {have["last_verified"]["date"]}')
        return
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False); f.write('\n')
    print(OUT)


if __name__ == '__main__':
    main()
