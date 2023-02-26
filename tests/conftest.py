from __future__ import annotations

from pathlib import Path

import pytest
from healthcheck import load_healthcheck
from healthcheck import RobotHealthCheck


@pytest.fixture
def fixtures_dir() -> Path:
    return Path(__file__).parent / "_fixtures"


@pytest.fixture
def data_json(fixtures_dir) -> Path:
    return fixtures_dir / "data.json"


@pytest.fixture
def data_pickle(fixtures_dir) -> Path:
    return fixtures_dir / "data.pkl.xz"


@pytest.fixture
def robot_health_check(data_pickle) -> RobotHealthCheck:
    return load_healthcheck(data_pickle)
