from unittest.mock import Mock
from urllib.error import URLError

import pytest

from sync import populate, zoterosync


def test_populate_stops_when_lexicon_download_fails(settings, tmp_path, monkeypatch):
    settings.LEXICON_URL = "https://example.org/lexicon.xlsx"
    settings.LEXICON_FILEPATH = str(tmp_path / "lexicon.xlsx")
    failure = URLError("download failed")
    monkeypatch.setattr(populate.urllib.request, "urlopen", Mock(side_effect=failure))
    load_lexicon = Mock()
    monkeypatch.setattr(populate, "load_lexicon_data", load_lexicon)

    with pytest.raises(URLError, match="download failed") as exc_info:
        populate.populate()

    assert exc_info.value is failure
    load_lexicon.assert_not_called()


def test_update_library_version_rejects_invalid_type():
    with pytest.raises(TypeError, match="version argument should be of type int"):
        zoterosync.update_local_library_version(Mock(), "invalid")
