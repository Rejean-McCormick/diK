import csv
import json
import zipfile
from pathlib import Path

import pytest
from dik.v53_export import export_v53


def test_shareable_export_redacts_paths_and_words(tmp_path):
    root=tmp_path/'dik'; run=root/'reports'/'resolution_14_langues'/'RESOLUTION_TEST'
    run.mkdir(parents=True)
    (run/'rapport.json').write_text(json.dumps({'etat':'PARTIEL','date_utc':'now',
        'portefeuille_officiel':'C:\\Users\\private',
        'locales':['fr'],'traduction_entre_langues':False,
        'totaux':{'kristals_officiels':126},
        'wikidata_thematic':{'status':'PARTIAL'},'wikidata_v53':{'activations':0}}))
    (run/'wikidata_forms_candidates.csv').write_text('locale;form;source_id\nfr;secret_word;local-1\n')
    (run/'wikidata_scan_progress.csv').write_text('source_id;checkpoint_ref\nlocal-1;C:\\secrets\\db.sqlite\n')
    output=export_v53(dik_root=root,resolution_dir=run)
    with zipfile.ZipFile(output['zip']) as z:
        payload='\n'.join(z.read(n).decode('utf-8-sig') for n in z.namelist())
        assert 'secret_word' not in payload and 'C:\\secrets' not in payload
        assert 'C:\\Users' not in payload
        assert 'local-1' in payload
        assert 'kristals_officiels' in payload
        assert 'EXPURGE' in payload


def test_export_rejects_outside_reports(tmp_path):
    root=tmp_path/'dik'; (root/'reports').mkdir(parents=True)
    other=tmp_path/'outside';other.mkdir()
    with pytest.raises(ValueError):
        export_v53(dik_root=root,resolution_dir=other)
