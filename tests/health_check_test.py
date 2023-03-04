from __future__ import annotations

import json
from io import StringIO

import pandas as pd
import pytest
from healthcheck.health_check import HealthCheck


def test_save_none(robot_health_check):
    p = robot_health_check.save()
    assert str(p) == "2023-02-28-1057.pkl.xz"
    df = pd.read_pickle(p, compression="infer")
    hc = HealthCheck(df)
    assert robot_health_check.df.shape == hc.df.shape
    p.unlink(missing_ok=False)


def test_save_str(robot_health_check):
    path = "test-save.pkl.xz"
    p = robot_health_check.save(path)
    assert p.is_file()
    assert str(p) == path
    p.unlink(missing_ok=False)


def test_save_path_dir(robot_health_check, tmp_path):
    p = robot_health_check.save(tmp_path)
    p.resolve()
    assert p.is_file()
    assert p.parent == tmp_path
    assert p.name == "2023-02-28-1057.pkl.xz"
    p.unlink(missing_ok=False)


def test_save_path_file(robot_health_check, tmp_path):
    p = robot_health_check.save(tmp_path / "test-save.pkl.xz")
    p.resolve()
    assert p.is_file()
    assert p.parent == tmp_path
    assert p.name == "test-save.pkl.xz"
    p.unlink(missing_ok=False)


def test_save_no_overwrite(robot_health_check):
    p = robot_health_check.save()
    with pytest.raises(RuntimeError):
        robot_health_check.save()
    p.unlink(missing_ok=False)


def test_subsystems(robot_health_check):
    assert ["DriveSubsystem", "IntakeSubsystem"] == robot_health_check.subsystems


def test_subsystems_for_talon(robot_health_check):
    assert robot_health_check.subsystem_for_talon(20) == "IntakeSubsystem"


def test_subsystems_for_talon_none(robot_health_check, capsys):
    assert robot_health_check.subsystem_for_talon(99) == ""
    captured = capsys.readouterr()
    assert captured.err == "no subsystem found for talon 99\n"


# Malformed - talon 1 in multiple subsystems
DATA_JSON = """
{
  "meta": {
  "case": { "0": 0, "1": 1  },
  "case_uuid": { "0": "8cb521e7-34d5-4317-9f23-7682f14e198d", "1": "a791a9a2-e8e1-49f3-89d6-3469354c3311" },
  "name": { "0": "DriveSubsystem", "1": "IntakeSubsystem" },
  "talon": { "0": 0, "1": 0 },
  "type": { "0": "time", "1": "time" },
  "output": { "0": 0.25, "1": 0.5 },
  "duration": { "0": 5000000, "1": 5000000 }
  },
  "data": {
    "case": { "0": 0, "1": 0, "2": 1, "3": 1  },
    "msec_elapsed": { "0": 0, "1": 5000, "2": 0, "3": 5000  },
    "talon": { "0": 1, "1": 1, "2": 1, "3": 1  },
    "voltage": { "0": 0.0, "1": 0.0, "2": 2.981427175, "3": 2.981427175 },
    "position": { "0": 2, "1": 2, "2": 2, "3": 2 },
    "speed": { "0": 0, "1": 0, "2": 0, "3": 0 },
    "supply_current": { "0": 0.125, "1": 0.125, "2": 0.125, "3": 0.125 },
    "stator_current": { "0": 0.0, "1": 0.0, "2": 0.5115, "3": 0.5115 }
  }
}
"""


def test_subsystems_for_talon_multiple(capsys):
    io = StringIO(DATA_JSON)
    data = json.load(io)
    hc = HealthCheck(data)
    assert hc.subsystem_for_talon(1) == "DriveSubsystem,IntakeSubsystem"
    captured = capsys.readouterr()
    assert captured.err == "multiple subsystem found for talon 1\n"
