from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import requests

from . import RobotHealthCheck


def load_healthcheck(path: str | Path) -> RobotHealthCheck:
    df = pd.read_pickle(path, compression="infer")
    return RobotHealthCheck(df)


def load_json(path: str | Path) -> RobotHealthCheck:
    with open(path) as f:
        j = json.load(f)
    return RobotHealthCheck(j)


def load_roborio(endpoint: str = "http://10.27.67.2:2767/data") -> RobotHealthCheck:
    r = requests.get(endpoint)
    j = r.json()
    return RobotHealthCheck(j)
