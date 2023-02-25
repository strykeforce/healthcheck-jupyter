from __future__ import annotations

from pathlib import Path

from healthcheck import load_healthcheck
from healthcheck import load_json


def test_load_json(data_json: Path):
    hc = load_json(data_json)
    assert len(hc.df) == 250


def test_load_pickle(data_pickle: Path):
    hc = load_healthcheck(data_pickle)
    assert len(hc.df) == 250
