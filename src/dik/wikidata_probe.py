"""Bounded official Wikidata Action API redirect probe for accepted Q/P mappings.

Manual, explicit network operation, never part of a read/resolve. Store raw
API envelopes separately, without modifying crosswalks or Kristal graphs.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import tempfile
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, HTTPRedirectHandler, build_opener

from .operations import DiKError
from .wikidata_evolution import _read_crosswalk
from .redirect_sources import _extract_envelope, _id_from_title

API = 'https://www.wikidata.org/w/api.php'
_MAX_RESPONSE = 4 * 1024 * 1024


def _safe_api_url(url: str) -> None:
    parts = urlsplit(url)
    if (parts.scheme != 'https' or parts.hostname != 'www.wikidata.org' or parts.port not in (None,443)
        or parts.username or parts.password or parts.path != '/w/api.php' or parts.fragment):
        raise DiKError('UNSAFE_REDIRECT: official Wikidata Action API required')


class _SafeApiRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        _safe_api_url(newurl)
        return super().redirect_request(req,fp,code,msg,headers,newurl)


def probe_crosswalk_redirects(*, crosswalk: Path, registry: Path, namespace: str,
                              output: Path, user_agent: str, max_ids: int = 500,
                              batch_size: int = 25, timeout: int = 30,
                              delay_seconds: float = 1.0, opener=None,
                              sleep=None) -> dict:
    """Archive live redirects query replies as JSONL with explicit limits.

    Do not infer that absent redirect != deleted; only query.redirects is used.
    An external network query cannot certify historical identity equivalence.
    """
    if not isinstance(user_agent, str) or len(user_agent.strip()) < 12 or len(user_agent) > 256:
        raise DiKError('USER_AGENT_REQUIRED: identify application and contact for the API operator')
    if not (1 <= max_ids <= 5000 and 1 <= batch_size <= 50 and 1 <= timeout <= 180):
        raise DiKError('INVALID_RESOURCE_LIMIT')
    if not (0.5 <= delay_seconds <= 120):
        raise DiKError('INVALID_RATE_LIMIT: at least 0.5 seconds between batches')
    output=Path(output)
    if output.exists():
        raise DiKError('OUTPUT_EXISTS')
    active = _read_crosswalk(Path(crosswalk),Path(registry),namespace)
    ids = sorted({m['external_ref']['id'] for m in active})
    if len(ids) > max_ids:
        raise DiKError('RESOURCE_LIMIT: crosswalk IDs exceed explicit max; no silent truncation')
    if not ids:
        raise DiKError('EMPTY_APPROVED_CROSSWALK')
    output.parent.mkdir(parents=True, exist_ok=True)
    fd, name=tempfile.mkstemp(prefix='.dik-api-',suffix='.tmp',dir=str(output.parent))
    tmp=Path(name)
    digest=hashlib.sha256()
    processed=0
    redirects=0
    opener = opener or build_opener(_SafeApiRedirect())
    snooze = sleep or time.sleep
    try:
        with os.fdopen(fd,'wb') as stream:
            for index in range(0,len(ids),batch_size):
                if index:
                    snooze(delay_seconds)
                subset=ids[index:index+batch_size]
                expected=set(subset)
                titles=['Property:'+x if x.startswith('P') else x for x in subset]
                params=urlencode({'action':'query','redirects':'1','titles':'|'.join(titles),
                                  'format':'json','formatversion':'2','maxlag':'5'})
                url=API+'?'+params
                _safe_api_url(url)
                req=Request(url,headers={'Accept-Encoding':'identity', 'Accept':'application/json',
                                         'User-Agent':user_agent})
                try:
                    res=opener.open(req,timeout=timeout)
                except (HTTPError,URLError,TimeoutError,OSError) as exc:
                    raise DiKError(f'MEDIAWIKI_API_UNAVAILABLE: {exc}') from exc
                with res as response:
                    final_url=response.geturl() if hasattr(response,'geturl') else url
                    _safe_api_url(final_url)
                    status=getattr(response,'status',None) or response.getcode()
                    if status != 200:
                        raise DiKError('MEDIAWIKI_API_STATUS: expected HTTP 200')
                    data=response.read(_MAX_RESPONSE + 1)
                    if len(data)>_MAX_RESPONSE:
                        raise DiKError('RESOURCE_LIMIT: oversized API response')
                try:
                    obj=json.loads(data)
                except (UnicodeError,ValueError) as exc:
                    raise DiKError('INVALID_MEDIAWIKI_JSON') from exc
                # Validate API shape, duplicate redirects and scope on every batch.
                events=_extract_envelope(obj,'live-probe',f'wikidata-action-api:batch:{index//batch_size+1}',set(),batch_size)
                for event in events:
                    if event['source_id'] not in expected:
                        raise DiKError('UNEXPECTED_MEDIAWIKI_REDIRECT: returned source not requested')
                redirects += len(events)
                line=(json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n').encode('utf-8')
                stream.write(line);digest.update(line)
                processed += 1
            stream.flush();os.fsync(stream.fileno())
        try:
            os.link(tmp,output)
        except FileExistsError as exc:
            raise DiKError('OUTPUT_EXISTS') from exc
    finally:
        tmp.unlink(missing_ok=True)
    return {'profile':'dik.wikidata-api-probe/1.0-candidate',
            'source':'https://www.wikidata.org/w/api.php',
            'output':str(output),'responses_sha256':digest.hexdigest(),
            'approved_exact_external_ids_queried':len(ids),
            'api_batches':processed,'redirects_found':redirects,
            'canonical_mutation':False,'crosswalk_mutation':False,
            'warning':'Saved API data are observation evidence; no identity is changed. '
                      'A live API query does not certify older snapshots or prove missing IDs are retired. '
                      'Review every proposed correspondence.'}
