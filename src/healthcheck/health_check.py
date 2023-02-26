from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pandas as pd
from pandas import DataFrame


class HealthCheck:
    def __init__(self, data: dict[str, Any] | DataFrame) -> None:
        if isinstance(data, DataFrame):
            self.df = data
            return

        meta = DataFrame(data["meta"])
        meta["case_uuid"] = meta["case_uuid"].astype("category")
        meta["name"] = meta["name"].astype("category")
        meta["type"] = meta["type"].astype("category")
        meta["datetime"] = pd.Timestamp.now()

        data = DataFrame(data["data"])

        self.df = pd.merge(meta, data, on="case", suffixes=("_set", "_measured"))

    def _path_name(self):
        ts = self.df.iloc[0, 8]
        return f"{ts.strftime('%Y-%m-%d-%H%M')}.pkl.xz"

    # TODO: allow path to be a Path and check if it is a directory
    def save(self, path: str | Path | None = None, overwrite=False) -> Path:
        if path is None:
            path = Path(self._path_name())

        if isinstance(path, str):
            path = Path(path)

        if path.is_dir():  # type: ignore
            path = path / self._path_name()

        if path.is_file() and not overwrite:  # type: ignore
            raise RuntimeError("unable to save, file exists and overwrite=False")

        self.df.to_pickle(path, compression="infer")
        return path  # type: ignore

    def subsystem_for_talon(self, talon: int) -> str:
        mask = self.df["talon_measured"] == talon
        subsystems = self.df[mask]["name"].unique()
        n = len(subsystems)

        if n == 0:
            print(f"no subsystem found for talon {talon}", file=sys.stderr)
            return ""

        if n > 1:
            print(f"multiple subsystem found for talon {talon}", file=sys.stderr)
            return ",".join(subsystems)

        return subsystems[0]


class SwerveDriveHealthCheck(HealthCheck):
    def plot(self, voltage=True):
        pass


class RobotHealthCheck(HealthCheck):
    @property
    def subsystems(self) -> list[str]:
        """Get the list of subsystems that were health checked."""
        return list(self.df["name"].unique())

    @property
    def swerve_drive_health_check(self) -> SwerveDriveHealthCheck:
        return SwerveDriveHealthCheck(self.df)
