"""Export reviewed diK curated terms into an optional Konstellation sidecar.

Usage: python integrations/konstellation_light/from_dik.py --dictionary CURATED.json
       --slug astronomy --state-ref urn:kristal:astronomy:state
       --surface-digest sha256:... --out overlays/astronomy/fr.json
No translation, implicit identity resolution or AI generation is performed.
"""
import argparse
import json
from pathlib import Path
from contract import ContractError,new_document,save

def export(doc, *, slug,state_ref,surface_digest):
    if doc.get('schema_version')!='11.0' or doc.get('artifact_type')!='kristal_curated_dictionary':
        raise ContractError('Reviewed curated dictionary required; imported records are not automatically approved')
    locale=doc.get('language')
    rows=[];relations=[]
    for entry in doc.get('entries',[]):
        review=entry.get('review') or {}
        ref=review.get('decision_id')
        if not ref:raise ContractError('Missing curated review decision')
        pid=entry['semantic_id']
        prov={'provider':'dik','source_refs':[], 'review_status':'reviewed','review_ref':ref}
        if pid.startswith('KP'):
            relations.append({'relation_id':pid,'label':entry['preferred_term'],'provenance':prov})
        else:
            rows.append({'node_id':pid,'label':entry['preferred_term'],'provenance':prov})
    return new_document(slug,state_ref,surface_digest,locale,rows,relations=relations)

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    for k in ['dictionary','slug','state-ref','surface-digest','out']:ap.add_argument('--'+k,required=True)
    a=ap.parse_args()
    doc=json.loads(Path(a.dictionary).read_text(encoding='utf-8'))
    print(save(a.out,export(doc,slug=a.slug,state_ref=a.state_ref,surface_digest=a.surface_digest)))
