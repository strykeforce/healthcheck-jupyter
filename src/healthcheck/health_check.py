from __future__ import annotations

import itertools
import sys
from functools import cache
from pathlib import Path
from typing import Any

import pandas as pd
from matplotlib import pyplot as plt
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
        self.df.set_index(["talon_measured", "case"], inplace=True)
        self.df.sort_index(inplace=True)

    def _path_name(self) -> str:
        ts = self.df["datetime"].iloc[0]
        return f"{ts.strftime('%Y-%m-%d-%H%M')}.pkl.xz"

    @staticmethod
    def _history_dir() -> Path:
        path = Path.cwd() / "history"
        path.mkdir(exist_ok=True)
        return path

    def save(self, path: str | Path | None = None, overwrite=False) -> Path:
        if path is None:
            path = self._history_dir() / Path(self._path_name())

        if isinstance(path, str):
            path = Path(path)

        if path.is_dir():  # type: ignore
            path = path / self._path_name()

        if path.is_file() and not overwrite:  # type: ignore
            raise RuntimeError("unable to save, file exists and overwrite=False")

        self.df.to_pickle(path, compression="infer")
        return path  # type: ignore

    @property
    def cases(self):
        """Get all the health check test cases."""
        return (
            self.df[~self.df.index.get_level_values("case").duplicated()][
                ["name", "talon_set", "type", "output", "duration"]
            ]
            .reset_index(level=0, drop=True)
            .sort_index()
        )

    @cache
    def subsystem_for_talon(self, talon: int) -> str:
        """Get the Subsystem name for the specified talon."""

        try:
            subsystems = self.df.loc[talon, "name"].unique()
        except KeyError:
            print(f"no subsystem found for talon {talon}", file=sys.stderr)
            return ""

        if len(subsystems) > 1:
            print(f"multiple subsystem found for talon {talon}", file=sys.stderr)
            return ",".join(subsystems)

        return subsystems[0]

    def plot_y_limits(self, cases: list[int], talons: list[int]) -> tuple:
        idx = itertools.product(talons, cases)
        mask = self.df.index.isin(idx)
        df = self.df[mask]
        supply_s = df["supply_current"]
        stator_s = df["stator_current"]
        speed_s = df["speed"]
        return (
            (supply_s.min(), supply_s.max()),
            (stator_s.min(), stator_s.max()),
            (speed_s.min(), speed_s.max()),
        )

    def plot_talons(
        self,
        cases: list[int],
        talons: list[int],
        title: str | None = None,
        voltage=False,
        stator_current=True,
    ) -> None:
        """Plots talon health check measurements for specified cases."""
        num_cases = len(cases)
        if num_cases == 0 or len(talons) == 0:
            raise RuntimeError("cases and talons must each contain at least one value")

        if title is None:
            title = f"{self.df.loc[(talons[0], cases[0]), 'name'].iloc[0]} Talons"

        num_measures = 2
        if voltage:
            num_measures += 1
        if stator_current:
            num_measures += 1

        fig, axs = plt.subplots(
            num_cases,
            num_measures,
            squeeze=False,
            layout="constrained",
            sharex="all",
            figsize=(12, num_cases * 4),
        )

        supply_ylim, stator_ylim, speed_ylim = self.plot_y_limits(cases, talons)

        for row, case in enumerate(cases):
            ts = self.df.loc[(talons[0], case), "msec_elapsed"]
            output = self.df.loc[(talons[0], case), "output"].iloc[0] * 100
            for t in talons:
                col = 0
                if voltage:
                    axs[row][col].plot(ts, self.df.loc[(t, case), "voltage"])
                    axs[row][col].set(
                        ylabel="volts",
                        ylim=(-13, 13),
                        title=f"voltage at {output:0.0f}%",
                    )
                    axs[row][col].grid(visible=True, alpha=0.25)
                    col += 1

                axs[row][col].plot(ts, self.df.loc[(t, case), "supply_current"])
                axs[row][col].set(
                    ylabel="amps",
                    ylim=supply_ylim,
                    title=f"supply current at {output:0.0f}%",
                )
                axs[row][col].grid(visible=True, alpha=0.25)
                col += 1

                if stator_current:
                    axs[row][col].plot(ts, self.df.loc[(t, case), "stator_current"])
                    axs[row][col].set(
                        ylabel="amps",
                        ylim=stator_ylim,
                        title=f"stator current at {output:0.0f}%",
                    )
                    axs[row][col].grid(visible=True, alpha=0.25)
                    col += 1

                axs[row][col].plot(ts, self.df.loc[(t, case), "speed"])
                axs[row][col].set(
                    ylabel="ticks/100ms",
                    ylim=speed_ylim,
                    title=f"speed at {output:0.0f}%",
                )
                axs[row][col].grid(visible=True, alpha=0.25)
        axs[0][0].legend(talons)
        fig.suptitle(title)
        # fig.show()


class SwerveDriveHealthCheck(HealthCheck):
    pass


class RobotHealthCheck(HealthCheck):
    @property
    def subsystems(self) -> list[str]:
        """Get the list of subsystems that were health checked."""
        return list(self.df["name"].unique())

    @property
    def swerve_drive_health_check(self) -> SwerveDriveHealthCheck:
        return SwerveDriveHealthCheck(self.df)
