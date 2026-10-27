#!/usr/bin/env python3
"""Executable, deterministic *documentation* oracles — NOT diK 1.0 product tests."""
from __future__ import annotations
import json,re,sys,unicodedata
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parents[1]

def resolve_label(x):
    ident=x['id']; locale=x['locale']; fallback=x['fallbacks']
    if not re.fullmatch(r'K[QP][1-9][0-9]*',ident):
        return {'status':'reject','code':'INVALID_SEMANTIC_ID'}
    if locale not in fallback:
        return {'status':'missing','id':ident}
    # Validate the fallback DAG independently of requested locale.
    def walk(node,visited):
        if node in visited: return False
        if node not in fallback: return False
        return all(walk(child,visited|{node}) for child in fallback[node])
    if not all(walk(k,set()) for k in fallback):
        return {'status':'reject','code':'FALLBACK_CYCLE'}
    for effective in [locale]+fallback[locale]:
        matches=[e for e in x['entries'] if e['id']==ident and e['locale']==effective]
        if not matches:continue
        top=max(e['priority'] for e in matches)
        winners=[e for e in matches if e['priority']==top]
        if len({e['term'] for e in winners})>1:
            return {'status':'conflicted','id':ident,'effective_locale':effective}
        return {'status':'resolved','id':ident,'effective_locale':effective,'term':winners[0]['term'],'fallback':effective!=locale}
    return {'status':'missing','id':ident}

def reverse(x):
    term=unicodedata.normalize('NFC',x['term'])
    ids=sorted(set(e['id'] for e in x['entries'] if e['locale']==x['locale'] and e['kind']==x['kind'] and unicodedata.normalize('NFC',e['term'])==term))
    return {'status':'no_candidate' if not ids else ('unique_candidate' if len(ids)==1 else 'ambiguous'),'ids':ids}

def eligible_crosswalk(x):
    identity=x['internal'];external=x['external']
    type_match=bool((re.fullmatch(r'KQ[1-9]\d*',identity) and re.fullmatch(r'Q[1-9]\d*',external)) or (re.fullmatch(r'KP[1-9]\d*',identity) and re.fullmatch(r'P[1-9]\d*',external)))
    eligible=bool(type_match and x['relation']=='exactMatch' and x['status']=='accepted' and x.get('reviewer') and x.get('method') and x.get('decision') and x.get('evidence') and all(re.fullmatch(r'KS[1-9]\d*',v) for v in x['evidence']))
    return {'eligible':eligible}

def coverage(x):
    counts=Counter(x['states'][i] for i in set(x['ids']))
    total=len(set(x['ids']));assert set(x['states'])==set(x['ids'])
    direct=counts['direct'];fallback=counts['fallback'];missing=counts['missing'];conflicted=counts['conflicted']
    assert direct+fallback+missing+conflicted==total
    return dict(total=total,direct=direct,fallback=fallback,missing=missing,conflicted=conflicted,complete_direct=bool(x['denominator_known'] and total>0 and direct==total and not conflicted),complete_usable=bool(x['denominator_known'] and total>0 and direct+fallback==total and not conflicted))

def idempotence(x):
    if x['new_key']!=x['previous_key']:return {'action':'start'}
    if x['new_digest']!=x['previous_digest']:return {'action':'reject','code':'IDEMPOTENCY_CONFLICT'}
    return {'action':'replay'}

FUNCS={'label':resolve_label,'reverse':reverse,'eligible_crosswalk':eligible_crosswalk,'coverage':coverage,'idempotence':idempotence}
def validate():
    suite=json.loads((ROOT/'tests/reference_vectors.json').read_text('utf-8'))
    valid_req=json.loads((ROOT/'tests/requirements.json').read_text('utf-8'))
    requirements={r['requirement_id'] for r in valid_req['requirements']}
    failures=[];ids=[]
    for item in suite['vectors']:
        ids.append(item['case_id'])
        if item['requirement_id'] not in requirements:failures.append(f'unknown requirement {item["case_id"]}')
        if item['run_status']!='DOC_ORACLE_ONLY':failures.append(f'wrong run status {item["case_id"]}')
        try:
            result=FUNCS[item['operation']](item['input'])
            if result!=item['expected']:failures.append(f'{item["case_id"]}: expected {item["expected"]}, got {result}')
        except Exception as exc:failures.append(f'{item["case_id"]}: {type(exc).__name__}: {exc}')
    if len(set(ids))!=len(ids):failures.append('duplicate vector ID')
    print(json.dumps({'status':'PASS' if not failures else 'FAIL','kind':'DOCUMENTARY_ORACLES_ONLY','vectors_run':len(ids),'errors':failures},ensure_ascii=False,indent=2))
    return 0 if not failures else 1
if __name__=='__main__':sys.exit(validate())
