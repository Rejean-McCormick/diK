"""V5.3: deterministic schemas, exact crosswalk boundaries and resumable inspection."""
import hashlib
import json
from pathlib import Path

import pytest

from dik.scan14 import TARGET_LOCALES
from dik.wikidata_v53 import (MAX_JSON_LINE, observe_thematic_v53,
                               probe, recognize, scan_file)


def _registered(tmp_path, lines, name='City.jsonl'):
    root=tmp_path/'gf-wikidata-tools'/'data';root.mkdir(parents=True,exist_ok=True)
    p=root/name
    p.write_bytes(b''.join(line if isinstance(line,bytes) else (json.dumps(line,ensure_ascii=False)+'\n').encode() for line in lines))
    entry={'source_id':'local-1','kind':'wikidata_thematic_candidate',
           'path':str(p),'root':str(tmp_path),'size_bytes':p.stat().st_size,
           'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
           'allowed_for_resolution':False}
    return p,entry


def _scan(tmp_path,entry, wanted={'Q17'}, **kwargs):
    return scan_file(entry,wanted=wanted,locales=tuple(TARGET_LOCALES),
                     checkpoint_dir=tmp_path/'reports'/'checkpoints',**kwargs)


def test_exact_14_locales_qid_keyed_and_no_fallback(tmp_path):
    _, entry=_registered(tmp_path,[{'Q17':{'fr':'étoile','en':'star','nb':'bokmål','nn':'nynorsk'}}])
    out,hits,diag=_scan(tmp_path,entry)
    assert diag['schema_id']=='qp_keyed_locales/1'
    assert diag['status']=='candidate_labels_observed' and diag['completed']
    assert {(r['qp'],r['locale']) for r in out}=={('Q17','fr'),('Q17','en'),('Q17','nn')}
    assert len(hits)==1 and diag['activations']==0


def test_typed_roles_statement_no_word_inference(tmp_path):
    _, entry=_registered(tmp_path,[{'subject':{'id':'Q17'},'predicate':{'id':'P31'},'object':{'id':'Q5'}}])
    out,hits,diag=_scan(tmp_path,entry,wanted={'Q17','P31','Q5'})
    assert diag['schema_id']=='statement_triple/1'
    assert diag['status']=='complete_overlap_no_lexical_field'
    assert out==[]
    assert {x['role'] for x in hits}=={'entity_subject'}
    assert not any(x.get('labels') for x in hits)


def test_candidate_qid_does_not_create_authority(tmp_path):
    _, entry=_registered(tmp_path,[{'semantic_id':'KQ123','candidate_qid':'Q17','confidence':0.8,'label':'ignored'}])
    out,hits,diag=_scan(tmp_path,entry)
    assert diag['schema_id']=='identity_candidate/1'
    assert out==[] and hits==[]
    assert diag['status']=='no_eligible_lexical_identity'


def test_unknown_schema_refuses_absence_and_no_recursive_guesses(tmp_path):
    _, entry=_registered(tmp_path,[{'something':{'Q17':{'fr':'wrong'}}}])
    out,hits,diag=_scan(tmp_path,entry)
    assert out==hits==[]
    assert diag['status']=='schema_unknown' and diag['completed'] is False
    assert recognize({'claim':{'value':{'id':'Q17'}}})[1]==[]
    assert recognize({'id':'L1','labels':{'fr':'word'}})[1]==[]
    assert recognize({'qid':'Q0017','labels':{'fr':'invalid'}})[1]==[]


def test_hash_stale_before_read(tmp_path):
    p,entry=_registered(tmp_path,[{'Q17':{'fr':'good'}}])
    p.write_text(json.dumps({'Q17':{'fr':'changed'}})+'\n')
    out,hits,diag=_scan(tmp_path,entry)
    assert not out and diag['status']=='pointer_stale'


def test_bom_last_line_and_unicode(tmp_path):
    _,entry=_registered(tmp_path,[b'\xef\xbb\xbf'+json.dumps({'Q17':{'fr':'électricité','en':'electricity'}},ensure_ascii=False).encode('utf-8')])
    out,_,diag=_scan(tmp_path,entry)
    assert diag['completed'] and {x['form'] for x in out}=={'électricité','electricity'}


def test_checkpoint_resume_equals_uninterrupted(tmp_path):
    data=[{'id':'Q17','labels':{'fr':f'forme {i}'}} for i in range(9)]
    _,entry=_registered(tmp_path,data)
    full,_,d1=_scan(tmp_path/'fresh',_clone(tmp_path/'fresh',entry),max_rows_per_pass=0)
    one,_,d2=_scan(tmp_path,entry,max_rows_per_pass=3)
    assert d2['status']=='partial_budget' and not d2['completed']
    assert len(one)==3
    two,_,d3=_scan(tmp_path,entry,max_rows_per_pass=3)
    assert d3['status']=='partial_budget' and len(two)==6
    three,_,d4=_scan(tmp_path,entry,max_rows_per_pass=3)
    assert d4['status']=='partial_budget' and len(three)==9
    four,_,d5=_scan(tmp_path,entry,max_rows_per_pass=3)
    assert d5['completed'] and d5['status']=='conflict'
    assert sorted(x['form'] for x in full)==sorted(x['form'] for x in four)
    assert d5['lines_read']==9 and d5['resumed']
    fifth,_,d6=_scan(tmp_path,entry)
    assert len(fifth)==9 and d6['lines_read']==9


def _clone(dest,entry):
    """Independent run with the same verified pointer and a different checkpoint folder."""
    dest.mkdir(parents=True,exist_ok=True)
    return entry


def test_150001_line_budget_resume_has_no_false_no_overlap(tmp_path):
    data=[{'id':'Q100','labels':{'fr':'autre'}} for _ in range(150000)]
    data.append({'id':'Q17','labels':{'fr':'trouvé après plafond'}})
    _,entry=_registered(tmp_path,data)
    a,_,first=_scan(tmp_path,entry,max_rows_per_pass=150000)
    assert first['status']=='partial_budget' and not first['completed']
    assert first['rows_matching_accepted_qp']==0
    b,_,second=_scan(tmp_path,entry,max_rows_per_pass=150000)
    assert second['completed'] and second['status']=='candidate_labels_observed'
    assert second['lines_read']==150001 and b[0]['form']=='trouvé après plafond'


def test_conflicts_between_sources_and_deduplicate_bytes(tmp_path):
    p1,r1=_registered(tmp_path,[{'Q17':{'fr':'premier'}}],'City.jsonl')
    p2,r2=_registered(tmp_path,[{'Q17':{'fr':'second'}}],'University.jsonl')
    r2['source_id']='local-2'
    out,profiles,summary,hits=observe_thematic_v53({'sources':[r1,r2]},wanted={'Q17'},
                          locales=tuple(TARGET_LOCALES),checkpoint_dir=tmp_path/'reports'/'cp')
    assert summary['conflicting_pairs']==1 and summary['activations']==0
    assert all(x['status']=='conflict' for x in out[('Q17','fr')])
    assert len(hits)==2
    p2.write_bytes(p1.read_bytes())
    r2.update(size_bytes=p2.stat().st_size,sha256=hashlib.sha256(p2.read_bytes()).hexdigest())
    _,profiles,summary,_=observe_thematic_v53({'sources':[r1,r2]},wanted={'Q17'},
                          locales=tuple(TARGET_LOCALES),checkpoint_dir=tmp_path/'reports'/'cp')
    assert summary['identical_copies_skipped']==1


def test_real_qid_sample_shape(tmp_path):
    sample=Path('/mnt/data/Pasted text(20261123-135505).txt')
    if not sample.exists():pytest.skip('User sample not mounted')
    out=[]
    for line in sample.read_text(encoding='utf-8').splitlines():
        if line.strip():
            shape, vals=recognize(json.loads(line))
            out.append((shape,vals))
    assert len(out)==50 and all(s=='qp_keyed_locales/1' for s,_ in out)
    assert all(item['role']=='lexical_entity' for _, vals in out for item in vals)


def test_checkpoint_rebuilt_when_accepted_index_changes(tmp_path):
    _,entry=_registered(tmp_path,[{'Q17':{'fr':'attesté'}},{'Q18':{'fr':'autre'}}])
    first,_,diag=_scan(tmp_path,entry,wanted={'Q17'},max_rows_per_pass=1)
    assert diag['status']=='partial_budget' and len(first)==1
    second,_,diag2=_scan(tmp_path,entry,wanted={'Q18'})
    assert diag2['completed'] and diag2['lines_read']==2
    assert {x['qp'] for x in second}=={'Q18'}
    assert not diag2['resumed']


def test_valid_json_null_is_not_extracted_as_qp(tmp_path):
    # `null` is valid JSON but not a valid lexical/statement object.
    _,entry=_registered(tmp_path,[b'null\n',b'null\n'])
    _,_,diag=_scan(tmp_path,entry)
    assert diag['status']=='schema_unknown' and not diag['completed']


def test_statement_object_is_not_joined_as_lexical_subject(tmp_path):
    _,entry=_registered(tmp_path,[{'subject':'Q999','predicate':'P31','object':'Q17'}])
    forms,hits,diag=_scan(tmp_path,entry,wanted={'Q17','P31'})
    assert forms==[] and hits==[]
    assert diag['rows_with_qp']==1
    assert diag['status']=='complete_no_accepted_qp_overlap'
