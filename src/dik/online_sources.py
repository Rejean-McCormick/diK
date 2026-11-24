"""V5.6: targeted, consented Wikidata label retrieval for accepted KQ/KP exactMatch.

Online access is *only* to Wikidata's fixed HTTPS Action API. No local labels,
KQ/KP, paths, or private content are sent. Data are retained as read-only,
content-addressed evidence in diK/reports and NEVER promote a candidate.

Kaikki/Wiktionary and GF-RGL are documented discovery-only providers; unlike
Wikidata entity labels, their lemmas/grammars cannot be joined to an identity
without an explicit semantic alignment and appropriate licensing review.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path
from typing import Callable

from ._framework import dictionaries as d
from .kristals14 import _select, _source, discover
from .resource_locator import _unsafe
from .scan14 import TARGET_LOCALES

API_ENDPOINT = 'https://www.wikidata.org/w/api.php'
QPID = re.compile(r'^[QP][1-9][0-9]*$')
SHA = re.compile(r'^[0-9a-f]{64}$')
SCHEMA = 'dik.online-wikidata-cache/5.6.0'
PROVIDER = 'wikidata_action_api'
LICENSE = 'CC0-1.0'
DEFAULT_USER_AGENT = ('diK-Semantic-Lexical-Audit/5.6 (read-only Wikidata label requests; '
                      'documentation: https://www.wikidata.org/wiki/Wikidata:Data_access)')
MAX_RESPONSE_BYTES = 8 * 1024 * 1024

PROVIDERS = (
    {'id': 'wikidata_action_api', 'url': API_ENDPOINT,
     'rights': 'CC0-1.0', 'state': 'TARGETED_FETCH_IMPLEMENTED',
     'identity': 'Q/P only, via accepted KS-backed exactMatch',
     'notes': 'Only explicit labels in the 14 target language codes, no fallback, no auto-promotion'},
    {'id': 'kaikki_wiktionary', 'url': 'https://kaikki.org/dictionary/',
     'rights': 'CC-BY-SA and GFDL; review needed for redistribution',
     'state': 'DISCOVERY_ONLY',
     'identity': 'No accepted KQ/KP or Wikidata-QID identity keys by default',
     'notes': 'Do not derive exactMatch from word resemblance; import deferred'},
    {'id': 'gf_rgl', 'url': 'https://github.com/GrammaticalFramework/gf-rgl',
     'rights': 'LGPL and BSD components; check each file',
     'state': 'DISCOVERY_ONLY', 'identity': 'Grammar/inflection, not KQ/KP mapping',
     'notes': 'Existing local GF preferred; no automatic lexeme alignment or download'},
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def json_bytes(obj: object) -> bytes:
    return (json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(',', ':'))+'\n').encode('utf-8')


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def _check_path(path: Path, root: Path):
    root = root.absolute()
    if not path.absolute().is_relative_to(root):
        raise ValueError('Dossier/cache hors des rapports diK')
    for p in (path, *path.parents):
        if p == root.parent:
            break
        if (p.exists() or p.is_symlink()) and _unsafe(p):
            raise ValueError(f'Lien symbolique/jonction interdit dans rapports: {p}')
        if p == root:
            break


def _root(dik_root: str | Path) -> Path:
    root = Path(dik_root).expanduser().absolute()
    if not root.is_dir() or _unsafe(root) or not (root / 'src/dik/cli.py').is_file():
        raise ValueError('Dépôt diK invalide')
    report = root/'reports'/'sources'/'online'/'wikidata_v56'
    _check_path(report, root)
    report.mkdir(parents=True, exist_ok=True)
    return report


def accepted_official_qp(official_root: str | Path, *, min_kristals: int = 126) -> tuple[dict, dict]:
    """Only canon v11 selected official Kristals; never trust a lexical guess."""
    from .resolution14 import _read_crosswalk
    root = Path(official_root).expanduser().absolute()
    if not root.is_dir() or _unsafe(root):
        raise ValueError('Racine des Kristals officiels invalide')
    children = sorted((p for p in root.iterdir() if p.is_dir() and not _unsafe(p) and
                       (p/'kristal.discovery.json').is_file() and
                       not _unsafe(p/'kristal.discovery.json')), key=lambda p:p.name.casefold())
    if len(children) < min_kristals or min_kristals < 1:
        raise ValueError(f'Portfolio officiel incomplet: {len(children)} < {min_kristals}')
    by_folder = {c.folder: c for c in discover(root)}
    accepted = {}  # (namespace, semantic_id) -> Wikidata Q/P
    conflicts = set()
    cw = {}
    evaluated = 0
    for folder in children:
        candidate = by_folder.get(folder)
        if not candidate:
            continue
        snapshot, _, _ = _select(candidate)
        if snapshot is None:
            continue
        try:
            ns, identities, *_ = _source(snapshot)
            matched, _ = _read_crosswalk(snapshot, ns, {s for s, _ in identities})
            for sid, qp in matched.items():
                if not QPID.fullmatch(qp):
                    continue
                key = (ns, sid)
                if key in accepted and accepted[key] != qp:
                    conflicts.add(key)
                else:
                    accepted[key] = qp
            cw[folder.name] = d.sha256(snapshot.crosswalk)
            evaluated += 1
        except (ValueError, OSError, UnicodeError, KeyError, TypeError):
            continue
    for key in conflicts:
        del accepted[key]
    summary = {'official_kristals':len(children), 'evaluated':evaluated,
               'accepted_identity_links':len(accepted), 'unique_qp':len(set(accepted.values())),
               'contradictory_links_excluded':len(conflicts),
               'crosswalk_sha256':cw, 'source':'official_selected_v11_only'}
    return accepted, summary


def _new_index() -> dict:
    return {'schema':SCHEMA, 'provider':PROVIDER, 'endpoint':API_ENDPOINT,
            'license':LICENSE, 'languages':list(TARGET_LOCALES),
            'candidate_only':True, 'no_translation':True, 'activations':0,
            'entries':{}, 'last_updated_utc':None}


def _load_index(directory: Path) -> dict:
    path=directory/'index.json'
    if not path.exists():
        return _new_index()
    _check_path(path, directory)
    raw=path.read_bytes()
    if len(raw)>16*1024*1024:
        raise ValueError('Index de cache anormalement grand')
    data=json.loads(raw)
    if (not isinstance(data,dict) or data.get('schema')!=SCHEMA or
        data.get('provider')!=PROVIDER or data.get('endpoint')!=API_ENDPOINT or
        data.get('languages')!=list(TARGET_LOCALES) or
        not isinstance(data.get('entries'),dict) or
        data.get('candidate_only') is not True or data.get('activations')!=0):
        raise ValueError('Index en ligne inconnu ou modifié')
    return data


def _save_atomic(path: Path, data: bytes):
    _check_path(path, path.parent.parent if path.parent.name=='blobs' else path.parent)
    temp=path.with_name(path.name+'.stage-'+uuid.uuid4().hex)
    try:
        with temp.open('xb') as fd:
            fd.write(data)
            fd.flush()
            os.fsync(fd.fileno())
        os.replace(temp,path)
    finally:
        temp.unlink(missing_ok=True)


def _record_for(qp: str, body: bytes, when: str) -> dict:
    """Validate an exact API response; redirects/other IDs are NEVER relabelled."""
    if len(body)>MAX_RESPONSE_BYTES:
        raise ValueError('Réponse Wikidata trop volumineuse')
    data=json.loads(body)
    if not isinstance(data,dict) or data.get('success') not in (1, '1'):
        raise ValueError('Réponse API Wikidata invalide ou incomplète')
    entities=data.get('entities')
    if not isinstance(entities,dict):
        raise ValueError('Réponse sans entités Wikidata')
    redirected={x.get('from') for x in data.get('redirects',[]) if isinstance(x,dict)} if isinstance(data.get('redirects',[]),list) else set()
    item=entities.get(qp)
    status='ok'
    labels={}
    if qp in redirected or not isinstance(item,dict) or item.get('id') != qp:
        status='needs_review_redirect_or_absent'
    elif 'missing' in item:
        status='not_found'
    else:
        values=item.get('labels')
        if not isinstance(values,dict):
            values={}
        for lang in TARGET_LOCALES:
            obj=values.get(lang)
            if isinstance(obj,dict) and obj.get('language')==lang:
                value=obj.get('value')
                if (isinstance(value,str) and 0<len(value.strip())<=500
                        and not any(x in value for x in '\r\n\x00')
                        and not value.lstrip().startswith(('=', '+', '-', '@'))):
                    labels[lang]=value.strip()
    return {'id':qp, 'status':status, 'labels':labels, 'retrieved_utc':when,
            'source_url':f'https://www.wikidata.org/wiki/{qp}',
            'response_sha256':sha256(body), 'license':LICENSE,
            'candidate_only':True, 'activations':0}


def _get_url(url: str, ua: str) -> bytes:
    # Do not accept redirects to third-party hosts or other endpoints.
    class BlockRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            raise ValueError('Redirection HTTP refusée pour Wikidata')
    request=urllib.request.Request(url,headers={'User-Agent':ua,'Accept':'application/json'})
    opener=urllib.request.build_opener(BlockRedirect())
    with opener.open(request,timeout=25) as response:
        if response.status!=200:
            raise ValueError(f'HTTP {response.status}')
        body=response.read(MAX_RESPONSE_BYTES+1)
    if len(body)>MAX_RESPONSE_BYTES:
        raise ValueError('Réponse Wikidata trop volumineuse')
    return body


def _fetch_batch(ids: list[str], ua: str, transport: Callable | None = None) -> bytes:
    params=urllib.parse.urlencode({
        'action':'wbgetentities','ids':'|'.join(ids), 'props':'labels',
        'languages':'|'.join(TARGET_LOCALES), # fallback absent by design
        'format':'json', 'formatversion':'2', 'maxlag':'5',
    })
    url=API_ENDPOINT+'?'+params
    if transport is not None:
        body=transport(url,tuple(ids))
        if not isinstance(body,bytes):
            raise ValueError('Transport de test : octets attendus')
        return body
    for attempt in range(3):
        try:
            return _get_url(url,ua)
        except urllib.error.HTTPError as exc:
            if exc.code not in (429,500,502,503,504) or attempt==2:
                raise ValueError(f'Echec Wikidata HTTP {exc.code}') from exc
            retry=exc.headers.get('Retry-After','') if exc.headers else ''
            wait=min(30, max(2**attempt, int(retry) if str(retry).isdigit() else 0))
            time.sleep(wait)
        except (urllib.error.URLError, TimeoutError) as exc:
            if attempt==2:
                raise ValueError(f'Connexion Wikidata indisponible: {exc}') from exc
            time.sleep(2**attempt)
    raise AssertionError('Inaccessible')


def _blob(directory: Path, digest: str) -> bytes:
    if not isinstance(digest,str) or not SHA.fullmatch(digest):
        raise ValueError('Hash du blob invalide')
    path=directory/'blobs'/(digest+'.json')
    _check_path(path,directory)
    body=path.read_bytes()
    if len(body)>MAX_RESPONSE_BYTES or sha256(body)!=digest:
        raise ValueError(f'Blob de réponse modifié: {digest}')
    return body


def _valid_record(directory:Path, qp: str, entry:dict) -> dict:
    if not isinstance(entry,dict) or not QPID.fullmatch(qp):
        raise ValueError('Entrée de cache invalide')
    body=_blob(directory, entry.get('response_sha256'))
    record=_record_for(qp,body,entry.get('retrieved_utc',''))
    if json_bytes(record)!=json_bytes(entry):
        raise ValueError(f'Index en ligne altéré: {qp}')
    return record


def fetch_accepted(*, official_root: str | Path, dik_root: str | Path,
                   allow_network: bool = False, max_ids: int = 2500, batch_size: int = 25,
                   min_kristals: int = 126, refresh: bool = False,
                   user_agent: str = DEFAULT_USER_AGENT,
                   transport: Callable | None = None, delay:float = 1.0,
                   targets_override: tuple[dict,dict] | None = None) -> dict:
    """Populate content-addressed read-only cache for accepted Wikidata IDs.

    Explicit --allow-network is required. A partial run is resumable; every
    successful batch is checkpointed. Network failure leaves prior batches.
    """
    if not allow_network:
        raise ValueError('Accès réseau non autorisé : fournir --allow-network explicitement')
    if not isinstance(max_ids,int) or not 1<=max_ids<=100000:
        raise ValueError('max_ids hors limites')
    if not isinstance(batch_size,int) or not 1<=batch_size<=50:
        raise ValueError('batch_size doit être de 1 à 50')
    if not isinstance(user_agent,str) or not (12<=len(user_agent)<=256) or '\r' in user_agent or '\n' in user_agent:
        raise ValueError('User-Agent invalide')
    directory=_root(dik_root)
    _check_path(directory/'blobs',directory)
    (directory/'blobs').mkdir(exist_ok=True)
    accepted, summary=targets_override if targets_override is not None else accepted_official_qp(official_root,min_kristals=min_kristals)
    ids=sorted({q for q in accepted.values() if isinstance(q,str) and QPID.fullmatch(q)},
               key=lambda x:(x[0],int(x[1:])))
    index=_load_index(directory)
    # Fail closed when any existing entry was corrupted before making requests.
    for qp, entry in index['entries'].items():
        _valid_record(directory,qp,entry)
    todo=[qp for qp in ids if refresh or qp not in index['entries']]
    selected=todo[:max_ids]
    batches=0
    fetched=0
    labels=0
    failures=[]
    for start in range(0,len(selected),batch_size):
        subset=selected[start:start+batch_size]
        if batches and delay and transport is None:
            time.sleep(max(0,delay))
        try:
            body=_fetch_batch(subset,user_agent,transport)
            stamp=utc_now()
            records={qp:_record_for(qp,body,stamp) for qp in subset}
            checksum=sha256(body)
            blobpath=directory/'blobs'/(checksum+'.json')
            _check_path(blobpath,directory)
            if blobpath.exists():
                if _blob(directory,checksum)!=body:
                    raise ValueError('Empreinte de blob existant incohérente')
            else:
                _save_atomic(blobpath,body)
            index['entries'].update(records)
            index['last_updated_utc']=stamp
            _save_atomic(directory/'index.json',json_bytes(index))
            batches+=1
            fetched+=len(subset)
            labels+=sum(len(x['labels']) for x in records.values())
        except (ValueError,urllib.error.URLError,TimeoutError,OSError,TypeError) as exc:
            failures.append({'batch':batches+1,'count':len(subset),'type':type(exc).__name__,
                             'reason':str(exc)[:240]})
            break
    cached=sum(qp in index['entries'] for qp in ids)
    report={'schema':'dik.online-wikidata-fetch-report/5.6.0',
            'provider':PROVIDER, 'endpoint':API_ENDPOINT,'license':LICENSE,
            'status':'PARTIAL_NETWORK_ERROR' if failures else ('PARTIAL_BUDGET' if cached<len(ids) else 'COMPLETE'),
            'candidate_only':True,'activations':0,'no_translation':True,
            'target_languages':list(TARGET_LOCALES),
            'official':summary, 'unique_accepted_qp_requested':len(ids),
            'unique_qp_cached':cached,'new_qp_fetched':fetched,'new_labels_observed':labels,
            'batches_completed':batches,'network_attempted':batches>0 or bool(failures),
            'failures':failures,'index':str(directory/'index.json'),
            'source_catalog':list(PROVIDERS), 'retrieved_utc':utc_now()}
    name='FETCH_'+dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'_'+uuid.uuid4().hex[:6]+'.json'
    _save_atomic(directory/name,json_bytes(report))
    return report


def observe_online(index_file: str|Path, *, wanted:set[str], locales:tuple[str,...]=TARGET_LOCALES) -> tuple[dict,dict]:
    """Read verified local evidence, no network, no count/publication mutation."""
    if tuple(locales)!=TARGET_LOCALES:
        raise ValueError('Les 14 codes officiels doivent être utilisés exactement')
    path=Path(index_file).expanduser().absolute()
    directory=path.parent
    if path.name!='index.json' or not path.is_file() or _unsafe(path):
        raise ValueError('Index en ligne absent ou invalide')
    _check_path(path,directory)
    doc=_load_index(directory)
    forms={}
    absent=[]
    for qp in sorted(wanted):
        entry=doc['entries'].get(qp)
        if entry is None:
            absent.append(qp)
            continue
        record=_valid_record(directory,qp,entry)
        if record['status'] != 'ok':
            continue
        for locale in locales:
            form=record['labels'].get(locale)
            if form:
                forms[qp,locale]={'form':form,'response_sha256':record['response_sha256'],
                                  'source_url':record['source_url'],'license':LICENSE,
                                  'retrieved_utc':record['retrieved_utc']}
    info={'status':'CACHE_VERIFIED' if not absent else 'CACHE_PARTIAL',
          'candidate_only':True,'activations':0,'no_translation':True,
          'wikidata_qp_requested':len(wanted),
          'wikidata_qp_cached':len(wanted)-len(absent),
          'wikidata_qp_not_cached':len(absent),
          'explicit_labels_candidate':len(forms), 'provider':PROVIDER,
          'license':LICENSE, 'index_sha256':d.sha256(path)}
    return forms,info
