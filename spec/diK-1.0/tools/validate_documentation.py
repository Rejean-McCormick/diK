#!/usr/bin/env python3
"""Documentation conformance; strict mode requires pinned originals. NOT product certification."""
from __future__ import annotations
from pathlib import Path
import json,re,hashlib,sys,os,argparse,subprocess
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--strict',action='store_true',help='require all SOURCE_LOCK input files and official Framework fixtures')
args=parser.parse_args()
errors=[];count={};warnings=[]
def check(cond,description):
    if not cond:errors.append(description)
def read_json(path):
    try:return json.loads(path.read_text(encoding='utf-8'))
    except Exception as e:errors.append(f'invalid JSON {path}: {e}');return None
try:from jsonschema import Draft202012Validator
except ImportError:
    Draft202012Validator=None
    errors.append('jsonschema missing: full schema validation not performed')
schemas=sorted((ROOT/'contracts').glob('*.schema.json'))
for f in schemas:
    d=read_json(f)
    if d is None:continue
    ex=ROOT/'examples/proposed'/f.name.replace('.schema.json','.example.json')
    check(ex.exists(),f'missing example for {f.name}')
    if Draft202012Validator:
        try:
            Draft202012Validator.check_schema(d)
            if ex.exists():
                e=read_json(ex)
                if e is not None: Draft202012Validator(d).validate(e)
        except Exception as exc:errors.append(f'contract example error {f.name}: {exc}')
count['schema_examples']=len(schemas)
if Draft202012Validator:
    for name in ['dik-review-decision','dik-import-job','dik-semantic-patch-intent']:
        schema=read_json(ROOT/'contracts'/f'{name}.schema.json')
        ex=read_json(ROOT/'examples/proposed'/f'{name}.example.json')
        if name=='dik-review-decision': ex['evidence_refs']=[]
        if name=='dik-import-job': ex.update(status='published');ex.pop('output_catalog_sha256',None)
        if name=='dik-semantic-patch-intent': ex['review_status']='approved';ex.pop('reviewer_id',None);ex.pop('evidence_refs',None)
        check(not Draft202012Validator(schema).is_valid(ex),f'negative schema case accepted: {name}')
count['contract_negative_checks']=3
md=list(ROOT.rglob('*.md'));missing=[]
pat=re.compile(r'(?<!!)\[[^\]]*\]\(([^)]+)\)')
for f in md:
    txt=f.read_text(encoding='utf-8');txt=re.sub(r'```.*?```','',txt,flags=re.S)
    for raw in pat.findall(txt):
        url=raw.strip().split('#',1)[0].split(' ',1)[0]
        if not url or url.startswith(('http://','https://','mailto:')):continue
        if not (f.parent/url.replace('%20',' ')).exists():missing.append(f'{f.relative_to(ROOT)} -> {raw}')
check(not missing,'broken markdown links: '+repr(missing));count['markdown_files']=len(md)
# TCK declared NOT RUN by construction
cases=read_json(ROOT/'tests/TCK_CASES.json')
if cases:
    tests=cases['cases'];ids=[t['case_id'] for t in tests]
    check(len(ids)==len(set(ids)),'duplicate TCK case IDs')
    check(all(t['result']=='NOT_RUN' for t in tests),'TCK falsely marked completed')
    count['planned_tck_cases']=len(tests)
req=read_json(ROOT/'tests/requirements.json')
if req:
    requirements=req['requirements'];ids=[x['requirement_id'] for x in requirements]
    check(len(ids)==len(set(ids)),'duplicate requirement IDs')
    # Actual normative headings, never inferred by fabricated consecutive ranges.
    ids_in_docs=set()
    heading_pattern=re.compile(r'^##\s+((?:ID|LEX|XW|IMP|PRJ|MIG|COV|OPS|API|UI|SEC|PERF|TCK)-\d{3})\s*[—:-]',re.M)
    for doc in (ROOT/'docs').glob('*.md'):
        ids_in_docs.update(heading_pattern.findall(doc.read_text('utf-8')))
    check(set(ids)==ids_in_docs,f'requirement registry differs from actual documented headings: missing={sorted(ids_in_docs-set(ids))}, extra={sorted(set(ids)-ids_in_docs)}')
    check(len(ids_in_docs)==87,'expected 87 titled requirements; review new normative heading before editing the lock')
    for r in requirements:
        for name in ('positive_test','negative_test'):
            t=r.get(name,{})
            check(t.get('result')=='NOT_RUN' and t.get('evidence') is None,f'future product test claimed: {r["requirement_id"]}/{name}')
        check((ROOT/'docs'/r['source_document']).is_file(),f'missing requirement source doc {r["requirement_id"]}')
    count['planned_requirements']=len(requirements)
# run exact documentary oracles; these do not run diK product
run=subprocess.run([sys.executable,str(ROOT/'tools/verify_reference_vectors.py')],capture_output=True,text=True)
check(run.returncode==0,'reference vector oracle failed: '+run.stdout+run.stderr)
try:count['documentary_oracle_vectors']=json.loads(run.stdout).get('vectors_run')
except Exception:count['documentary_oracle_vectors']=None
lock=read_json(ROOT/'SOURCE_LOCK.json')
source_root=os.environ.get('DIK_SOURCE_DATA_ROOT')
if lock:
    verified=0
    for key,s in lock['sources'].items():
        original=s['source_path'].removeprefix('[uploaded-session]/')
        loc=Path(source_root)/original if source_root else Path('/__missing_diK_sources__')/original
        if not loc.exists():
            if args.strict:errors.append(f'REQUIRED source missing: {key}: {loc}')
            continue
        check(hashlib.sha256(loc.read_bytes()).hexdigest()==s['sha256'],f'SOURCE_LOCK SHA mismatch: {key}')
        verified+=1
    count['locked_source_records']=len(lock['sources'])
    count['sources_verified']=verified
    count['sources_unavailable']=len(lock['sources'])-verified
    if not args.strict and verified<len(lock['sources']): warnings.append('Source lock partly unavailable; not a strict qualification')
# Exact uploaded archive baselines are additionally checked in strict mode.
if lock:
    base=Path(source_root) if source_root else Path('/__missing_diK_sources__')
    archive_verified=0
    for archive_name,expected_sha in lock.get('uploaded_archives',{}).items():
        loc=base/archive_name
        if not loc.is_file():
            if args.strict:errors.append(f'REQUIRED archive missing: {archive_name}: {loc}')
            continue
        check(hashlib.sha256(loc.read_bytes()).hexdigest()==expected_sha,f'archive SHA mismatch: {archive_name}')
        archive_verified+=1
    count['locked_archive_records']=len(lock.get('uploaded_archives',{}))
    count['archives_verified']=archive_verified
framework_root=os.environ.get('KRISTAL_FRAMEWORK_ROOT')
fw=Path(framework_root) if framework_root else Path('/__missing_framework__')
files={'semantic-graph':'kristal-semantic-graph.schema.json','identity-registry':'kristal-identity-registry.schema.json','external-crosswalk':'kristal-external-crosswalk.schema.json','dik-coverage':'kristal-dik-coverage-report.schema.json','dik-conversion-plan':'kristal-dik-conversion-plan.schema.json'}
fw_count=0
if args.strict and (not fw.is_dir()):errors.append('REQUIRED KRISTAL_FRAMEWORK_ROOT not mounted')
if fw.is_dir() and Draft202012Validator:
    for ex_name,sch_name in files.items():
        original_schema=fw/'schemas/v11'/sch_name
        example=ROOT/'examples/framework-v11-unaltered'/f'{ex_name}.example.json'
        if not original_schema.exists() or not example.exists():
            if args.strict:errors.append(f'REQUIRED Framework schema/fixture missing: {ex_name}')
            continue
        s=read_json(original_schema);e=read_json(example)
        if s is not None and e is not None:
            try:Draft202012Validator(s).validate(e);fw_count+=1
            except Exception as exc:errors.append(f'official Framework schema mismatch: {ex_name}: {exc}')
else:
    if not args.strict:warnings.append('Official Framework fixtures not validated; set KRISTAL_FRAMEWORK_ROOT for a strict check')
count['framework_fixtures_validated']=fw_count
if args.strict:check(fw_count==5,'strict Framework fixtures incomplete')
print(json.dumps({'status':'PASS' if not errors else 'FAIL','mode':'STRICT_DOCS_WITH_UPSTREAM' if args.strict else 'DOCS_ONLY','NOTE':'Product TCK/diK 1.0 tests are NOT executed here','counts':count,'warnings':warnings,'errors':errors},ensure_ascii=False,indent=2))
sys.exit(bool(errors))
