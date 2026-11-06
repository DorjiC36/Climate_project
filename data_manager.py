from pathlib import Path
import pandas as pd
import numpy as np


DEFAULT_DATA = (
    Path(__file__).parent
    / "data"
    / "climate_change_dataset.csv"
)


REQUIRED = [
    "Year",
    "Country",
    "Avg Temperature (°C)",
    "CO2 Emissions (Tons/Capita)",
    "Sea Level Rise (mm)",
    "Rainfall (mm)",
    "Population",
    "Renewable Energy (%)",
    "Extreme Weather Events",
    "Forest Area (%)"
]


def load_dataset(path=DEFAULT_DATA):

    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(
            f"Dataset not found: {path}"
        )

    df = pd.read_csv(
        path,
        encoding="utf-8-sig",
        on_bad_lines="error"
    )

    missing = [
        col for col in REQUIRED
        if col not in df.columns
    ]

    if missing:
        raise ValueError(
            "CSV is missing required columns: "
            + ", ".join(missing)
        )

    df = df.copy()

    df["Year"] = pd.to_numeric(
        df["Year"],
        errors="coerce"
    )

    for col in REQUIRED:

        if col not in ("Year", "Country"):

            df[col] = pd.to_numeric(
                df[col],
                errors="coerce"
            )

    df["Country"] = (
        df["Country"]
        .astype(str)
        .str.strip()
    )

    df = df.dropna(
        subset=["Year", "Country"]
    )

    df = df[
        df["Country"] != ""
    ]

    df["Year"] = df["Year"].astype(int)

    if df.empty:
        raise ValueError(
            "The CSV has no usable rows."
        )

    return df.sort_values(
        ["Year", "Country"]
    ).reset_index(drop=True)


def export_csv(df, path):

    df.to_csv(
        path,
        index=False
    )