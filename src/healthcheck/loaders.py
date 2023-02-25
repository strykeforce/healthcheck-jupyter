from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import requests

from . import HealthCheck


def load_healthcheck(path: str | Path) -> HealthCheck:
    df = pd.read_pickle(path, compression="infer")
    return HealthCheck(df)


def load_json(path: str | Path) -> HealthCheck:
    with open(path) as f:
        j = json.load(f)
    return HealthCheck(j)


def load_roborio(endpoint: str = "http://10.27.67.2:2767/data") -> HealthCheck:
    r = requests.get(endpoint)
    j = r.json()
    return HealthCheck(j)
