from pathlib import Path

import pytest

from dik.iana_fetch import _check_url, fetch_iana_registry, REGISTRY_URL

FIX = Path(__file__).parents[1]/'examples/world-dictionaries/iana-fixtures/synthetic-language-subtag-registry.txt'


class FakeResponse:
    status = 200
    def __init__(self, url=REGISTRY_URL):
        self.url = url
        self.data = FIX.read_bytes()
        self.done = False
    def geturl(self):
        return self.url
    def read(self, limit):
        if self.done:
            return b''
        self.done = True
        return self.data[:limit]
    def __enter__(self):
        return self
    def __exit__(self, *args):
        pass


class FakeOpener:
    def __init__(self, url=REGISTRY_URL):
        self.url = url
    def open(self, req, timeout):
        assert req.full_url == REGISTRY_URL
        assert timeout <= 180
        return FakeResponse(self.url)


def test_iana_fetch_with_injected_offline_response(tmp_path):
    out = tmp_path/'real-file-only-for-test.txt'
    report = fetch_iana_registry(output=out, user_agent='diK-test (contact: tests@example.org)', opener=FakeOpener())
    assert out.read_bytes() == FIX.read_bytes()
    assert report['file_date'] == '2020-01-01'
    assert report['independent_source_attestation'] is False
    with pytest.raises(FileExistsError):
        fetch_iana_registry(output=out, user_agent='diK-test (contact: tests@example.org)', opener=FakeOpener())


@pytest.mark.parametrize('bad_url', ['http://www.iana.org/assignments/language-subtag-registry/language-subtag-registry',
                                   'https://evil.example.org/assignments/language-subtag-registry/language-subtag-registry',
                                   'https://www.iana.org/assignments/language-subtag-registry/language-subtag-registry?redirect=1',
                                   'https://user:pass@www.iana.org/assignments/language-subtag-registry/language-subtag-registry'])
def test_url_not_official_rejected(bad_url):
    with pytest.raises(ValueError, match='official'):
        _check_url(bad_url)


def test_redirect_to_other_host_rejected(tmp_path):
    out = tmp_path/'test.txt'
    with pytest.raises(ValueError):
        fetch_iana_registry(output=out, user_agent='diK-test (contact: tests@example.org)', opener=FakeOpener('https://bad.example.org/'))
    assert not out.exists()


def test_iana_expected_sha256_mismatch_rejected(tmp_path):
    out = tmp_path/'test.txt'
    with pytest.raises(ValueError, match='SHA-256'):
        fetch_iana_registry(output=out, user_agent='diK-test (contact: tests@example.org)', opener=FakeOpener(), expected_sha256='a'*64)
    assert not out.exists()
