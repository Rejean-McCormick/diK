from pathlib import Path

import pytest

from dik.iana_registry import RegistryError, check_tag, load_registry

FIXTURE = Path(__file__).parents[1] / 'examples/world-dictionaries/iana-fixtures/synthetic-language-subtag-registry.txt'


def test_iana_fixture_load_and_summary():
    reg = load_registry(FIXTURE)
    assert reg.file_date == '2020-01-01'
    assert reg.summary()['authority_verified'] is False
    assert reg.get('language', 'FR')['Description'] == ['French']
    assert reg.get('script', 'hans') is not None


@pytest.mark.parametrize('tag,canonical', [
    ('fr', 'fr'), ('fr-CA', 'fr-CA'), ('EN-us', 'en-US'),
    ('zh-Hans-CN', 'zh-Hans-CN'), ('sr-Latn-RS', 'sr-Latn-RS'),
    ('ca-valencia', 'ca-valencia'), ('en-a-foo-b-bar', 'en-a-foo-b-bar'),
    ('x-kristal-internal', 'x-kristal-internal'), ('i-klingon', 'i-klingon'),
])
def test_accept_bcp47_samples(tag, canonical):
    res = check_tag(tag, load_registry(FIXTURE))
    assert res['valid'] and res['normalized_case'] == canonical


@pytest.mark.parametrize('tag', ['fr_XY', 'fr-XX', 'abc', 'fr-Latn-Latn', 'fr-a',
                                'fr-a-abc-a-xyz', 'ca-valencia-valencia', 'en-CA-x', 'x'])
def test_invalid_bcp47_and_repeated_subtags(tag):
    res = check_tag(tag, load_registry(FIXTURE))
    assert res['valid'] is False


def test_unknown_prefix_and_deprecation():
    reg = load_registry(FIXTURE)
    assert check_tag('fr-valencia', reg)['valid'] is False
    result = check_tag('iw', reg)
    assert result['valid'] is True
    assert 'deprecated:language:iw:preferred=he' in result['notes']


def test_bad_header_rejected(tmp_path):
    p = tmp_path/'registry.txt'
    p.write_text(FIXTURE.read_text().replace('File-Date: ', 'File-Dates: ', 1))
    with pytest.raises(RegistryError):
        load_registry(p)


def test_duplicate_subtag_rejected(tmp_path):
    p = tmp_path/'registry.txt'
    p.write_text(FIXTURE.read_text()+ 'Type: language\nSubtag: fr\nDescription: duplicate\nAdded: 2005-10-16\n%%\n')
    with pytest.raises(RegistryError, match='duplicate'):
        load_registry(p)


def test_unexpected_folded_line_rejected(tmp_path):
    p = tmp_path/'registry.txt'
    p.write_text(FIXTURE.read_text().replace('Type: language', ' bogus\nType: language', 1))
    with pytest.raises(RegistryError):
        load_registry(p)


def test_max_bytes_rejected():
    with pytest.raises(RegistryError):
        load_registry(FIXTURE, max_bytes=200)
