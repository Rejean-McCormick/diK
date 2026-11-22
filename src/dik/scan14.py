"""Audit lexical ciblé 14 langues, natif diK et *en lecture seule*.

Les libellés sont résolus avec l'ordre de priorité et de repli Framework
(v11 draft.3), sur un index construit en un passage APRÈS audit canonique.
Un mot ou un libellé Konstellation n'est jamais promu en identifiant KQ/KP.
"""
from __future__ import annotations

import collections
import csv
import hashlib
import json
import os
import shutil
import tempfile
from pathlib import Path

from ._framework import coverage as framework_coverage
from ._framework import dictionaries as dictionaries
from .operations import load_project
from .scan14_inventory import Source, InventoryError, corpus_terms, ui_candidate_strings

TARGET_LOCALES = ('en','fr','es','de','nl','sv','da','no','nn','fi','et','af','it','pt')


class Scan14Error(ValueError):
    """Invalid/incomplete scan; no report is published."""


def _csv(path: Path, rows: list[dict], columns: list[str]) -> None:
    with path.open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction='ignore', delimiter=';')
        writer.writeheader()
        writer.writerows(rows)


def _json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def _check_handoff(data: dict, source: str) -> None:
    if not isinstance(data, dict) or tuple(data.get('target_locales', ())) != TARGET_LOCALES:
        raise Scan14Error(f'Liste des 14 langues incompatible avec {source}')


def _preindexed_layers(project, catalog: dict, registered: set[str],
                       locales: set[str] | None = None) -> tuple[dict, list[dict]]:
    """Batched equivalent of Framework dictionaries.resolve() for audited layers.

    Same highest-priority rule, same requested-locale-first fallback order.
    The mandatory prior dictionaries.audit() rejects stale/unauthorized layers.
    """
    by_locale: dict[str, dict] = {}
    sources = []
    root = project.catalog.resolve().parent
    for language in catalog['languages']:
        locale = language['tag']
        if locales is not None and locale not in locales:
            continue
        current = {}
        for layer in language['layers']:
            path = dictionaries.safe_file(root, layer['path'])
            count = 0
            for record, _ in dictionaries.layer_records(path, layer['kind']):
                count += 1
                kid = record['semantic_id']
                if kid not in registered:
                    continue
                candidate = (layer['priority'], record['preferred_term'], layer['layer_id'])
                old = current.get(kid)
                if old is None or candidate[0] > old[0]:
                    current[kid] = candidate
                elif candidate[0] == old[0] and candidate[1] != old[1]:
                    # Should be impossible after dictionaries.audit().
                    raise Scan14Error(f'Conflit lexical de priorité égale: {locale}/{kid}')
            sources.append({
                'locale': locale, 'couche': layer['layer_id'], 'type': layer['kind'],
                'chemin': layer['path'], 'priorite': layer['priority'],
                'entrees_lues': count, 'sha256': layer['sha256'],
                'integrite': 'validee_par_dik_audit',
            })
        by_locale[locale] = current
    return by_locale, sources


def _resolve(tag: str, sid: str, catalog_languages: dict, by_locale: dict) -> tuple[str,str,str,str]:
    if tag not in catalog_languages:
        return 'langue_non_configuree','','',''
    for effective in [tag, *catalog_languages[tag]['fallbacks']]:
        selected = by_locale[effective].get(sid)
        if selected:
            _, word, layer = selected
            return ('direct' if effective == tag else 'repli'), word, effective, layer
    return 'manquant','','',''


def scan14(*, project: str | Path, output: str | Path,
           konstellation: str | Path | None = None,
           corpus: str = 'data/demo.pack.json',
           spek: str | Path | None = None,
           handoff: str | Path | None = None,
           mapping: str | Path | None = None) -> dict:
    """Audit exactly 14 targets; output a *new* directory of traceable CSV/JSON.

    `mapping` is deliberately rejected: a user-supplied CSV marked "accepted"
    does not establish independently proven cross-repository semantic identity.
    """
    if mapping is not None:
        raise Scan14Error('Mapping inter-projets non qualifié : preuve diK révisée non disponible; refus de le traiter comme exactMatch accepté')
    project = load_project(project)
    dest = Path(output).expanduser().resolve()
    if dest.exists():
        raise Scan14Error(f'Le dossier de rapport existe déjà: {dest}')
    if dest == project.manifest.parent or project.manifest.parent in dest.parents:
        raise Scan14Error('Le rapport ne peut pas être créé dans la source du projet diK')
    if konstellation is not None:
        ks = Path(konstellation).expanduser().resolve()
        if ks.is_dir() and (dest == ks or ks in dest.parents):
            raise Scan14Error('Le rapport ne peut pas être créé dans la source Konstellation')
    else:
        ks = None
    if handoff is not None:
        _check_handoff(json.loads(Path(handoff).read_text(encoding='utf-8')), str(handoff))
    if spek is not None:
        source_spek = Source(spek)
        try:
            _check_handoff(source_spek.js('integrations/unesco-mt1-10/handoff.json'), str(spek))
        finally:
            source_spek.close()

    # The canonical diK audit enforces layer sha256, schema, namespaces,
    # priority conflicts and *approved* external crosswalks before any publication.
    dictionaries.audit(project.catalog, project.crosswalk, project.registry)
    graph = dictionaries.read_json(project.graph)
    registry = dictionaries.read_json(project.registry)
    catalog = dictionaries.read_json(project.catalog)
    if graph['namespace_id'] != registry['namespace_id'] or catalog['namespace_id'] != registry['namespace_id']:
        raise Scan14Error('Namespace graphe / registre / catalogue divergent')
    active = framework_coverage._references(graph, registry)
    ids = sorted((entry['id'],entry['kind']) for entry in registry['identities']
                 if entry['kind'] in ('entity','property'))
    identities = [(sid, 'KQ' if kind == 'entity' else 'KP') for sid, kind in ids]
    known = {sid for sid,_ in identities}
    selected_languages = {row['tag']:row for row in catalog['languages']}
    by_locale, sources = _preindexed_layers(project, catalog, known)
    counts = collections.Counter()
    detailed = []
    summary = []
    active_ids = active['KQ'] | active['KP']
    for locale in TARGET_LOCALES:
        per_locale = collections.Counter()
        for sid, family in identities:
            state, word, effective, layer = _resolve(locale, sid, selected_languages, by_locale)
            counts[state] += 1
            per_locale[state] += 1
            action = {
                'direct': 'aucune',
                'repli': 'verifier_si_terme_direct_requis',
                'manquant': 'rechercher_dans_les_dictionnaires_existants_puis_qualifier',
                'langue_non_configuree': 'declarer_langue_et_fournir_une_couche_auditable',
            }[state]
            detailed.append({
                'namespace_id': registry['namespace_id'], 'semantic_id': sid, 'famille': family,
                'dans_graphe': 'oui' if sid in active_ids else 'non',
                'locale':locale, 'etat':state, 'libelle_resolu':word,
                'langue_source':effective, 'preuve_couche':layer,
                'statut_preuve':'catalogue_audite','action':action,
            })
        summary.append({
            'locale': locale, 'references_KQ_KP': len(identities),
            'direct': per_locale['direct'], 'repli':per_locale['repli'],
            'manquant':per_locale['manquant'],
            'langue_non_configuree':per_locale['langue_non_configuree'],
            'pourcentage_direct': round(100 * per_locale['direct'] / len(identities), 2)
                if identities and locale in selected_languages else '',
            'scope':'REGISTRE_KQ_KP_PROJET_SELECTIONNE',
        })

    payload = {'corpus_fourni':False,'entites':0,'assertions':0}
    terms = []
    direct_pack = []
    ui = []
    if ks is not None:
        source_kon = Source(ks)
        try:
            terms_raw, pack = corpus_terms(source_kon, corpus)
            for row in terms_raw:
                terms.append({**row, 'namespace_id':'', 'semantic_id':'',
                              'statut_alignement':'non_aligne',
                              'action':'examiner_une_preuve_d_identite_avant_couverture'})
            for relation in pack.get('registry', {}).get('relations', []):
                localized = relation.get('label', {})
                if not isinstance(localized, dict):
                    raise Scan14Error('Étiquette de relation de Konstellation non multilingue')
                for locale in TARGET_LOCALES:
                    value = localized.get(locale, '')
                    direct_pack.append({
                        'id_relation':relation['id'], 'locale':locale,
                        'libelle_direct_pack':value,
                        'etat_pack':'direct_dans_pack' if value else 'absent_du_pack_a_verifier_dans_dik',
                    })
            ui = ui_candidate_strings(source_kon)
            payload = {
                'corpus_fourni': True,'titre':pack.get('title'),
                'synthetique':pack.get('synthetic'),
                'entites':len(pack.get('entities',[])),
                'assertions':len(pack.get('assertions',[])),
                'champs_textuels':len(terms),'chaines_ui_candidates':len(ui),
                'libelles_relations_directs':sum(r['etat_pack']=='direct_dans_pack' for r in direct_pack),
            }
        finally:
            source_kon.close()

    result = {
        'schema':'dik.coverage.scan14/1.0', 'mode':'LECTURE_SEULE',
        'locales_cibles':list(TARGET_LOCALES), 'projet':str(project.manifest),
        'namespace_id':registry['namespace_id'],
        'catalogue':str(project.catalog),
        'catalogue_sha256':dictionaries.sha256(project.catalog),
        'registre_sha256':dictionaries.sha256(project.registry),
        'graphe_sha256':dictionaries.sha256(project.graph),
        'catalogue_selectionne_est_demo': 'examples/demo/' in project.manifest.as_posix(),
        'langues_declarees_dans_catalogue':sorted(selected_languages),
        'identites_KQ_KP_registre':len(identities),
        'identites_KQ_KP_graphe':len(active_ids),
        'couches_auditees':len(sources), 'entrees_lexicales_par_couche':sum(x['entrees_lues'] for x in sources),
        'totaux_statuts':{key:counts[key] for key in ('direct','repli','manquant','langue_non_configuree')},
        'couverture_par_langue':summary,
        'corpus':payload, 'termes_konstellation_non_alignes':len(terms),
        'crosswalk_konstellation_qualifie':False,
        'reseau_utilise':False,
        'avertissements':[
            'Les rapports ne représentent que le projet diK choisi, pas tous les dictionnaires possibles.',
            'Une langue non configurée ne prouve pas que le terme est absent de toutes les ressources.',
            'Un repli ne prouve pas une traduction directe.',
            'Une chaîne ou un libellé Konstellation n’est pas automatiquement un KQ/KP correspondant.',
            'La qualité linguistique, les licences et la couverture industrielle ne sont pas certifiées.',
        ]
    }
    if dest.parent.exists() and dest.parent.is_symlink():
        raise Scan14Error('Parent de sortie symbolique refusé')
    dest.parent.mkdir(parents=True,exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix='.dik-scan14-',dir=dest.parent))
    try:
        columns=['namespace_id','semantic_id','famille','dans_graphe','locale','etat',
                 'libelle_resolu','langue_source','preuve_couche','statut_preuve','action']
        _csv(stage/'registre_14_langues_KQ_KP.csv',detailed,columns)
        _csv(stage/'lacunes_14_langues.csv',[r for r in detailed if r['etat']!='direct'],columns)
        _csv(stage/'couverture_14_langues.csv',summary,
             ['locale','references_KQ_KP','direct','repli','manquant','langue_non_configuree','pourcentage_direct','scope'])
        _csv(stage/'couches_lexicales_auditees.csv',sources,
             ['locale','couche','type','chemin','priorite','entrees_lues','sha256','integrite'])
        _json(stage/'rapport.json',result)
        if ks is not None:
            _csv(stage/'inventaire_termes_konstellation.csv',terms,
                 ['source','id','role','canal','texte_fr','namespace_id','semantic_id','statut_alignement','action'])
            _csv(stage/'libelles_multilingues_dans_pack.csv',direct_pack,
                 ['id_relation','locale','libelle_direct_pack','etat_pack'])
            _csv(stage/'chaines_interface_candidats.csv',ui,
                 ['fichier','ligne_approx','texte_candidat','origine','etat'])
        if dest.exists():
            raise Scan14Error(f'Le dossier de rapport existe déjà: {dest}')
        stage.rename(dest)
    finally:
        if stage.exists():
            shutil.rmtree(stage)
    return result
