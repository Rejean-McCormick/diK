"""diK's local, task-oriented workbench.

UX reference: senior-interface-ux-patterns-v2, UX-01/05/06/07/08/09/11/12/14.
Canonical Kristal data never changes through this server. Optional local curation
creates an isolated immutable *candidate catalog* via the existing engine; it
never approves an identity, a crosswalk, or a new canonical graph.

No JavaScript, remote CDNs, cookies, or network dependency. Only loopback binding.
The optional POST endpoint requires a CSRF token and explicit opt-in. This is
NOT authenticated multi-user governance; local OS access is the trust boundary.
"""
from __future__ import annotations

import html
import json
import secrets
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlsplit

from . import __version__
from .operations import Project, inspect, coverage_report, dictionary_resolve, DiKError
from .index import reverse_lookup
from .compact import project_compact
from .curation import publish_preference
from .conciliation import conflicts, variants, conflict_detail
from ._framework import dictionaries as fw
from ._framework import coverage as fw_coverage

STYLE = '''
:root{color-scheme:light;--ink:#172f35;--sub:#576b70;--brand:#146763;--line:#dce6e5;--paper:#fff;--bg:#f5f8f7;--soft:#eaf3f2;--warn:#805126;--bad:#9b3342}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 system-ui,-apple-system,Segoe UI,Roboto,sans-serif}
a{color:var(--brand)}a:focus-visible,input:focus-visible,select:focus-visible,button:focus-visible,textarea:focus-visible{outline:3px solid #b88228;outline-offset:2px}
header{background:var(--paper);border-bottom:1px solid var(--line)}.head,.layout{max-width:1200px;margin:auto;padding:0 24px}
.head{display:flex;align-items:center;justify-content:space-between;gap:12px;padding-top:16px;padding-bottom:16px}.brand{font-size:1.6rem;font-weight:750;text-decoration:none;color:var(--ink)}
.brand span{color:var(--brand)}.hint{color:var(--sub);font-size:.87rem}.layout{display:grid;grid-template-columns:200px minmax(0,1fr);gap:24px;padding-top:24px;padding-bottom:36px}
nav{align-self:start;position:sticky;top:16px}nav a{display:block;text-decoration:none;padding:11px 12px;border-radius:9px;color:var(--ink);margin-bottom:4px}nav a[aria-current=page]{background:#d8eeeb;color:#105c58;font-weight:700}
main{min-width:0}.lede{color:var(--sub);margin-top:-4px}.eyebrow{letter-spacing:.05em;text-transform:uppercase;color:var(--sub);font-size:.75rem;font-weight:650}
h1{margin:0 0 8px;font-size:1.75rem;line-height:1.2}h2{font-size:1.16rem;margin:0 0 10px}h3{font-size:1rem;margin:0 0 8px}.panel{background:var(--paper);border:1px solid var(--line);border-radius:13px;padding:20px;margin:16px 0;box-shadow:0 1px 3px #1f3e3b0b}
.columns{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}.stat{background:var(--soft);padding:14px;border-radius:9px}.stat strong{font-size:1.5rem;display:block}
form{display:flex;gap:12px;align-items:end;flex-wrap:wrap}label{display:flex;flex-direction:column;gap:5px;min-width:100px;font-weight:600;flex:1}label .hint{font-weight:400}
input,select,textarea{width:100%;border:1px solid #afc0be;border-radius:7px;background:#fff;color:var(--ink);font:inherit;padding:9px 11px}textarea{min-height:92px}button,.button{cursor:pointer;display:inline-block;background:var(--brand);color:#fff;border:1px solid var(--brand);border-radius:8px;padding:10px 16px;font:inherit;font-weight:600;text-decoration:none}
.secondary{background:#fff;color:var(--brand)}.pill{display:inline-block;background:var(--soft);border-radius:99px;padding:2px 10px;font-size:.78rem;color:#165956;margin-right:5px}.muted{color:var(--sub)}.warn{color:var(--warn)}.bad{color:var(--bad)}.ok{color:#176958}.note{border-left:3px solid var(--brand);padding:10px 14px;background:var(--soft);margin:14px 0}.list{margin:0;padding-left:20px}.list li{margin:8px 0}.item{border-bottom:1px solid var(--line);padding:12px 0}.item:last-child{border:0}
table{border-collapse:collapse;width:100%;font-size:.94rem}th,td{text-align:left;padding:10px 7px;border-bottom:1px solid var(--line);vertical-align:top}th{color:var(--sub);font-size:.8rem}code{font-size:.86em;overflow-wrap:anywhere;color:#234a56;background:#eff4f3;padding:1px 4px;border-radius:3px}
.bar{height:8px;border-radius:12px;background:#e0e9e8;overflow:hidden;min-width:78px}.bar b{display:block;height:100%;background:var(--brand)}.actions{display:flex;gap:10px;flex-wrap:wrap;margin:12px 0}.crumb{font-size:.85rem;color:var(--sub);margin-bottom:14px}
fieldset{border:1px solid var(--line);border-radius:10px;padding:14px;margin:0}legend{font-weight:650}fieldset label{font-weight:400}.single-checkbox{display:flex;flex-direction:row;align-items:flex-start;gap:8px}.single-checkbox input{width:auto;flex:0;margin-top:5px}
.source-row{display:grid;grid-template-columns:minmax(120px,1fr) minmax(130px,1fr) minmax(80px,auto);gap:12px;align-items:start;padding:10px 0;border-bottom:1px solid var(--line)}.source-row:last-child{border:0}.source-row .hint{font-size:.8rem}.status-warning{border-left:3px solid #ba8433;padding:10px 14px;background:#fff8e9;margin:14px 0}footer{margin:24px auto;max-width:1200px;padding:14px 24px;border-top:1px solid var(--line);font-size:.85rem;color:var(--sub)}
@media(max-width:740px){.layout{display:block;padding:14px}nav{position:static;display:flex;flex-wrap:wrap;gap:5px;margin-bottom:16px}nav a{margin:0;padding:8px}.head{padding-left:14px;padding-right:14px}.panel{padding:15px}.columns{grid-template-columns:1fr}table{font-size:.85rem}}
'''


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def path_for(view='workspace', **query) -> str:
    params = {'view': view}
    params.update({k: v for k, v in query.items() if v is not None and v != ''})
    return '/?' + urlencode(params)


def _locale(catalog: dict, candidate: str) -> str:
    tags = [item['tag'] for item in catalog['languages']]
    if not tags:
        raise DiKError('No declared locales')
    if candidate in tags:
        return candidate
    if candidate == 'fr' and 'fr' not in tags:
        return tags[0]  # UI default when this project does not declare French
    raise DiKError('Undeclared locale: '+candidate)


def _selector(catalog: dict, selected: str) -> str:
    return '<select name="locale" aria-label="Langue">' + ''.join(
        f'<option value="{esc(lang["tag"])}"' + (' selected' if lang['tag'] == selected else '') + '>'
        + esc(lang['tag']) + '</option>' for lang in catalog['languages']
    ) + '</select>'


def _nav(active: str, locale: str) -> str:
    parts = [('workspace', 'Concepts et traductions'), ('coverage', 'Complétude'),
             ('projection', 'Lire un Kristal')]
    links = ''.join(f'<a href="{esc(path_for(view, locale=locale))}"'+
                    (' aria-current="page"' if active == view else '')+'>'+esc(label)+'</a>' for view,label in parts)
    return ('<nav aria-label="Navigation principale">'+ links + '<hr style="border:0;border-top:1px solid #dce6e5">' +
           f'<a href="{esc(path_for("diagnostics", locale=locale))}"' + (' aria-current="page"' if active=='diagnostics' else '') + '>Diagnostics et API</a></nav>')


def _search(project: Project, index: Path | None, *, locale: str, term: str, kind: str) -> str:
    # Never quietly present a unique lexical result as a verified identity.
    kind = kind if kind in ('KQ', 'KP') else 'KQ'
    form = ('<form method="get" action="/"><input type="hidden" name="view" value="workspace">'
        + '<label>Mot ou expression<input name="term" maxlength="256" value="'+esc(term)+'" placeholder="Ex. Saint Augustin"></label>'
        + '<label style="flex:0 0 135px">Type<select name="kind"><option value="KQ"'+(' selected' if kind=='KQ' else '')+'>Concept KQ</option><option value="KP"'+(' selected' if kind=='KP' else '')+'>Propriété KP</option></select></label>'
        + '<input type="hidden" name="locale" value="'+esc(locale)+'"><button>Rechercher</button></form>')
    if not term:
        return form + '<p class="hint">Recherche exacte dans les dictionnaires. Un résultat unique est un candidat, pas une identité approuvée.</p>'
    if index is None:
        return form + '<p class="note">Index absent. Construisez-le avec <code>dik index build</code> ou ouvrez directement un identifiant.</p>'
    try:
        result = reverse_lookup(project, index, term=term, locale=locale, kind=kind, limit=50)
    except (DiKError, ValueError) as err:
        return form + '<p class="bad">Recherche indisponible : '+esc(err)+'</p>'
    lines = '<p><strong>'+str(result['candidate_count'])+' candidat(s)</strong> — '+esc(result['state'])+'</p>'
    if result['truncated']:
        lines += '<p class="warn">Résultats tronqués. Affinez votre recherche.</p>'
    for entry in result['candidates']:
        kid = entry['semantic_id']
        href = path_for('workspace', locale=locale, id=kid)
        lines += ('<div class="item"><a href="'+esc(href)+'"><strong>'+esc(kid)+'</strong></a> '
                  '<span class="pill">Candidat non approuvé</span><div class="hint">'
                  + esc(', '.join(sorted({s['variant']+' · '+s['layer_id'] for s in entry['signals']})))
                  + '</div></div>')
    return form + lines


def _concept(project: Project, catalog: dict, locale: str, semantic_id: str, index: Path | None,
             *, writable: bool, csrf_token: str) -> str:
    reg = fw.read_json(project.registry)
    items = {item['id']: item for item in reg['identities']}
    if semantic_id not in items or items[semantic_id]['kind'] not in ('entity', 'property'):
        return '<div class="panel"><p class="bad">Identifiant KQ/KP inconnu.</p></div>'
    info = dictionary_resolve(project, semantic_id, locale)
    label = info.get('term')
    state = info.get('status','missing')
    kind = 'Concept' if items[semantic_id]['kind'] == 'entity' else 'Propriété'
    graph = fw.read_json(project.graph)
    total = sum(semantic_id in [s['subject'],s['predicate'], s['object'].get('id') if isinstance(s['object'],dict) else None] for s in graph['assertions'])
    mappings = [m for m in fw.read_json(project.crosswalk)['mappings'] if
                m['local_ref']['id']==semantic_id and m['local_ref']['namespace_id']==graph['namespace_id']]
    mapping_html = ''.join('<div class="item"><code>'+esc(m['external_ref']['system'])+':'+esc(m['external_ref']['id'])+
                 '</code> — '+esc(m['relation'])+' · <strong>'+esc(m['status'])+'</strong></div>' for m in mappings)
    body = ('<section class="panel"><p class="crumb"><a href="'+esc(path_for('workspace',locale=locale))+'">Concepts et traductions</a> / '+esc(semantic_id)+'</p>'
       + '<h2>'+esc(kind)+' <code>'+esc(semantic_id)+'</code></h2>'
       + '<p><strong>'+esc(label if label is not None else 'Traduction manquante')+'</strong> <span class="pill">'+esc(state)+'</span></p>'
       + '<p class="hint">'+str(total)+' assertion(s) du Kristal utilisent cet identifiant. L’identité KQ/KP ne change pas avec la langue.</p>'
       + '<h3>Wikidata / référentiels externes</h3>' + (mapping_html if mappings else '<p class="muted">Aucun alignement enregistré.</p>')+'</section>')
    if index is not None:
        try:
            observed = variants(project, index, semantic_id, locale)
            signals = observed['signals']
            if observed['competing_preferred']:
                body += ('<div class="status-warning"><strong>Plusieurs libellés préférés</strong> : '
                         'une priorité d’affichage ne constitue pas une décision d’équivalence. '
                         'Examinez les sources avant toute correction.</div>')
            rows = ''.join('<div class="source-row"><div><strong>'+esc(x['term'])+'</strong><div class="hint">'+esc(x['variant'])+'</div></div>'
              +'<div>'+esc(x['source_kind'])+' · '+esc(x['layer_id'])+'<div class="hint">'
              +esc(x['provenance'].get('source') or 'révision locale')+'</div></div>'
              +'<div>Priorité '+str(x['priority'])+'</div></div>' for x in signals)
            body += ('<section class="panel"><h3>Comparer les dictionnaires</h3>'
              '<p class="hint">'+str(len(signals))+' observation(s) vérifiables. '
              'Les alias ne sont pas des identités; la priorité détermine l’affichage seulement.</p>'
              +(rows if rows else '<p class="muted">Aucun libellé direct disponible.</p>')
              +'</section>')
        except DiKError as exc:
            body += '<div class="status-warning">Conciliation indisponible : '+esc(exc)+'</div>'
    if writable:
        body += ('<section class="panel"><h2>Créer une nouvelle révision lexicale</h2>'
             '<p class="note">Écrit un <strong>nouveau catalogue isolé</strong>. Ne change pas le Kristal actif, ne valide aucune équivalence Wikidata et ne constitue pas une signature d’approbation.</p>'
             '<form method="post" action="/curate"><input type="hidden" name="csrf" value="'+esc(csrf_token)+'">'
             '<input type="hidden" name="id" value="'+esc(semantic_id)+'">'
             '<input type="hidden" name="locale" value="'+esc(locale)+'">'
             '<label>Nouveau libellé<input name="term" maxlength="4096" required value="'+esc(label or '')+'"></label>'
             '<label>Réviseur déclaré <span class="hint">non authentifié</span><input name="reviewer" maxlength="128" required></label>'
             '<label style="flex-basis:100%">Justification<textarea name="reason" maxlength="2000" required></textarea></label>'
             '<label class="single-checkbox" style="flex-basis:100%"><input type="checkbox" name="confirm" value="yes" required>Je comprends que diK crée un catalogue candidat sans remplacer le canon ni authentifier le réviseur.</label>'
             '<button>Créer une révision distincte</button></form></section>')
    else:
        body += '<section class="panel"><h2>Correction lexicale</h2><p class="muted">Mode consultation. Pour créer une révision lexicale distincte, relancez l’interface avec <code>dik serve --workspace /chemin/privé</code>.</p></section>'
    return body


def _conflict_queue(project: Project, index: Path | None, locale: str, page: int=1) -> str:
    if index is None:
        return '<section class="panel"><h2>Termes concurrents</h2><p class="muted">Construisez l’index local pour détecter les désaccords entre dictionnaires.</p></section>'
    try:
        result = conflicts(project,index,locale=locale,page=page,page_size=10)
    except DiKError as exc:
        return '<section class="panel"><h2>Termes concurrents</h2><p class="warn">'+esc(exc)+'</p></section>'
    rows=[]
    for entry in result['items']:
        key=entry['key']
        if entry['type']=='competing_preferred':
            href=path_for('workspace',locale=locale,id=key)
            title=esc(key)+' — libellés préférés divergents'
        else:
            href=path_for('workspace',locale=locale,term=key,kind=entry['kind'])
            title=esc(key)+' — terme partagé entre plusieurs identifiants'
        rows.append('<div class="item"><a href="'+esc(href)+'">'+title+'</a> '
                    '<span class="pill">À examiner</span><div class="hint">'+str(entry['affected_count'])
                    +' formes / référents · '+esc(entry['kind'])+'</div></div>')
    maxpage=max(1,(result['total']+9)//10)
    pager='<div class="actions">'+(' <a href="'+esc(path_for('workspace',locale=locale,conflicts_page=page-1))+'">Précédent</a>' if page>1 else '')+' <span class="hint">'+str(page)+' / '+str(maxpage)+'</span> '+(' <a href="'+esc(path_for('workspace',locale=locale,conflicts_page=page+1))+'">Suivant</a>' if page<maxpage else '')+'</div>'
    return ('<section class="panel"><h2>Termes concurrents · '+esc(locale)+'</h2>'
      '<p class="hint">'+str(result['total'])+' cas à examiner, sans fusion ni changement automatique de KQ/KP.</p>'
      +(''.join(rows) if rows else '<p class="ok">Aucun désaccord lexical détecté dans cette langue.</p>')+pager+'</section>')


def _workspace(project: Project, index: Path | None, catalog: dict, locale: str, term: str, kind: str,
               semantic_id: str, writable: bool, csrf_token: str, conflicts_page: int=1) -> str:
    # The workbench home validates the semantic references, not every one of
    # potentially millions of imported lexical records. Deep audit stays in
    # Diagnostics / CLI and every curation or projection uses validated inputs.
    refs=fw_coverage._references(fw.read_json(project.graph),fw.read_json(project.registry))
    head = '<h1>Concepts et traductions</h1><p class="lede">Retrouvez un référent, vérifiez son sens et préparez une correction sans toucher au canon.</p>'
    head += ('<div class="columns"><div class="stat"><strong>'+str(len(refs['KQ']))+'</strong>référents KQ utilisés</div>'
             '<div class="stat"><strong>'+str(len(refs['KP']))+'</strong>propriétés KP utilisées</div></div>')
    head += '<section class="panel"><h2>Retrouver un concept</h2>'+_search(project,index,locale=locale,term=term,kind=kind)+'</section>'
    head += '<section class="panel"><h2>Accéder directement à un identifiant</h2><form method="get" action="/"><input type="hidden" name="view" value="workspace"><input type="hidden" name="locale" value="'+esc(locale)+'"><label>Identifiant KQ/KP<input name="id" placeholder="KQ1001" required pattern="K[QP][0-9]+"></label><button>Ouvrir</button></form></section>'
    return head + (_concept(project,catalog,locale,semantic_id,index,writable=writable,csrf_token=csrf_token) if semantic_id else _conflict_queue(project,index,locale,conflicts_page))


def _coverage(project: Project, catalog: dict, locale: str, page: int) -> str:
    langs = [x['tag'] for x in catalog['languages']]
    pages = max(1, (len(langs)+24)//25)
    page = min(max(page,1),pages)
    visible = langs[(page-1)*25:page*25]
    report=coverage_report(project,locales=visible,sample_limit=8)
    rows=[]
    for row in report['locales']:
        total=sum(row[k]['total'] for k in ('KQ','KP'))
        direct=sum(row[k]['direct'] for k in ('KQ','KP'))
        fallback=sum(row[k]['fallback'] for k in ('KQ','KP'))
        missing=sum(row[k]['missing'] for k in ('KQ','KP'))
        pct=100 if not total else round(direct*100/total)
        href=path_for('coverage',locale=row['tag'],page=page)
        rows.append(f'<tr><td><a href="{esc(href)}">{esc(row["tag"])}</a></td><td>{direct}/{total}</td><td><div class="bar" aria-label="{pct} % direct"><b style="width:{pct}%"></b></div></td><td>{fallback}</td><td>{missing}</td></tr>')
    chosen=coverage_report(project,locales=[locale],sample_limit=25)['locales'][0]
    missing_ids=sorted({id for k in ('KQ','KP') for id in chosen[k]['missing_ids_sample']})
    missing_note='<ul class="list">'+''.join('<li><a href="'+esc(path_for('workspace',locale=locale,id=i))+'"><code>'+esc(i)+'</code></a></li>' for i in missing_ids)+'</ul>' if missing_ids else '<p class="ok">Aucun identifiant manquant dans cette langue.</p>'
    pager='<div class="actions">'+(' <a class="button secondary" href="'+esc(path_for('coverage',locale=locale,page=page-1))+'">Précédent</a>' if page>1 else '')+'<span class="hint">Page '+str(page)+' / '+str(pages)+'</span>'+(' <a class="button secondary" href="'+esc(path_for('coverage',locale=locale,page=page+1))+'">Suivant</a>' if page<pages else '')+'</div>'
    return ('<h1>Complétude linguistique</h1><p class="lede">Voyez quelles langues couvrent réellement les identifiants de ce Kristal. Les replis ne comptent pas comme traduction directe.</p>'
          +'<section class="panel"><h2>'+esc(locale)+' — identifiants à compléter</h2><p class="hint">Échantillon de 25 références manquantes au plus, sans traductions inventées.</p>' + missing_note+'</section>'
          +'<section class="panel"><h2>Langues ('+str(len(langs))+')</h2><table><thead><tr><th>Langue</th><th>Direct</th><th>Progrès</th><th>Repli</th><th>Manquant</th></tr></thead><tbody>'+''.join(rows)+'</tbody></table>'+pager+'</section>')


def _projection(project:Project,locale:str,style:str)->str:
    style=style if style in ('annotated','clean') else 'clean'
    graph_bytes=project.graph.stat().st_size
    if graph_bytes>25_000_000:
        return '<h1>Lire un Kristal</h1><section class="panel"><p class="warn">Ce graphe est trop volumineux pour la prévisualisation Web. Utilisez <code>dik projection export</code>.</p></section>'
    data=project_compact(project,locale)
    entries=data['lexicon']['entries'];graph=data['canonical_graph']
    def display(kid):
        info=entries.get(kid, {'label':None})
        value=info['label'] or kid
        if style=='clean':return '<strong>'+esc(value)+'</strong>'
        return '<strong>'+esc(value)+'</strong> <code>'+esc(kid)+'</code>'
    rows=[]
    for stmt in graph['assertions'][:30]:
        obj=stmt['object']
        target=display(obj['id']) if obj['kind']=='entity' else '<code>'+esc(json.dumps(obj,ensure_ascii=False))+'</code>'
        rows.append('<div class="item">'+display(stmt['subject'])+' → '+display(stmt['predicate'])+' → '+target+'</div>')
    counts=data['lexicon']['coverage_counts']
    selected='<div class="actions"><a class="button '+('secondary' if style=='annotated' else '')+'" href="'+esc(path_for('projection',locale=locale,style='clean'))+'">Lecture épurée</a><a class="button '+('secondary' if style=='clean' else '')+'" href="'+esc(path_for('projection',locale=locale,style='annotated'))+'">Lecture annotée</a></div>'
    return ('<h1>Lire un Kristal</h1><p class="lede">Une projection en langue naturelle. Les KQ/KP restent dans les données réversibles.</p>'
        +'<section class="panel"><h2>Vue '+esc(style)+' — '+esc(locale)+'</h2>'+selected
        +'<p class="hint">'+str(counts['direct'])+' traductions directes · '+str(counts['fallback'])+' par repli · '+str(counts['missing'])+' absentes</p>'
        +''.join(rows) + ('<p class="hint">Aperçu limité aux 30 premières assertions.</p>' if len(graph['assertions'])>30 else '')
        +'<div class="actions"><a class="button secondary" href="'+esc('/api/projection?'+urlencode({'locale':locale}))+'">Exporter le JSON réversible</a></div>'
        +'<p class="note">Le JSON contient le graphe canonique et une table lexicale dédupliquée. diK restaure le canon directement, jamais par reconnaissance de mots.</p></section>')


def _diagnostics(project:Project)->str:
    info=inspect(project)
    rows=''.join('<tr><th>'+esc(key)+'</th><td><code>'+esc(value)+'</code></td></tr>' for key,value in info.items() if key not in ('lexical_records_by_locale','catalog_locales'))
    return ('<h1>Diagnostics</h1><p class="lede">Détails techniques et API locale, séparés du travail courant.</p>'
        +'<section class="panel"><h2>Contrats et sources</h2><table>'+rows+'</table></section>'
        +'<section class="panel"><h2>API (lecture seule)</h2><ul class="list">'
        +'<li><a href="/api/inspect">Inspection du Kristal</a></li>'
        +'<li><a href="/api/coverage?locales=fr">Complétude JSON</a></li>'
        +'<li><a href="/api/health">État du serveur</a></li><li><a href="/api/conciliation?locale=fr">Conflits lexicaux</a></li></ul></section>')


def html_page(project:Project,index:Path|None,locale='fr',term='',kind='KQ',*,view='workspace',
              semantic_id='',page=1,style='clean',writable=False,csrf_token='',conflicts_page=1) -> str:
    """Keep old keyword/positional compatibility for alpha.1 consumers."""
    catalog=fw.read_json(project.catalog)
    locale=_locale(catalog,locale)
    active=view if view in ('workspace','coverage','projection','diagnostics') else 'workspace'
    if active=='workspace':body=_workspace(project,index,catalog,locale,term,kind,semantic_id,writable,csrf_token,conflicts_page)
    elif active=='coverage':body=_coverage(project,catalog,locale,page)
    elif active=='projection':body=_projection(project,locale,style)
    else:body=_diagnostics(project)
    context = {'id': semantic_id if active == 'workspace' else '',
               'term': term if active == 'workspace' else '',
               'kind': kind if active == 'workspace' else '',
               'style': style if active == 'projection' else '',
               'page': str(page) if active == 'coverage' else '',
               'conflicts_page': str(conflicts_page) if active == 'workspace' and not semantic_id else ''}
    hidden = ''.join('<input type="hidden" name="'+esc(key)+'" value="'+esc(value)+'">'
                     for key,value in context.items() if value)
    selector=('<form method="get" action="/"><input type="hidden" name="view" value="'+esc(active)+'">'
              +hidden+'<label class="hint" style="max-width:135px">Langue '+_selector(catalog,locale)+'</label><button class="secondary">Changer</button></form>')
    return ('<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
      +'<title>diK — Atelier de dictionnaires</title><style>'+STYLE+'</style></head><body>'
      +'<header><div class="head"><a class="brand" href="/">di<span>K</span></a><div><span class="hint">Kristal v11 · '+esc(__version__)+' · Local</span>'+selector+'</div></div></header>'
      +'<div class="layout">'+_nav(active,locale)+'<main id="content">'+body+'</main></div>'
      +'<footer>Source de vérité : graphe KQ/KP · Wikidata : correspondances externes · Révisions non destructives · Interface locale</footer>'
      +'</body></html>')


def handler_factory(project:Project,index:Path|None,*,workspace:Path|None=None):
    # Unique token per server instance, not exposed through cookies or links.
    csrf_token=secrets.token_urlsafe(32)
    workspace=Path(workspace).resolve() if workspace is not None else None
    class Handler(BaseHTTPRequestHandler):
        def _respond(self,status:int,body:bytes,content_type:str):
            self.send_response(status)
            self.send_header('Content-Type',content_type+'; charset=utf-8')
            self.send_header('Content-Length',str(len(body)))
            self.send_header('Cache-Control','no-store')
            self.send_header('X-Content-Type-Options','nosniff')
            self.send_header('X-Frame-Options','DENY')
            self.send_header('Referrer-Policy','no-referrer')
            self.send_header('Content-Security-Policy',"default-src 'none'; style-src 'unsafe-inline'; form-action 'self'; base-uri 'none'; frame-ancestors 'none'")
            self.end_headers()
            self.wfile.write(body)
        def _check_host(self) -> bool:
            # Protect local UI against DNS rebinding, including localhost aliases.
            host=self.headers.get('Host','')
            return host in ('127.0.0.1:'+str(self.server.server_port), 'localhost:'+str(self.server.server_port))
        def _error(self,status,code):
            self._respond(status,json.dumps({'error':code},ensure_ascii=False).encode('utf-8'),'application/json')
        def do_GET(self):
            try:
                if not self._check_host():return self._error(403,'INVALID_HOST')
                if len(self.path)>2048:raise DiKError('Request too long')
                url=urlsplit(self.path)
                q=parse_qs(url.query,keep_blank_values=True)
                def val(n,default=''):return q.get(n,[default])[0][:256]
                if url.path=='/':
                    try: page=int(val('page','1'))
                    except ValueError:raise DiKError('Invalid page')
                    page=max(1,min(100_000,page))
                    body=html_page(project,index,locale=val('locale','fr'),term=val('term'),kind=val('kind','KQ'),view=val('view','workspace'),
                                   semantic_id=val('id'),page=page,style=val('style','clean'),writable=workspace is not None,csrf_token=csrf_token,
                                   conflicts_page=max(1,min(100000,int(val('conflicts_page','1')))))
                    self._respond(200,body.encode('utf-8'),'text/html');return
                if url.path=='/api/inspect':data=inspect(project)
                elif url.path=='/api/coverage':
                    locales=val('locales','fr').split(',')
                    if len(locales)>301:raise DiKError('Too many locales in interactive view')
                    data=coverage_report(project,locales=locales)
                elif url.path=='/api/resolve':data=dictionary_resolve(project,val('id'),val('locale','fr'))
                elif url.path=='/api/conciliation':
                    if index is None:raise DiKError('Index unavailable')
                    data=conflicts(project,index,locale=val('locale','fr'),kind=val('kind','all'),
                                   conflict_type=val('type','all'),page=int(val('page','1')))
                elif url.path=='/api/variants':
                    if index is None:raise DiKError('Index unavailable')
                    data=variants(project,index,val('id'),val('locale','fr'))
                elif url.path=='/api/conciliation/detail':
                    if index is None:raise DiKError('Index unavailable')
                    data=conflict_detail(project,index,locale=val('locale','fr'),kind=val('kind'),
                                         conflict_type=val('type'),key=val('key'))
                elif url.path=='/api/lookup':
                    if index is None:raise DiKError('Index unavailable')
                    data=reverse_lookup(project,index,term=val('term'),locale=val('locale','fr'),kind=val('kind','KQ'))
                elif url.path=='/api/projection':
                    if project.graph.stat().st_size>25_000_000:raise DiKError('Projection too large for Web; use CLI')
                    data=project_compact(project,_locale(fw.read_json(project.catalog),val('locale','fr')))
                    payload=json.dumps(data,ensure_ascii=False,sort_keys=True).encode('utf-8')
                    if len(payload)>40_000_000:raise DiKError('Projection too large for Web; use CLI')
                    self.send_response(200)
                    self.send_header('Content-Type','application/json; charset=utf-8')
                    self.send_header('Content-Disposition','attachment; filename="dik-projection.json"')
                    self.send_header('Content-Length',str(len(payload)))
                    self.send_header('Cache-Control','no-store')
                    self.send_header('X-Content-Type-Options','nosniff')
                    self.end_headers();self.wfile.write(payload);return
                elif url.path=='/api/health':data={'ok':True,'mode':'local-curation' if workspace else 'read-only','contract':'11.0.0-draft.3'}
                else:return self._error(404,'NOT_FOUND')
                self._respond(200,json.dumps(data,ensure_ascii=False).encode('utf-8'),'application/json')
            except (DiKError,ValueError,KeyError,fw.DictionaryError) as err:
                self._error(422,str(err))
        def do_POST(self):
            if not self._check_host():return self._error(403,'INVALID_HOST')
            if workspace is None or urlsplit(self.path).path!='/curate':return self._error(405,'METHOD_NOT_ALLOWED')
            if self.headers.get('Content-Type','').split(';')[0].strip().lower()!='application/x-www-form-urlencoded':
                return self._error(415,'UNSUPPORTED_MEDIA_TYPE')
            # CSRF defence: token + strict origin when supplied, bounded payload.
            origin=self.headers.get('Origin')
            if origin is not None and origin not in ('http://127.0.0.1:'+str(self.server.server_port),'http://localhost:'+str(self.server.server_port)):
                return self._error(403,'INVALID_ORIGIN')
            try:
                length=int(self.headers.get('Content-Length','-1'))
                if length<1 or length>10_000:return self._error(413,'FORM_TOO_LARGE')
                form=parse_qs(self.rfile.read(length).decode('utf-8'),keep_blank_values=True,strict_parsing=True)
                if any(len(values)!=1 for values in form.values()):raise DiKError('Duplicate form field')
                def field(k):return form.get(k,[''])[0].strip()
                if not secrets.compare_digest(field('csrf'),csrf_token):return self._error(403,'INVALID_CSRF')
                if field('confirm')!='yes':raise DiKError('Explicit confirmation required')
                if any(len(field(k))>max_len for k,max_len in [('id',64),('locale',40),('term',4096),('reviewer',128),('reason',2000)]):
                    raise DiKError('Form field too long')
                decision='local-'+secrets.token_hex(12)
                destination=workspace/'curations'/decision
                result=publish_preference(project,semantic_id=field('id'),locale=field('locale'),
                    term=field('term'),reviewer=field('reviewer'),reason=field('reason'),
                    decision_id=decision,destination=destination)
                receipt=('<h1>Révision lexicale créée</h1><div class="note">Le catalogue initial, le crosswalk et le graphe canonique sont inchangés. '
                         'Le nouveau catalogue n’est pas adopté automatiquement.</div>'
                         '<p>Nouvelle révision : <code>'+esc(decision)+'</code></p>'
                         '<p>Catalogue candidat : <code>'+esc(result['catalog'])+'</code></p>'
                         '<p>Empreinte SHA-256 : <code>'+esc(result['catalog_sha256'])+'</code></p>'
                         '<p><a class="button" href="'+esc(path_for('workspace',locale=field('locale'),id=field('id')))+'">Retour au concept</a></p>')
                body=('<!doctype html><html lang="fr"><head><meta charset="utf-8"><title>diK — Révision</title><style>'+STYLE+'</style></head>'
                      '<body><div class="layout"><main><section class="panel">'+receipt+'</section></main></div></body></html>')
                self._respond(201,body.encode('utf-8'),'text/html')
            except (DiKError,ValueError,KeyError,fw.DictionaryError,UnicodeError) as err:
                self._error(422,str(err))
        def log_message(self,fmt,*args):pass
    return Handler


def serve(project:Project,index:Path|None=None,port:int=8765,*,workspace:Path|None=None):
    if not 0<=port<=65535:raise DiKError('Invalid HTTP port')
    if workspace is not None:
        workspace=Path(workspace).resolve()
        if workspace.exists() and (not workspace.is_dir() or workspace.is_symlink()):
            raise DiKError('Workspace must be a normal directory')
        if workspace==project.manifest.parent or workspace.is_relative_to(project.manifest.parent):
            raise DiKError('Workspace must be outside the canonical project root')
        workspace.mkdir(parents=True,exist_ok=True)
    server=ThreadingHTTPServer(('127.0.0.1',port),handler_factory(project,index,workspace=workspace))
    try:
        print('diK local workbench: http://127.0.0.1:'+str(server.server_port),flush=True)
        server.serve_forever()
    finally:server.server_close()
