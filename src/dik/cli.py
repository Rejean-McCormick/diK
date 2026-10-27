"""Entry point of the local/offline diK 0.1 CLI."""
from __future__ import annotations

import argparse
import csv
import io
import json
import sys
from pathlib import Path

from . import __version__
from .operations import (DiKError, coverage_report, dictionaries_audit,
                         dictionary_resolve, import_wikidata_local, inspect,
                         load_project, serialize_json, write_new)
from ._framework.dictionaries import DictionaryError
from .projection import (project_graph, restore_projection, readable_markdown)
from .compact import project_compact
from .index import build as build_index, reverse_lookup
from .governance import append_review, journal_records
from .portfolio import portfolio_report
from .legacy import conversion_candidates, validate_plan_source
from .patches import inspect_patch
from .curation import publish_preference
from .sync import import_idempotent
from .mirror import fetch_dump
from .snapshot_diff import compare_snapshots
from .mirror_import import import_verified_mirror
from .large_import import import_large
from .wikidata_evolution import analyze_evolution
from .redirect_sources import extract_api_redirects
from .wikidata_probe import probe_crosswalk_redirects
from .webapp import serve
from .reconcile import publish_crosswalk
from .conciliation import conflicts,variants,conflict_detail


def make_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog='dik', description='diK — gestion locale des dictionnaires Kristal')
    p.add_argument('--version', action='version', version=f'diK {__version__}')
    sub = p.add_subparsers(dest='area', required=True)

    project = sub.add_parser('project', help='Inspecter un projet Kristal v11')
    ps = project.add_subparsers(dest='command', required=True)
    inspect_p = ps.add_parser('inspect', help='Vérifier graphe, registre, catalogues, crosswalk')
    inspect_p.add_argument('--project', required=True, help='Chemin vers dik.project.json')
    inspect_p.add_argument('--output', help='Créer un nouveau rapport JSON')

    dictionaries = sub.add_parser('dictionaries', help='Auditer ou consulter les dictionnaires')
    ds = dictionaries.add_subparsers(dest='command', required=True)
    audit = ds.add_parser('audit', help='Vérifier SHA-256, schémas, fallbacks et conflits')
    audit.add_argument('--project', required=True)
    audit.add_argument('--output')
    resolve = ds.add_parser('resolve', help='Obtenir un libellé sans modifier le graphe')
    resolve.add_argument('--project', required=True)
    resolve.add_argument('--id', required=True)
    resolve.add_argument('--locale', required=True)
    compare=ds.add_parser('compare',help='Comparer les sources d’un KQ/KP sans les fusionner')
    compare.add_argument('--project',required=True); compare.add_argument('--index',required=True)
    compare.add_argument('--id',required=True);compare.add_argument('--locale',required=True)
    con=ds.add_parser('conflicts',help='Liste paginée des contradictions et homonymes')
    con.add_argument('--project',required=True);con.add_argument('--index',required=True)
    con.add_argument('--locale',required=True);con.add_argument('--kind',choices=['KQ','KP','all'],default='all')
    con.add_argument('--type',choices=['competing_preferred','shared_term','all'],default='all')
    con.add_argument('--page',type=int,default=1);con.add_argument('--page-size',type=int,default=25)
    con.add_argument('--output')
    detail=ds.add_parser('conflict-detail',help='Observations vérifiables pour un conflit')
    detail.add_argument('--project',required=True);detail.add_argument('--index',required=True)
    detail.add_argument('--locale',required=True);detail.add_argument('--kind',required=True,choices=['KQ','KP'])
    detail.add_argument('--type',required=True,choices=['competing_preferred','shared_term'])
    detail.add_argument('--key',required=True)

    coverage = sub.add_parser('coverage', help='Rapport de complétude d’un Kristal')
    cs = coverage.add_subparsers(dest='command', required=True)
    report = cs.add_parser('report', help='KQ/KP couverts pour chaque langue sélectionnée')
    report.add_argument('--project', required=True)
    report.add_argument('--locales', help='Séparées par virgule; défaut: toutes les langues du catalogue')
    report.add_argument('--missing-sample-limit', type=int, default=25)
    report.add_argument('--output', help='Créer un rapport JSON sans écraser un fichier')
    report.add_argument('--csv', help='Créer un CSV récapitulatif séparé')

    projection = sub.add_parser('projection', help='Projeter et restaurer un Kristal sémantique sans perte')
    pjs = projection.add_subparsers(dest='command', required=True)
    export = pjs.add_parser('export', help='Créer une projection lisible réversible (JSON)')
    export.add_argument('--project', required=True)
    export.add_argument('--locale', required=True)
    export.add_argument('--output', required=True, help='Nouveau JSON de projection réversible')
    export.add_argument('--markdown', help='Copie de lecture humaine optionnelle, NON réversible seule')
    export.add_argument('--format', choices=['compact','verbose'], default='compact',
                        help='compact (defaut) de-duplique les libelles; verbose preserve le format v0.2')
    export.add_argument('--style', choices=['annotated','clean'], default='annotated',
                        help='Lecture annotée avec KQ/KP ou épurée (IDs dans JSON seulement)')
    restore = pjs.add_parser('restore', help='Restaurer le graphe pur depuis les références embarquées')
    restore.add_argument('--input', required=True, help='Enveloppe diK JSON générée par export')
    restore.add_argument('--output', required=True, help='Nouveau fichier graphe JSON (pas de remplacement)')
    restore.add_argument('--project', help='Recommandé: vérification contre le projet d’origine et dictionnaires')
    verify = pjs.add_parser('verify', help='Vérifier la projection sans écrire de graphe')
    verify.add_argument('--input', required=True)
    verify.add_argument('--project', help='Recommandé: contrôle renforcé contre le projet source')

    wikidata = sub.add_parser('wikidata', help='Importer depuis une copie locale Wikidata')
    ws = wikidata.add_subparsers(dest='command', required=True)
    imp = ws.add_parser('import-local', help='Import streaming .json/.jsonl/.gz/.bz2 (identités approuvées seulement)')
    imp.add_argument('--dump', required=True)
    imp.add_argument('--crosswalk', required=True)
    imp.add_argument('--registry', required=True)
    imp.add_argument('--namespace', required=True)
    imp.add_argument('--snapshot', required=True)
    imp.add_argument('--locales', required=True)
    imp.add_argument('--output', required=True, help='Nouveau dossier snapshot, doit être inexistant')
    idx = sub.add_parser('index', help='Index SQLite dérivé et reconstructible')
    xi = idx.add_subparsers(dest='command', required=True)
    bi=xi.add_parser('build'); bi.add_argument('--project',required=True);bi.add_argument('--output',required=True)
    ri=xi.add_parser('lookup');ri.add_argument('--project',required=True);ri.add_argument('--index',required=True)
    ri.add_argument('--term',required=True);ri.add_argument('--locale',required=True)
    ri.add_argument('--kind',required=True,choices=['KQ','KP'])
    rv=sub.add_parser('review',help='Décisions append-only vérifiables, pas de promotion automatique')
    vs=rv.add_subparsers(dest='command',required=True)
    a=vs.add_parser('append');a.add_argument('--project',required=True);a.add_argument('--decision',required=True);a.add_argument('--journal',required=True)
    l=vs.add_parser('list');l.add_argument('--journal',required=True)
    port=sub.add_parser('portfolio',help='Rapports de complétude multi-Kristals')
    ports=port.add_subparsers(dest='command',required=True)
    pr=ports.add_parser('coverage');pr.add_argument('--projects',required=True,nargs='+');pr.add_argument('--locales',required=True);pr.add_argument('--output')
    legacy=sub.add_parser('legacy',help='Plans de migration non exécutables')
    ls=legacy.add_subparsers(dest='command',required=True)
    plan=ls.add_parser('plan');plan.add_argument('--project',required=True);plan.add_argument('--source',required=True)
    plan.add_argument('--index',required=True);plan.add_argument('--roles',required=True)
    plan.add_argument('--locale',required=True);plan.add_argument('--output',required=True)
    pv=ls.add_parser('verify');pv.add_argument('--source',required=True);pv.add_argument('--plan',required=True)
    patch=sub.add_parser('patch',help='Vérifier une intention sans modifier le graphe')
    pts=patch.add_subparsers(dest='command',required=True)
    pat=pts.add_parser('verify');pat.add_argument('--intent',required=True);pat.add_argument('--graph',required=True)
    cura=sub.add_parser('curate',help='Nouvelle couche lexicale approuvée et immuable')
    cus=cura.add_subparsers(dest='command',required=True)
    edit=cus.add_parser('publish');edit.add_argument('--project',required=True);edit.add_argument('--id',required=True)
    edit.add_argument('--locale',required=True);edit.add_argument('--term',required=True)
    edit.add_argument('--reviewer',required=True);edit.add_argument('--decision-id',required=True)
    edit.add_argument('--reason',required=True);edit.add_argument('--output',required=True)
    sync=sub.add_parser('sync',help='Import local idempotent depuis snapshot Wikidata')
    ss=sync.add_subparsers(dest='command',required=True)
    fetch = ss.add_parser('fetch', help='Télécharger un dump HTTPS officiel avec reprise byte-range vérifiée')
    fetch.add_argument('--url', required=True, help='URL HTTPS officielle dumps.wikimedia.org')
    fetch.add_argument('--root', required=True, help='Dossier de miroirs, publication isolée par snapshot')
    fetch.add_argument('--snapshot', required=True, help='Nom immuable de snapshot')
    fetch.add_argument('--sha256', help='Empreinte amont de confiance; sinon dump marqué NON vérifié')
    fetch.add_argument('--max-bytes', type=int, default=250 * 1024**3)
    fetch.add_argument('--timeout', type=int, default=60)
    verified = ss.add_parser('import-mirror', help='Importer un miroir téléchargé avec SHA-256 amont approuvé')
    verified.add_argument('--manifest', required=True)
    verified.add_argument('--sha256', required=True, help='Empreinte approuvée indépendamment du manifeste du miroir')
    verified.add_argument('--crosswalk', required=True)
    verified.add_argument('--registry', required=True)
    verified.add_argument('--namespace', required=True)
    verified.add_argument('--locales', required=True)
    verified.add_argument('--root', required=True)
    diff = ss.add_parser('diff', help='Comparer deux catalogues Wikidata immuables, sans adoption')
    diff.add_argument('--before', required=True)
    diff.add_argument('--after', required=True)
    diff.add_argument('--crosswalk', required=True)
    diff.add_argument('--registry', required=True)
    diff.add_argument('--sample-limit', type=int, default=25)
    diff.add_argument('--events', help='Écrire un JSONL de tous les changements, sans écraser')
    diff.add_argument('--revision-only', action='store_true', help='Inclure les révisions purement techniques')
    probe=ss.add_parser('probe-redirects', help='Interroger explicitement l’API officielle pour les Q/P déjà approuvés (quotas stricts)')
    probe.add_argument('--crosswalk',required=True)
    probe.add_argument('--registry',required=True)
    probe.add_argument('--namespace',required=True)
    probe.add_argument('--output',required=True,help='Archive JSONL des réponses API, aucune adoption')
    probe.add_argument('--user-agent',required=True,help='Agent identifiable avec contact utilisateur')
    probe.add_argument('--max-ids',type=int,default=500)
    probe.add_argument('--batch-size',type=int,default=25)
    probe.add_argument('--timeout',type=int,default=30)
    probe.add_argument('--delay-seconds',type=float,default=1.0)
    extractor=ss.add_parser('extract-redirects', help='Normaliser des réponses réelles MediaWiki Action API en événements revus (hors ligne)')
    extractor.add_argument('--source',required=True,help='JSON ou JSONL de réponses action=query&redirects=1')
    extractor.add_argument('--format',choices=['action-api-json','action-api-jsonl'],default='action-api-json')
    extractor.add_argument('--snapshot',required=True)
    extractor.add_argument('--output',required=True,help='Nouveau JSONL normalisé, sans écrasement')
    extractor.add_argument('--approved-sha256',help='SHA-256 source approuvé indépendamment')
    extractor.add_argument('--max-bytes',type=int,default=128 * 1024 * 1024)
    extractor.add_argument('--max-records',type=int,default=250000)
    evo=ss.add_parser('evolution',help='Impact des redirections/retraits/scissions Wikidata sur les mappings actifs (revue seule)')
    evo.add_argument('--observations', required=True, help='JSONL normalisé par diK, PAS un dump Wikidata brut')
    evo.add_argument('--crosswalk', required=True)
    evo.add_argument('--registry', required=True)
    evo.add_argument('--namespace', required=True)
    evo.add_argument('--snapshot', required=True)
    evo.add_argument('--approved-sha256', help='SHA-256 indépendant des observations normalisées; sinon non authentifiées')
    evo.add_argument('--max-records', type=int, default=250000)
    evo.add_argument('--sample-limit', type=int, default=25)
    evo.add_argument('--events', help='JSONL complet des impacts; jamais écrasé')
    evo.add_argument('--output', help='Rapport JSON synthétique; jamais écrasé')
    large=ss.add_parser('import-large', help='Importer un dump local avec checkpoint SQLite et reprise')
    for name in ('dump','crosswalk','registry','namespace','snapshot','locales','root'):
        large.add_argument('--'+name,required=True)
    large.add_argument('--approved-sha256',help='SHA-256 d’origine vérifié indépendamment (optionnel)')
    large.add_argument('--batch-lines',type=int,default=5000)
    large.add_argument('--max-line-bytes',type=int,default=128 * 1024 * 1024)
    si=ss.add_parser('import-local')
    for name in ('dump','crosswalk','registry','namespace','snapshot','locales','root'):
        si.add_argument('--'+name,required=True)
    reconcile = sub.add_parser('reconcile', help='Exporter un nouveau crosswalk depuis décisions revues')
    reconcile.add_argument('--project',required=True);reconcile.add_argument('--journal',required=True)
    reconcile.add_argument('--revision-id',required=True);reconcile.add_argument('--output',required=True)
    serve_p = sub.add_parser('serve', help='Atelier local : consultation et curation optionnelle')
    serve_p.add_argument('--project',required=True);serve_p.add_argument('--index')
    serve_p.add_argument('--port',type=int,default=8765)
    serve_p.add_argument('--workspace',help='Dossier distinct pour publier de nouveaux catalogues locaux; absent = consultation seulement')
    return p


def _csv_coverage(report: dict) -> str:
    out = io.StringIO(newline='')
    writer = csv.writer(out)
    writer.writerow(['namespace', 'graph_id', 'langue', 'famille', 'total',
                     'direct', 'fallback', 'missing', 'conflicted', 'complete_direct', 'complete_usable'])
    for lang in report['locales']:
        for fam in ('KQ', 'KP'):
            row = lang[fam]
            writer.writerow([report['namespace_id'], report['graph_id'], lang['tag'], fam, row['total'],
                             row['direct'], row['fallback'], row['missing'], row['conflicted'],
                             lang['complete_direct'], lang['complete_usable']])
    return out.getvalue()


def run(args: argparse.Namespace) -> dict:
    if args.area=='reconcile':
        return publish_crosswalk(load_project(args.project),Path(args.journal),Path(args.output),args.revision_id)
    if args.area == 'serve':
        serve(load_project(args.project),Path(args.index) if args.index else None,args.port,
              workspace=Path(args.workspace) if args.workspace else None)
        return {'server':'stopped'}
    if args.area == 'index':
        project=load_project(args.project)
        if args.command=='build': return build_index(project,Path(args.output))
        return reverse_lookup(project,Path(args.index),term=args.term,locale=args.locale,kind=args.kind)
    if args.area == 'review':
        if args.command=='list':
            records=journal_records(Path(args.journal))
            return {'events':records,'count':len(records)}
        return append_review(Path(args.journal),json.loads(Path(args.decision).read_text(encoding='utf-8')),load_project(args.project))
    if args.area=='portfolio':
        result=portfolio_report(args.projects,args.locales.split(','))
        if args.output:write_new(Path(args.output),serialize_json(result))
        return result
    if args.area=='legacy':
        if args.command=='verify':
            return validate_plan_source(json.loads(Path(args.plan).read_text(encoding='utf-8')),Path(args.source))
        roles=json.loads(Path(args.roles).read_text(encoding='utf-8'))
        result=conversion_candidates(load_project(args.project),Path(args.source),Path(args.index),roles,locale=args.locale)
        write_new(Path(args.output),serialize_json(result));return result
    if args.area=='patch':
        return inspect_patch(json.loads(Path(args.intent).read_text(encoding='utf-8')),Path(args.graph))
    if args.area=='curate':
        return publish_preference(load_project(args.project),semantic_id=args.id,locale=args.locale,
            term=args.term,reviewer=args.reviewer,decision_id=args.decision_id,
            reason=args.reason,destination=Path(args.output))
    if args.area=='sync' and args.command=='fetch':
        return fetch_dump(url=args.url, root=Path(args.root), snapshot=args.snapshot,
            expected_sha256=args.sha256, max_bytes=args.max_bytes, timeout=args.timeout)
    if args.area=='sync' and args.command=='import-large':
        return import_large(dump=Path(args.dump),crosswalk=Path(args.crosswalk),
            registry=Path(args.registry),namespace=args.namespace,snapshot=args.snapshot,
            locales=args.locales.split(','),root=Path(args.root),batch_lines=args.batch_lines,
            max_line_bytes=args.max_line_bytes, approved_sha256=args.approved_sha256)
    if args.area=='sync' and args.command=='import-mirror':
        return import_verified_mirror(manifest=Path(args.manifest),crosswalk=Path(args.crosswalk),
            registry=Path(args.registry),namespace=args.namespace,
            locales=args.locales.split(','),root=Path(args.root),approved_sha256=args.sha256)
    if args.area=='sync' and args.command=='probe-redirects':
        return probe_crosswalk_redirects(crosswalk=Path(args.crosswalk), registry=Path(args.registry),
            namespace=args.namespace, output=Path(args.output),user_agent=args.user_agent,
            max_ids=args.max_ids, batch_size=args.batch_size, timeout=args.timeout,
            delay_seconds=args.delay_seconds)
    if args.area=='sync' and args.command=='extract-redirects':
        return extract_api_redirects(source=Path(args.source), output=Path(args.output),
            snapshot=args.snapshot,input_format=args.format,approved_sha256=args.approved_sha256,
            max_bytes=args.max_bytes,max_records=args.max_records)
    if args.area=='sync' and args.command=='evolution':
        if args.output and Path(args.output).exists():
            raise DiKError('OUTPUT_EXISTS')
        if args.output and args.events and Path(args.output).resolve()==Path(args.events).resolve():
            raise DiKError('OUTPUT_PATH_COLLISION')
        result=analyze_evolution(observations=Path(args.observations),crosswalk=Path(args.crosswalk),
            registry=Path(args.registry),namespace=args.namespace,snapshot=args.snapshot,
            approved_sha256=args.approved_sha256,sample_limit=args.sample_limit,
            max_records=args.max_records,events_jsonl=Path(args.events) if args.events else None)
        if args.output:
            write_new(Path(args.output),serialize_json(result))
        return result
    if args.area=='sync' and args.command=='diff':
        return compare_snapshots(before=Path(args.before),after=Path(args.after),
            crosswalk=Path(args.crosswalk),registry=Path(args.registry),
            sample_limit=args.sample_limit,events_path=Path(args.events) if args.events else None,
            include_revision_only=args.revision_only)
    if args.area=='sync':
        return import_idempotent(dump=Path(args.dump),crosswalk=Path(args.crosswalk),registry=Path(args.registry),
           namespace=args.namespace,snapshot=args.snapshot,locales=args.locales.split(','),root=Path(args.root))
    if args.area == 'projection':
        if args.command == 'export':
            project = load_project(args.project)
            proj = (project_compact(project, args.locale) if args.format == 'compact'
                    else project_graph(project, args.locale))
            files = [(Path(args.output), serialize_json(proj))]
            if args.markdown:
                files.append((Path(args.markdown), readable_markdown(proj,args.style)))
            if len({path.resolve() for path, _ in files}) != len(files):
                raise DiKError('Les chemins de sortie doivent être distincts')
            for path, _ in files:
                if path.exists():
                    raise DiKError(f'Le fichier existe déjà: {path}')
            created = []
            try:
                for path, payload in files:
                    write_new(path, payload)
                    created.append(path)
            except Exception:
                for path in created:
                    path.unlink()
                raise
            return {'action':'projection-export', 'locale':args.locale,
                    'projection':str(args.output), 'markdown':args.markdown, 'style':args.style,
                    'format':args.format,
                    'coverage_counts':proj['lexicon' if args.format == 'compact' else 'readable']['coverage_counts'],
                    'canonical_graph_sha256':proj['digests']['canonical_graph']}
        envelope = json.loads(Path(args.input).read_text(encoding='utf-8'))
        project = load_project(args.project) if args.project else None
        graph = restore_projection(envelope,project)
        if args.command == 'restore':
            write_new(Path(args.output),serialize_json(graph))
        return {'action':'projection-'+args.command, 'graph_id':graph['graph_id'],
                'namespace_id':graph['namespace_id'], 'projection_verified':True,
                'verified_against_project':project is not None,
                'output':getattr(args,'output',None),
                'warning':None if project else 'Sans projet source, les empreintes détectent les accidents, mais ne sont pas une signature cryptographique.'}
    if args.area == 'wikidata':
        return import_wikidata_local(dump=Path(args.dump), crosswalk=Path(args.crosswalk),
                                    registry=Path(args.registry), namespace=args.namespace,
                                    snapshot=args.snapshot,
                                    locales=args.locales.split(','), output=Path(args.output))
    project = load_project(args.project)
    if args.area == 'project':
        return inspect(project)
    if args.area == 'dictionaries':
        if args.command=='compare':
            return variants(project,Path(args.index),args.id,args.locale)
        if args.command=='conflict-detail':
            return conflict_detail(project,Path(args.index),locale=args.locale,kind=args.kind,
                                   conflict_type=args.type,key=args.key)
        if args.command=='conflicts':
            result=conflicts(project,Path(args.index),locale=args.locale,kind=args.kind,
                conflict_type=args.type,page=args.page,page_size=args.page_size)
            if args.output:write_new(Path(args.output),serialize_json(result))
            return result
        if args.command == 'audit':
            return dictionaries_audit(project)
        return dictionary_resolve(project, args.id, args.locale)
    locales = args.locales.split(',') if args.locales else None
    report = coverage_report(project, locales=locales, sample_limit=args.missing_sample_limit)
    # All-or-nothing publication of multiple reports; never overwrite.
    files = []
    if args.output:
        files.append((Path(args.output), serialize_json(report)))
    if args.csv:
        files.append((Path(args.csv), _csv_coverage(report)))
    if len({p.resolve() for p, _ in files}) != len(files):
        raise DiKError('La sortie JSON et CSV doivent être deux chemins différents')
    for path, _ in files:
        if path.exists():
            raise DiKError(f'Rapport déjà existant: {path}')
    created = []
    try:
        for path, text in files:
            write_new(path, text)
            created.append(path)
    except Exception:
        for path in created:
            path.unlink()
        raise
    return report


def main(argv: list[str] | None = None) -> int:
    parser = make_parser()
    try:
        args = parser.parse_args(argv)
        result = run(args)
        if getattr(args, 'output', None) and args.area not in ('coverage','projection','index','legacy','portfolio','curate','sync') and not (args.area=='dictionaries' and args.command=='conflicts'):
            write_new(args.output, serialize_json(result))
        print(serialize_json(result), end='')
        return 0
    except (DiKError, DictionaryError, OSError, ValueError, KeyError, json.JSONDecodeError) as e:
        print(f'diK: {e}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
