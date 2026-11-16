import numpy as np
from scipy.stats import pearsonr

import styles as S


RESEARCH_QUESTIONS = (
    "What trends can be seen in the climate indicators over the years?",
    "How do average temperature and CO₂ emissions differ across countries and years?",
    "Is there a relationship between CO₂ emissions, average temperature and sea-level rise?",
    "How do renewable energy use and forest area vary in the dataset?",
    "What patterns can be seen in extreme weather events?"
)


HYPOTHESES = (
    (
        "H₀₁: No significant relationship between CO₂ emissions per capita "
        "and average temperature. H₁₁: A significant relationship.",
        "H₀₁",
        "H₁₁",
        "CO2 Emissions (Tons/Capita)",
        "Avg Temperature (°C)"
    ),
    (
        "H₀₂: No significant relationship between average temperature and "
        "sea-level rise. H₁₂: A significant relationship.",
        "H₀₂",
        "H₁₂",
        "Avg Temperature (°C)",
        "Sea Level Rise (mm)"
    ),
    (
        "H₀₃: No significant relationship between renewable energy (%) and "
        "CO₂ emissions per capita. H₁₃: A significant relationship.",
        "H₀₃",
        "H₁₃",
        "Renewable Energy (%)",
        "CO2 Emissions (Tons/Capita)"
    )
)


def _format(value, decimals=2):
    return f"{value:,.{decimals}f}" if np.isfinite(value) else "N/A"


def _annual_trend(df, column, label, unit):
    annual = df.groupby("Year")[column].mean().dropna()

    if annual.empty:
        return f"{label}: no numeric observations."

    if len(annual) == 1:
        return (
            f"{label}: {_format(annual.iloc[0])} {unit} "
            f"in {int(annual.index[0])}."
        )

    years = annual.index.to_numpy(dtype=float)
    values = annual.to_numpy(dtype=float)
    slope = float(np.polyfit(years, values, 1)[0])
    direction = (
        "upward" if slope > 0
        else "downward" if slope < 0
        else "flat"
    )

    return (
        f"{label}: annual mean changed from "
        f"{_format(values[0])} {unit} in {int(years[0])} to "
        f"{_format(values[-1])} {unit} in {int(years[-1])}; "
        f"linear trend {direction} ({slope:+.3f} {unit}/year)."
    )


def _country_extremes(df, column, label, unit):
    means = df.groupby("Country")[column].mean().dropna()

    if means.empty:
        return f"{label}: no numeric observations."

    lowest = means.idxmin()
    highest = means.idxmax()
    return (
        f"{label}: lowest country mean {lowest} "
        f"({_format(means[lowest])} {unit}); highest {highest} "
        f"({_format(means[highest])} {unit})."
    )


def _correlation(df, x_column, y_column):
    values = df[[x_column, y_column]].to_numpy(dtype=float)
    values = values[np.isfinite(values).all(axis=1)]
    x = values[:, 0]
    y = values[:, 1]
    n = len(values)

    if n < 3 or np.std(x) == 0 or np.std(y) == 0:
        return float("nan"), float("nan"), n

    result = pearsonr(x, y)
    return float(result.statistic), float(result.pvalue), n


def _association_text(label, df, x_column, y_column):
    r, p_value, n = _correlation(df, x_column, y_column)

    if not np.isfinite(r):
        return f"{label}: insufficient valid variation (n={n:,})."

    p_text = f"{p_value:.3g}" if np.isfinite(p_value) else "N/A"
    return f"{label}: r={r:+.3f}, p={p_text}, n={n:,}."


def _hypothesis_finding(
    df,
    title,
    null_label,
    alternative_label,
    x_column,
    y_column
):
    r, p_value, n = _correlation(df, x_column, y_column)

    if not np.isfinite(r):
        decision = "Insufficient valid variation to test this hypothesis."
    elif not np.isfinite(p_value):
        decision = "Insufficient pairs to determine statistical significance."
    elif p_value < 0.05:
        decision = (
            f"Reject {null_label} at alpha = 0.05; "
            f"evidence supports {alternative_label}."
        )
    else:
        decision = (
            f"Fail to reject {null_label} at alpha = 0.05; "
            f"{alternative_label} is not supported."
        )

    r_text = f"{r:+.3f}" if np.isfinite(r) else "N/A"
    p_text = f"{p_value:.3g}" if np.isfinite(p_value) else "N/A"
    return (
        title,
        f"Pearson r={r_text}, p={p_text}, n={n:,}. {decision}"
    )


def build_findings(df, period):
    years = df["Year"].dropna()
    if years.empty:
        year_range = "no year range available"
    else:
        year_range = f"{int(years.min())}–{int(years.max())}"

    overview = (
        f"Selected dashboard period: {period}. "
        f"{len(df):,} country-year records across "
        f"{df['Country'].nunique():,} countries; years {year_range}."
    )

    trends = [
        _annual_trend(
            df,
            "Avg Temperature (°C)",
            "Temperature",
            "°C"
        ),
        _annual_trend(
            df,
            "CO2 Emissions (Tons/Capita)",
            "CO₂ emissions",
            "tons/capita"
        ),
        _annual_trend(
            df,
            "Sea Level Rise (mm)",
            "Sea-level rise",
            "mm"
        ),
        _annual_trend(df, "Rainfall (mm)", "Rainfall", "mm"),
        _annual_trend(
            df,
            "Renewable Energy (%)",
            "Renewable energy",
            "%"
        ),
        _annual_trend(
            df,
            "Forest Area (%)",
            "Forest area",
            "%"
        ),
        _annual_trend(
            df,
            "Population",
            "Population",
            "people"
        ),
        _annual_trend(
            df,
            "Extreme Weather Events",
            "Extreme weather events",
            "events"
        )
    ]

    relationships = [
        _association_text(
            "CO₂ emissions vs temperature",
            df,
            "CO2 Emissions (Tons/Capita)",
            "Avg Temperature (°C)"
        ),
        _association_text(
            "Temperature vs sea-level rise",
            df,
            "Avg Temperature (°C)",
            "Sea Level Rise (mm)"
        ),
        _association_text(
            "CO₂ emissions vs sea-level rise",
            df,
            "CO2 Emissions (Tons/Capita)",
            "Sea Level Rise (mm)"
        )
    ]

    questions = [
        (
            RESEARCH_QUESTIONS[0],
            " ".join(trends)
        ),
        (
            RESEARCH_QUESTIONS[1],
            " ".join((
                _country_extremes(
                    df,
                    "Avg Temperature (°C)",
                    "Average temperature",
                    "°C"
                ),
                _country_extremes(
                    df,
                    "CO2 Emissions (Tons/Capita)",
                    "CO₂ emissions",
                    "tons/capita"
                )
            ))
        ),
        (
            RESEARCH_QUESTIONS[2],
            " ".join(relationships)
        ),
        (
            RESEARCH_QUESTIONS[3],
            " ".join((
                _annual_trend(
                    df,
                    "Renewable Energy (%)",
                    "Renewable energy",
                    "%"
                ),
                _country_extremes(
                    df,
                    "Renewable Energy (%)",
                    "Renewable energy",
                    "%"
                ),
                _annual_trend(
                    df,
                    "Forest Area (%)",
                    "Forest area",
                    "%"
                ),
                _country_extremes(
                    df,
                    "Forest Area (%)",
                    "Forest area",
                    "%"
                )
            ))
        ),
        (
            RESEARCH_QUESTIONS[4],
            " ".join((
                _annual_trend(
                    df,
                    "Extreme Weather Events",
                    "Extreme weather events",
                    "events"
                ),
                _country_extremes(
                    df,
                    "Extreme Weather Events",
                    "Extreme weather events",
                    "events"
                )
            ))
        )
    ]

    hypotheses = [
        _hypothesis_finding(df, *hypothesis)
        for hypothesis in HYPOTHESES
    ]

    return {
        "overview": overview,
        "questions": questions,
        "hypotheses": hypotheses
    }


class ResearchFindingsSection:

    def __init__(self, parent):
        import tkinter as tk

        self.frame = tk.Frame(parent, bg=S.BG)
        self.frame.pack(fill="x", pady=(0, 16))

        card = tk.Frame(
            self.frame,
            bg=S.WHITE,
            highlightbackground=S.BORDER,
            highlightthickness=1
        )
        card.pack(fill="x")

        tk.Label(
            card,
            text="Research findings",
            bg=S.WHITE,
            fg=S.TEXT,
            font=(S.FONT, 12, "bold")
        ).pack(anchor="w", padx=18, pady=(16, 2))

        self.overview = tk.Label(
            card,
            text="",
            bg=S.WHITE,
            fg=S.MUTED,
            font=(S.FONT, 8),
            justify="left",
            wraplength=760
        )
        self.overview.pack(anchor="w", padx=18, pady=(0, 10))

        self.question_labels = []
        for question in RESEARCH_QUESTIONS:
            tk.Label(
                card,
                text=question,
                bg=S.WHITE,
                fg=S.TEXT,
                font=(S.FONT, 9, "bold"),
                justify="left",
                wraplength=760
            ).pack(anchor="w", padx=18, pady=(8, 2))

            finding = tk.Label(
                card,
                text="",
                bg=S.WHITE,
                fg=S.MUTED,
                font=(S.FONT, 9),
                justify="left",
                wraplength=760
            )
            finding.pack(anchor="w", padx=18, pady=(0, 4))
            self.question_labels.append(finding)

        tk.Label(
            card,
            text="Hypothesis tests",
            bg=S.WHITE,
            fg=S.TEXT,
            font=(S.FONT, 10, "bold")
        ).pack(anchor="w", padx=18, pady=(14, 4))

        self.hypothesis_labels = []
        for title, _null, _alternative, _x_column, _y_column in HYPOTHESES:
            tk.Label(
                card,
                text=title,
                bg=S.WHITE,
                fg=S.TEXT,
                font=(S.FONT, 9, "bold"),
                justify="left",
                wraplength=760
            ).pack(anchor="w", padx=18, pady=(6, 2))

            finding = tk.Label(
                card,
                text="",
                bg=S.WHITE,
                fg=S.MUTED,
                font=(S.FONT, 9),
                justify="left",
                wraplength=760
            )
            finding.pack(anchor="w", padx=18, pady=(0, 4))
            self.hypothesis_labels.append(finding)

        tk.Label(
            card,
            text=(
                "Two-sided Pearson tests use alpha = 0.05. "
                "P-values are exploratory and do not adjust for repeated "
                "country/year observations or multiple tests; correlation "
                "does not establish causation."
            ),
            bg=S.WHITE,
            fg=S.MUTED,
            font=(S.FONT, 8),
            justify="left",
            wraplength=760
        ).pack(anchor="w", padx=18, pady=(12, 16))

    def update(self, df, period):
        findings = build_findings(df, period)
        self.overview.config(text=findings["overview"])

        for label, (_question, result) in zip(
            self.question_labels,
            findings["questions"]
        ):
            label.config(text=result)

        for label, (_hypothesis, result) in zip(
            self.hypothesis_labels,
            findings["hypotheses"]
        ):
            label.config(text=result)
