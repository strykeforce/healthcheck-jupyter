from __future__ import annotations

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

    def save(self, path: str | None = None) -> None:
        if path is None:
            ts = self.df.iloc[0, 7]
            path = f"{ts.strftime('%Y-%m-%d-%H%M')}.pkl.xz"
        self.df.to_pickle(path, compression="infer")

    @property
    def subsystems(self) -> list[str]:
        """Get the list of subsystems that were health checked."""
        return list(self.df["name"].unique())
