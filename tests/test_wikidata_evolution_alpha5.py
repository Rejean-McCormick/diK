"""Offline identity-evolution tests: no upstream Wikidata access or canon writes."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import pytest

from dik.cli import make_parser, run
from dik.operations import DiKError
from dik.wikidata_evolution import analyze_evolution

DEMO = Path(__file__).resolve().parents[1] / 'examples' / 'demo'
SNAPSHOT = 'local-wikidata-2026-10-16'


def event(source: str, action='redirect', targets=None, reference='local-wikidata-record'):
    if targets is None:
        targets = ['Q9999'] if action == 'redirect' else []
    return {'source_snapshot': SNAPSHOT, 'source_reference': reference,
            'source_id': source, 'event_type': action, 'targets': targets}


def setup(tmp_path, events, crosswalk=None):
    path = tmp_path / 'observations.jsonl'
    path.write_text(''.join(json.dumps(e, ensure_ascii=False) + '\n' for e in events), encoding='utf-8')
    cr = tmp_path / 'crosswalk.json'
    obj = json.loads((DEMO / 'external-crosswalk.example.json').read_text()) if crosswalk is None else crosswalk
    cr.write_text(json.dumps(obj,ensure_ascii=False),encoding='utf-8')
    return path, cr


def analyze(tmp_path, records, crosswalk=None, **kwargs):
    path, cr = setup(tmp_path, records, crosswalk)
    return analyze_evolution(observations=path,crosswalk=cr,
        registry=DEMO/'identity-registry.example.json',namespace='example.org/kristal-demo',
        snapshot=SNAPSHOT, **kwargs)


def test_redirect_chain_proposal_does_not_modify_source(tmp_path):
    records=[event('Q8018', targets=['Q9000']),event('Q9000',targets=['Q9900'])]
    obs, cr=setup(tmp_path,records)
    before=(obs.read_bytes(),cr.read_bytes())
    events_file=tmp_path/'impacts.jsonl'
    result=analyze_evolution(observations=obs,crosswalk=cr,
        registry=DEMO/'identity-registry.example.json',namespace='example.org/kristal-demo',
        snapshot=SNAPSHOT,events_jsonl=events_file)
    assert result['affected_mappings']==1
    assert result['by_category']=={'redirect_chain':1}
    impact=result['samples'][0]
    assert impact['local_id']=='KQ1001' and impact['external_id']=='Q8018'
    assert impact['resolution']['path']==['Q8018','Q9000','Q9900']
    assert impact['resolution']['terminal_id']=='Q9900'
    assert impact['requires_review'] and not impact['crosswalk_changed']
    assert not result['normalized_digest_verified']
    assert (obs.read_bytes(),cr.read_bytes())==before
    assert json.loads(events_file.read_text())==impact
    with pytest.raises(DiKError,match='OUTPUT_EXISTS'):
        analyze_evolution(observations=obs,crosswalk=cr,
            registry=DEMO/'identity-registry.example.json',namespace='example.org/kristal-demo',
            snapshot=SNAPSHOT,events_jsonl=events_file)


def test_possible_merge_flags_existing_mapping(tmp_path):
    cw=json.loads((DEMO/'external-crosswalk.example.json').read_text())
    second=copy.deepcopy(cw['mappings'][0]); second['mapping_id']='map-second'
    second['local_ref']['id']='KQ1002';second['external_ref']['id']='Q9999'
    cw['mappings'].append(second)
    result=analyze(tmp_path,[event('Q8018',targets=['Q9999'])],crosswalk=cw)
    assert result['affected_mappings']==1
    assert result['by_category']=={'redirect_collision_review':1}
    assert result['collisions'][0]['local_ids']==['KQ1001','KQ1002']
    assert result['collisions'][0]['mapping_ids']==['map-augustin-demo','map-second']
    assert result['collisions'][0]['decision']=='human_review_required_no_identity_merge'


def test_retired_split_indirect_and_property(tmp_path):
    cw=json.loads((DEMO/'external-crosswalk.example.json').read_text())
    property_map=copy.deepcopy(cw['mappings'][0]);property_map['mapping_id']='property-map'
    property_map['local_ref']['id']='KP2001';property_map['external_ref']['id']='P50'
    cw['mappings'].append(property_map)
    a=analyze(tmp_path,[event('Q8018',targets=['Q42']),
        event('Q42','split_candidate',['Q901','Q902']),
        event('P50','retired')],crosswalk=cw)
    assert a['by_category']=={'possible_split':1,'retired_external_identifier':1}
    assert a['affected_mappings']==2
    split=next(x for x in a['samples'] if x['local_id']=='KQ1001')
    assert split['resolution']['candidates']==['Q901','Q902']
    assert next(x for x in a['samples'] if x['local_id']=='KP2001')['resolution']['kind']=='retired'


@pytest.mark.parametrize('records,error',[
    ([event('Q8018',targets=['Q20']),event('Q20',targets=['Q8018'])],'REDIRECT_CYCLE'),
    ([event('Q8018',targets=['Q8018'])],'REDIRECT_CYCLE'),
    ([event('Q8018',targets=['P31'])],'IDENTITY_KIND_MISMATCH'),
    ([event('Q8018'),event('Q8018')],'DUPLICATE_EVOLUTION_EVENT'),
    ([event('Q8018','split_candidate',['Q9'])],'INVALID_EVOLUTION_EVENT'),
    ([event('Q8018','retired',['Q9'])],'INVALID_EVOLUTION_EVENT'),
    ([event('Q8018',targets=['Q9','Q10'])],'INVALID_EVOLUTION_EVENT'),
    ([event('Q8018',targets=['Q1','Q1'])],'INVALID_EVOLUTION_EVENT'),
    ([{**event('Q8018'), 'semantic_id':'KQ1001'}],'INVALID_EVOLUTION_EVENT'),
    ([{**event('Q8018'), 'source_snapshot':'another-snapshot'}],'SNAPSHOT_MISMATCH'),
])
def test_rejects_unsafe_observations(tmp_path,records,error):
    with pytest.raises(DiKError,match=error):
        analyze(tmp_path,records)


def test_off_path_cycle_rejected(tmp_path):
    with pytest.raises(DiKError,match='REDIRECT_CYCLE'):
        analyze(tmp_path,[event('Q777',targets=['Q778']),event('Q778',targets=['Q777'])])


def test_hash_verified_and_mismatch(tmp_path):
    path, cw=setup(tmp_path,[event('Q8018')]); sha=hashlib.sha256(path.read_bytes()).hexdigest()
    kwargs=dict(observations=path,crosswalk=cw,registry=DEMO/'identity-registry.example.json',
        namespace='example.org/kristal-demo',snapshot=SNAPSHOT)
    assert analyze_evolution(**kwargs,approved_sha256=sha)['normalized_digest_verified']
    with pytest.raises(DiKError,match='INTEGRITY_MISMATCH'):
        analyze_evolution(**kwargs,approved_sha256='f'*64)
    with pytest.raises(DiKError,match='INVALID_APPROVED_SHA256'):
        analyze_evolution(**kwargs,approved_sha256='unknown')
    with pytest.raises(DiKError,match='NAMESPACE_MISMATCH'):
        analyze_evolution(**{**kwargs,'namespace':'other'})
    with pytest.raises(DiKError,match='INVALID_MAX_RECORDS'):
        analyze_evolution(**kwargs,max_records=0)
    with pytest.raises(DiKError,match='INVALID_SAMPLE_LIMIT'):
        analyze_evolution(**kwargs,sample_limit=1001)


def test_crosswalk_conflict_already_unacceptable(tmp_path):
    cw=json.loads((DEMO/'external-crosswalk.example.json').read_text())
    duplicate=copy.deepcopy(cw['mappings'][0]);duplicate['mapping_id']='duplicate'
    cw['mappings'].append(duplicate)
    with pytest.raises(Exception,match='duplicate accepted exact'):
        analyze(tmp_path,[event('Q8018')],crosswalk=cw)


def test_cli_evolution_without_publishing(tmp_path):
    obs,cw=setup(tmp_path,[event('Q8018',targets=['Q9999'])])
    parser=make_parser()
    args=parser.parse_args(['sync','evolution','--observations',str(obs),
      '--crosswalk',str(cw),'--registry',str(DEMO/'identity-registry.example.json'),
      '--namespace','example.org/kristal-demo','--snapshot',SNAPSHOT,
      '--output',str(tmp_path/'report.json')])
    result=run(args)
    assert result['affected_mappings']==1
    assert json.loads((tmp_path/'report.json').read_text())['canonical_mutation'] is False
    assert not list(tmp_path.glob('*new-crosswalk*'))


def test_overlong_line_and_output_collisions(tmp_path):
    obs,cw=setup(tmp_path,[event('Q8018')])
    obs.write_bytes(b'{' + b'x'*(256*1024) + b'}\n')
    with pytest.raises(DiKError,match='RECORD_TOO_LARGE'):
        analyze_evolution(observations=obs,crosswalk=cw,
            registry=DEMO/'identity-registry.example.json',namespace='example.org/kristal-demo',snapshot=SNAPSHOT)
    obs,cw=setup(tmp_path,[event('Q8018')])
    parser=make_parser()
    base=['sync','evolution','--observations',str(obs),'--crosswalk',str(cw),
      '--registry',str(DEMO/'identity-registry.example.json'),
      '--namespace','example.org/kristal-demo','--snapshot',SNAPSHOT]
    same=tmp_path/'same.jsonl'
    args=parser.parse_args(base+['--output',str(same),'--events',str(same)])
    with pytest.raises(DiKError,match='OUTPUT_PATH_COLLISION'):
        run(args)
    assert not same.exists()
    existing=tmp_path/'existing.json';existing.write_text('important')
    args=parser.parse_args(base+['--output',str(existing),'--events',str(tmp_path/'never.jsonl')])
    with pytest.raises(DiKError,match='OUTPUT_EXISTS'):
        run(args)
    assert existing.read_text()=='important' and not (tmp_path/'never.jsonl').exists()
