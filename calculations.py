import numpy as np
import pandas as pd


def finite_values(series):
    arr = pd.to_numeric(
        series, errors="coerce"
    ).to_numpy(dtype=float)

    return arr[np.isfinite(arr)]


def safe_mean(values):
    a = np.asarray(values, dtype=float)
    a = a[np.isfinite(a)]

    return float(np.mean(a)) if a.size else float("nan")


def change_between(values):
    a = np.asarray(values, dtype=float)
    a = a[np.isfinite(a)]

    return float(a[-1] - a[0]) if a.size >= 2 else 0.0


def pct_change(old, new):
    if not np.isfinite(old) or old == 0:
        return float("nan")

    if not np.isfinite(new):
        return float("nan")

    return float((new - old) / abs(old) * 100)


def completeness(df):
    numeric = df.select_dtypes(include=[np.number])

    numeric_array = numeric.to_numpy(dtype=float)

    if numeric_array.size == 0:
        return 0.0

    valid = np.isfinite(numeric_array).sum()

    return float(100 * valid / numeric_array.size)


def annual_series(df, column, start_year=None):

    part = df if start_year is None else df[
        df["Year"] >= start_year
    ]

    if part.empty:
        return (
            np.array([], dtype=int),
            np.array([], dtype=float)
        )

    grouped = part.groupby("Year")[column].mean()

    years = grouped.index.to_numpy(dtype=int)
    values = grouped.to_numpy(dtype=float)

    return years, values


def country_summary(df):

    return df.groupby(
        "Country",
        as_index=False
    ).agg(
        records=("Year", "count"),
        years=("Year", "nunique"),
        temperature=("Avg Temperature (°C)", "mean"),
        co2=("CO2 Emissions (Tons/Capita)", "mean"),
        sea_level=("Sea Level Rise (mm)", "mean"),
        renewable=("Renewable Energy (%)", "mean"),
        extreme=("Extreme Weather Events", "mean"),
        forest=("Forest Area (%)", "mean")
    )