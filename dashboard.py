import io
import os
import sys
from pathlib import Path

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

from calculations import completeness, country_summary, safe_mean
from data_manager import DEFAULT_DATA, load_dataset
from research_findings import build_findings


VARIABLES = {
    "Average temperature (°C)": "Avg Temperature (°C)",
    "CO₂ emissions (tons/capita)": "CO2 Emissions (Tons/Capita)",
    "Sea level rise (mm)": "Sea Level Rise (mm)",
    "Rainfall (mm)": "Rainfall (mm)",
    "Population": "Population",
    "Renewable energy (%)": "Renewable Energy (%)",
    "Extreme weather events": "Extreme Weather Events",
    "Forest area (%)": "Forest Area (%)",
}

SHORT_LABELS = {
    "Avg Temperature (°C)": "Temperature",
    "CO2 Emissions (Tons/Capita)": "CO₂",
    "Sea Level Rise (mm)": "Sea level",
    "Rainfall (mm)": "Rainfall",
    "Population": "Population",
    "Renewable Energy (%)": "Renewables",
    "Extreme Weather Events": "Extreme events",
    "Forest Area (%)": "Forest",
}
HEATMAP_PALETTES = {
    "Purple–green": "purplegreen",
    "Red–blue": "redblue",
    "Purple–orange": "purpleorange",
}
SOURCE_URL = "https://climateknowledgeportal.worldbank.org/"


def _configure_tk_library_paths():
    if sys.platform != "win32":
        return

    library_root = Path(sys.base_prefix) / "tcl"
    for tcl_path in sorted(library_root.glob("tcl*"), reverse=True):
        if not tcl_path.is_dir() or not (tcl_path / "init.tcl").is_file():
            continue

        tk_path = tcl_path.with_name("tk" + tcl_path.name[3:])
        if not (tk_path / "tk.tcl").is_file():
            continue

        for variable, library, marker in (
            ("TCL_LIBRARY", tcl_path, "init.tcl"),
            ("TK_LIBRARY", tk_path, "tk.tcl"),
        ):
            configured = os.environ.get(variable)
            if configured and (Path(configured) / marker).is_file():
                continue
            os.environ[variable] = str(library)
        return


@st.cache_data(show_spinner=False)
def _load_bundled_dataset():
    return load_dataset(DEFAULT_DATA)


@st.cache_data(show_spinner=False)
def _load_uploaded_dataset(contents, filename):
    if not filename.lower().endswith(".csv"):
        raise ValueError("Please upload a CSV file.")
    return load_dataset(io.BytesIO(contents))


def _period_start(years, period):
    latest = int(years.max())
    earliest = int(years.min())
    if period == "Day":
        return latest
    if period == "Month":
        return max(earliest, latest - 11)
    if period == "Year":
        return max(earliest, latest - 4)
    return earliest


def _pair_correlation(pair):
    if (
        len(pair) < 2
        or pair["x"].nunique() < 2
        or pair["y"].nunique() < 2
    ):
        return None

    correlation = pair["x"].corr(pair["y"])
    return float(correlation) if np.isfinite(correlation) else None


def _render_correlation_analysis(data):
    st.caption(
        "Explore relationships between recorded indicators. "
        "Correlation does not establish causation."
    )
    numeric_columns = list(VARIABLES.values())
    short_labels = [SHORT_LABELS[column] for column in numeric_columns]
    correlations = data[numeric_columns].corr()
    correlation_data = (
        correlations.rename_axis("Indicator")
        .reset_index()
        .melt(
            id_vars="Indicator",
            var_name="Other indicator",
            value_name="Correlation",
        )
    )
    label_lookup = dict(zip(numeric_columns, short_labels))
    correlation_data["Indicator"] = correlation_data["Indicator"].map(
        label_lookup
    )
    correlation_data["Other indicator"] = correlation_data[
        "Other indicator"
    ].map(label_lookup)
    correlation_data["HasCorrelation"] = np.isfinite(
        correlation_data["Correlation"]
    )
    correlation_data["CorrelationLabel"] = correlation_data[
        "Correlation"
    ].map(
        lambda value: f"{value:.2f}" if np.isfinite(value) else "—"
    )

    with st.container(border=True):
        title_column, palette_column = st.columns([1.6, 1])
        title_column.subheader("Correlation matrix", icon=":material/grid_on:")
        palette = palette_column.selectbox(
            "Heatmap colors",
            tuple(HEATMAP_PALETTES),
            key="heatmap_palette",
        )
        heatmap = (
            alt.Chart(correlation_data)
            .mark_rect()
            .encode(
                x=alt.X(
                    "Other indicator:N",
                    sort=short_labels,
                    title=None,
                    axis=alt.Axis(labelAngle=-40, labelOverlap=False),
                ),
                y=alt.Y("Indicator:N", sort=short_labels, title=None),
                color=alt.condition(
                    alt.datum.HasCorrelation,
                    alt.Color(
                        "Correlation:Q",
                        scale=alt.Scale(
                            domain=[-1, 1],
                            scheme=HEATMAP_PALETTES[palette],
                        ),
                        title="Pearson r",
                    ),
                    alt.value("#DFE7E3"),
                ),
                tooltip=[
                    "Indicator:N",
                    "Other indicator:N",
                    alt.Tooltip("Correlation:Q", format=".3f"),
                ],
            )
        )
        labels = (
            alt.Chart(correlation_data)
            .mark_text(fontSize=9)
            .encode(
                x=alt.X("Other indicator:N", sort=short_labels),
                y=alt.Y("Indicator:N", sort=short_labels),
                text=alt.Text("CorrelationLabel:N"),
                color=alt.condition(
                    alt.datum.HasCorrelation
                    & (
                        (alt.datum.Correlation > 0.6)
                        | (alt.datum.Correlation < -0.6)
                    ),
                    alt.value("#FFFFFF"),
                    alt.value("#263B33"),
                ),
            )
        )
        st.altair_chart(
            heatmap + labels,
            alt="Pairwise Pearson correlations between climate indicators",
            height=360,
        )

    with st.container(border=True):
        st.subheader("Relationship explorer", icon=":material/scatter_plot:")
        x_label, y_label = st.columns(2)
        x_name = x_label.selectbox(
            "X variable",
            list(VARIABLES),
            index=0,
            key="relationship_x",
        )
        y_name = y_label.selectbox(
            "Y variable",
            list(VARIABLES),
            index=2,
            key="relationship_y",
        )
        x_column, y_column = VARIABLES[x_name], VARIABLES[y_name]
        pair = pd.DataFrame(
            {"x": data[x_column], "y": data[y_column]}
        ).dropna()
        pair = pair[np.isfinite(pair.to_numpy(dtype=float)).all(axis=1)]

        correlation = _pair_correlation(pair)
        if correlation is None:
            if pair.empty:
                st.info(
                    "No comparison is available: there are no valid paired "
                    "observations for these indicators."
                )
            else:
                st.info(
                    "No comparison is available: at least two valid "
                    "observations with variation in both indicators are "
                    "required."
                )
        else:
            st.caption(
                f"Pearson r = {correlation:+.3f} · "
                f"valid paired records n = {len(pair):,}"
            )
            points = (
                alt.Chart(pair)
                .mark_circle(size=55, opacity=0.75, color="#0072B2")
                .encode(
                    x=alt.X("x:Q", title=SHORT_LABELS[x_column]),
                    y=alt.Y("y:Q", title=SHORT_LABELS[y_column]),
                    tooltip=[
                        alt.Tooltip(
                            "x:Q",
                            title=SHORT_LABELS[x_column],
                            format=".3f",
                        ),
                        alt.Tooltip(
                            "y:Q",
                            title=SHORT_LABELS[y_column],
                            format=".3f",
                        ),
                    ],
                )
            )
            chart = points
            if len(pair) >= 2 and pair["x"].std() > 0:
                regression = (
                    alt.Chart(pair)
                    .transform_regression("x", "y")
                    .mark_line(color="#D55E00", strokeWidth=2.5)
                    .encode(
                        x=alt.X("x:Q"),
                        y=alt.Y("y:Q"),
                    )
                )
                chart = points + regression
            st.altair_chart(
                chart,
                alt=f"{SHORT_LABELS[y_column]} versus {SHORT_LABELS[x_column]}",
            )


def _render_overview(data, period, source_name):
    st.title("ClimateLens", icon=":material/eco:")
    st.caption("A clearer view of our changing climate.")
    st.caption(
        f"Data source: {source_name} · "
        f"{data['Year'].min()}–{data['Year'].max()}"
    )

    metrics = (
        (
            "Average temperature",
            "Avg Temperature (°C)",
            "°C",
            1,
            ":material/device_thermostat:",
        ),
        (
            "CO₂ emissions / capita",
            "CO2 Emissions (Tons/Capita)",
            "t",
            2,
            ":material/co2:",
        ),
        (
            "Sea-level rise",
            "Sea Level Rise (mm)",
            "mm",
            2,
            ":material/water:",
        ),
        (
            "Renewable energy",
            "Renewable Energy (%)",
            "%",
            1,
            ":material/energy_savings_leaf:",
        ),
    )
    for column, (label, field, unit, decimals, icon) in zip(
        st.columns(4, gap="small"),
        metrics,
    ):
        value = safe_mean(data[field])
        rendered = (
            f"{value:,.{decimals}f} {unit}"
            if np.isfinite(value)
            else "N/A"
        )
        column.metric(label, rendered, icon=icon, border=True)

    st.header("Climate snapshot", icon=":material/monitoring:")
    annual = (
        data.groupby("Year", as_index=False)["Avg Temperature (°C)"]
        .mean()
        .rename(columns={"Avg Temperature (°C)": "Average temperature (°C)"})
    )
    trend_column, quality_column = st.columns([1.7, 1], gap="large")
    with trend_column.container(border=True):
        st.subheader(f"Annual temperature trend · {period}")
        st.caption("Mean temperature across selected countries and years.")
        if annual.empty:
            st.info("No temperature data is available for this selection.")
        else:
            temperature_trend = (
                alt.Chart(annual)
                .mark_line(
                    point=True,
                    color="#F0644D",
                    strokeWidth=3,
                )
                .encode(
                    x=alt.X(
                        "Year:Q",
                        title="Year",
                        axis=alt.Axis(format="d"),
                    ),
                    y=alt.Y(
                        "Average temperature (°C):Q",
                        title="Average temperature (°C)",
                    ),
                    tooltip=[
                        alt.Tooltip("Year:Q", format="d"),
                        alt.Tooltip(
                            "Average temperature (°C):Q",
                            format=".2f",
                        ),
                    ],
                )
            )
            st.altair_chart(
                temperature_trend,
                alt="Annual average temperature across selected countries",
                height=330,
            )
    with quality_column.container(border=True):
        st.subheader("Dataset health", icon=":material/health_and_safety:")
        st.metric("Records", f"{len(data):,}")
        st.metric("Countries", f"{data['Country'].nunique():,}")
        st.metric("Numeric completeness", f"{completeness(data):.1f}%")
        st.caption(
            f"{int(data.isna().any(axis=1).sum()):,} rows contain missing "
            f"values · {int(data.isna().sum().sum()):,} missing cells"
        )

    st.header("Country comparison", icon=":material/public:")
    with st.container(border=True):
        summary = country_summary(data)
        sort_options = {
            "Average temperature": "temperature",
            "CO₂ emissions per capita": "co2",
            "Sea-level rise": "sea_level",
            "Renewable energy": "renewable",
        }
        control_column, _ = st.columns([1, 2])
        sort_label = control_column.selectbox(
            "Sort countries by",
            list(sort_options),
            key="sort_by",
        )
        summary = summary.sort_values(
            sort_options[sort_label],
            ascending=False,
            na_position="last",
        )
        st.dataframe(
            summary.rename(
                columns={
                    "temperature": "Average temperature (°C)",
                    "co2": "CO₂ emissions (tons/capita)",
                    "sea_level": "Sea-level rise (mm)",
                    "renewable": "Renewable energy (%)",
                    "records": "Records",
                    "years": "Years",
                    "extreme": "Extreme weather events",
                    "forest": "Forest area (%)",
                }
            ),
            hide_index=True,
            alt="Country comparison of selected climate indicators",
        )
        st.download_button(
            "Download filtered data (CSV)",
            data=data.to_csv(index=False).encode("utf-8"),
            file_name="climatelens_export.csv",
            mime="text/csv",
            icon=":material/download:",
        )

    st.header("Explore relationships", icon=":material/query_stats:")
    _render_correlation_analysis(data)


def _render_findings(data, period):
    st.title("Research findings", icon=":material/description:")
    findings = build_findings(data, period)
    st.caption(findings["overview"])

    st.header("Research questions", icon=":material/lightbulb:")
    for question, result in findings["questions"]:
        with st.expander(question, icon=":material/chevron_right:"):
            st.write(result)

    st.header("Hypothesis tests", icon=":material/science:")
    for hypothesis, result in findings["hypotheses"]:
        with st.expander(hypothesis, icon=":material/chevron_right:"):
            st.write(result)
    st.caption(
        "Two-sided Pearson tests use alpha = 0.05. P-values are exploratory "
        "and do not adjust for repeated country/year observations or multiple "
        "tests; correlation does not establish causation."
    )


def main():
    st.set_page_config(
        page_title="ClimateLens · Data Studio",
        page_icon=":material/eco:",
        layout="wide",
    )

    st.sidebar.title("ClimateLens", icon=":material/eco:")
    st.sidebar.caption("CLIMATE DATA STUDIO")
    st.sidebar.caption(
        "Use the top-right app menu to choose System, Light, or Dark."
    )
    page = st.sidebar.radio(
        "Explore",
        ("Overview", "Research findings"),
        key="page",
        format_func=lambda value: (
            f":material/monitoring: {value}"
            if value == "Overview"
            else f":material/description: {value}"
        ),
    )

    upload = st.sidebar.file_uploader(
        "Load a climate CSV",
        type=["csv"],
        key="dataset_upload",
    )
    try:
        if upload is None:
            data = _load_bundled_dataset()
            source_name = DEFAULT_DATA.name
        else:
            data = _load_uploaded_dataset(upload.getvalue(), upload.name)
            source_name = upload.name
    except (
        OSError,
        UnicodeDecodeError,
        ValueError,
        pd.errors.ParserError,
    ) as error:
        st.error(f"Could not load the selected dataset: {error}")
        st.stop()

    years = data["Year"]
    periods = ("All", "Year", "Month", "Day")
    period = st.sidebar.segmented_control(
        "Time window",
        periods,
        default="All",
        required=True,
        key="period",
        width="stretch",
    )
    start_year = _period_start(years, period)
    filtered = data[data["Year"] >= start_year]

    countries = sorted(filtered["Country"].unique())
    selected_countries = st.sidebar.multiselect(
        "Countries",
        countries,
        default=countries,
        key="countries",
    )
    filtered = filtered[filtered["Country"].isin(selected_countries)]
    st.sidebar.caption(
        f"{len(filtered):,} records · {len(selected_countries):,} countries"
    )
    st.sidebar.link_button(
        "Climate data reference",
        SOURCE_URL,
        icon=":material/open_in_new:",
        width="stretch",
    )

    if filtered.empty:
        st.title("ClimateLens", icon=":material/eco:")
        st.info("No records match the selected time window and countries.")
        return

    if page == "Overview":
        _render_overview(filtered, period, source_name)
    else:
        _render_findings(filtered, period)


if __name__ == "__main__":
    main()
