#!/usr/bin/env python3
"""Pull the SAT Suite Educator Question Bank into a single questions.js blob."""
import json, re, sys, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor

LIST_URL = 'https://qbank-api.collegeboard.org/msreportingquestionbank-prod/questionbank/digital/get-questions'
ITEM_URL = 'https://qbank-api.collegeboard.org/msreportingquestionbank-prod/questionbank/digital/get-question'
# Powers the bank UI's "Exclude Active Questions" checkbox: two lists of
# external_ids that College Board flags as in active use on test forms.
LOOKUP_URL = 'https://qbank-api.collegeboard.org/msreportingquestionbank-prod/questionbank/lookup'

SECTIONS = {
    'rw':   {'test': 1, 'domain': 'INI,CAS,EOI,SEC', 'live': 'readingLiveItems'},
    'math': {'test': 2, 'domain': 'H,P,Q,S',         'live': 'mathLiveItems'},
}


def post(url, payload, tries=4):
    for attempt in range(tries):
        try:
            req = urllib.request.Request(
                url, data=json.dumps(payload).encode(),
                headers={'Content-Type': 'application/json'})
            return json.load(urllib.request.urlopen(req, timeout=30))
        except Exception:
            if attempt == tries - 1:
                return None
    return None


# --- HTML cleanup -----------------------------------------------------------
# <mfenced> was dropped from MathML Core; Chrome/Safari won't render it.
# Rewrite it into explicit <mo> delimiters so the parens survive.
MFENCED = re.compile(r'<mfenced([^>]*)>(.*?)</mfenced>', re.S | re.I)
ATTR = re.compile(r'(\w+)\s*=\s*"([^"]*)"')


def fix_mfenced(html):
    prev = None
    while prev != html:  # nested mfenced needs repeated passes
        prev = html
        html = MFENCED.sub(_expand, html)
    return html


def _expand(m):
    attrs = dict(ATTR.findall(m.group(1) or ''))
    open_c = attrs.get('open', '(')
    close_c = attrs.get('close', ')')
    return '<mrow><mo>%s</mo>%s<mo>%s</mo></mrow>' % (open_c, m.group(2), close_c)


ALTTEXT = re.compile(r'\s+alttext="[^"]*"')


def clean(html):
    if not html:
        return ''
    return ALTTEXT.sub('', fix_mfenced(html))


# --- fetch ------------------------------------------------------------------
def fetch_one(meta):
    d = post(ITEM_URL, {'external_id': meta['external_id']})
    if not d:
        return None
    opts = d.get('answerOptions') or []
    ans = d.get('correct_answer') or []
    qtype = d.get('type') or 'mcq'
    if qtype == 'mcq' and (not opts or not ans):
        return None
    return {
        'id': meta['questionId'],
        'dom': meta['primary_class_cd'],
        'domName': meta['primary_class_cd_desc'],
        'skill': meta['skill_desc'],
        'diff': meta['difficulty'],
        'type': qtype,
        'sti': clean(d.get('stimulus')),
        'stem': clean(d.get('stem')),
        'opts': [clean(o.get('content')) for o in opts],
        'ans': ans,
        'rat': clean(d.get('rationale')),
        'live': 1 if meta['_live'] else 0,
    }


def live_sets():
    """external_ids College Board flags as in active use, per section."""
    look = json.load(urllib.request.urlopen(LOOKUP_URL, timeout=30))
    return {name: set(look[p['live']]) for name, p in SECTIONS.items()}


def get_meta(name, params, live):
    meta = [m for m in post(LIST_URL, {'asmtEventId': 99,
                                       'test': params['test'],
                                       'domain': params['domain']})
            if m.get('external_id')]
    for m in meta:
        m['_live'] = m['external_id'] in live[name]
    return meta


def write_gridins(out, path='gridins.js'):
    """Math question ids that are grid-ins (student-produced response).

    The metadata endpoint doesn't expose question type, but module building needs
    to know it *before* fetching bodies in order to place exactly 6 grid-ins per
    math module. These are bare identifiers, not question content. R&W is 100%
    multiple choice, so only math needs a list.
    """
    ids = sorted(q['id'] for q in out['math'] if q['type'] == 'spr')
    with open(path, 'w') as f:
        f.write('window.GRIDINS=')
        json.dump(ids, f, separators=(',', ':'))
        f.write(';\n')
    print('wrote %s (%d grid-in ids, %.1f KB)' % (path, len(ids),
                                                  len(json.dumps(ids)) / 1024))


def write(dest, out):
    with open(dest, 'w') as f:
        f.write('window.QBANK=')
        json.dump(out, f, separators=(',', ':'), ensure_ascii=False)
        f.write(';\n')
    import os
    print('wrote %s (%.1f MB)' % (dest, os.path.getsize(dest) / 1e6))


def annotate(dest, live):
    """Refresh only the `live` flags on an existing questions.js — no bodies."""
    src = open(dest).read()
    out = json.loads(src[src.index('=') + 1:src.rstrip().rstrip(';').rindex('}') + 1])
    for name, params in SECTIONS.items():
        flag = {m['questionId']: m['_live'] for m in get_meta(name, params, live)}
        n = 0
        for q in out[name]:
            q['live'] = 1 if flag.get(q['id']) else 0
            n += q['live']
        print('%s: %d active, %d safe' % (name, n, len(out[name]) - n))
    write(dest, out)


def main():
    dest = sys.argv[1]
    live = live_sets()
    print('active items: ' + ', '.join('%s %d' % (k, len(v)) for k, v in live.items()))

    if '--annotate' in sys.argv:
        return annotate(dest, live)

    out = {}
    for name, params in SECTIONS.items():
        meta = get_meta(name, params, live)
        print('%s: fetching %d questions...' % (name, len(meta)), flush=True)
        with ThreadPoolExecutor(max_workers=24) as pool:
            got = list(pool.map(fetch_one, meta))
        qs = [q for q in got if q]
        print('  -> %d ok, %d dropped, %d active' % (
            len(qs), len(got) - len(qs), sum(q['live'] for q in qs)), flush=True)
        out[name] = qs
    write(dest, out)


if __name__ == '__main__':
    main()
