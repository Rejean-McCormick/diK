from pathlib import Path

from dik.cli import make_parser, run, main

BASE = Path(__file__).parents[1]/'examples/world-dictionaries'


def test_world_command_parse_and_audit():
    args = make_parser().parse_args(['world', 'resource-audit', '--catalog', str(BASE/'resource-catalog.json')])
    assert run(args)['discovery_resources'] >= 20


def test_world_cli_iana_and_tags(capsys):
    registry = str(BASE/'iana-fixtures/synthetic-language-subtag-registry.txt')
    assert main(['world','iana-audit','--registry',registry]) == 0
    assert main(['world','tag-check','--registry',registry,'--tags','fr-CA,xyz']) == 0
    assert 'unregistered_components' in capsys.readouterr().out


def test_world_cli_lexeme_gf_integration(tmp_path):
    source = str(BASE/'wikidata-lexeme-sample.jsonl')
    ob = str(tmp_path/'ob')
    gf = str(tmp_path/'gf')
    assert main(['world','lexemes-import','--dump',source,'--snapshot','cli-unit','--output-dir',ob]) == 0
    assert main(['world','lexemes-audit','--dir',ob]) == 0
    assert main(['world','gf-handoff','--observations',ob,'--output-dir',gf,'--locale','fr']) == 0
    assert main(['world','gf-audit','--dir',gf]) == 0
