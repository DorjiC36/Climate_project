import tkinter as tk
from tkinter import ttk

import numpy as np

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import styles as S


VARIABLES = {

    "Average temperature (°C)":
        "Avg Temperature (°C)",

    "CO₂ emissions (tons/capita)":
        "CO2 Emissions (Tons/Capita)",

    "Sea level rise (mm)":
        "Sea Level Rise (mm)",

    "Rainfall (mm)":
        "Rainfall (mm)",

    "Population":
        "Population",

    "Renewable energy (%)":
        "Renewable Energy (%)",

    "Extreme weather events":
        "Extreme Weather Events",

    "Forest area (%)":
        "Forest Area (%)"
}


SHORT = {

    "Avg Temperature (°C)": "Temp",

    "CO2 Emissions (Tons/Capita)": "CO₂",

    "Sea Level Rise (mm)": "Sea level",

    "Rainfall (mm)": "Rainfall",

    "Population": "Population",

    "Renewable Energy (%)": "Renewables",

    "Extreme Weather Events": "Extreme events",

    "Forest Area (%)": "Forest"
}


def pairwise_corr(x, y):

    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)

    valid = np.isfinite(x) & np.isfinite(y)

    x = x[valid]
    y = y[valid]

    if (
        len(x) < 2
        or np.std(x) == 0
        or np.std(y) == 0
    ):

        return float("nan"), int(len(x))

    correlation = np.corrcoef(x, y)[0, 1]

    return float(correlation), int(len(x))


class CorrelationSection:

    def __init__(self, parent, on_pair_change=None):

        self.parent = parent
        self.on_pair_change = on_pair_change

        self.frame = tk.Frame(
            parent,
            bg=S.BG
        )

        self.frame.pack(
            fill="x",
            pady=(0, 16)
        )

        header = tk.Frame(
            self.frame,
            bg=S.BG
        )

        header.pack(
            fill="x",
            pady=(0, 10)
        )

        tk.Label(
            header,
            text="Climate correlation analysis",
            bg=S.BG,
            fg=S.TEXT,
            font=(S.FONT, 15, "bold")
        ).pack(anchor="w")

        tk.Label(
            header,
            text=(
                "Explore statistical relationships between "
                "recorded climate indicators. "
                "Correlation does not establish causation."
            ),
            bg=S.BG,
            fg=S.MUTED,
            font=(S.FONT, 9)
        ).pack(
            anchor="w",
            pady=(4, 0)
        )

        body = tk.Frame(
            self.frame,
            bg=S.BG
        )

        body.pack(fill="x")

        # CORRELATION HEATMAP

        self.heat_card = tk.Frame(
            body,
            bg=S.WHITE,
            highlightbackground=S.BORDER,
            highlightthickness=1
        )

        self.heat_card.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 12)
        )

        tk.Label(
            self.heat_card,
            text="Correlation matrix",
            bg=S.WHITE,
            fg=S.TEXT,
            font=(S.FONT, 11, "bold")
        ).pack(
            anchor="w",
            padx=16,
            pady=(14, 0)
        )

        tk.Label(
            self.heat_card,
            text="Pearson correlation coefficient (r)",
            bg=S.WHITE,
            fg=S.MUTED,
            font=(S.FONT, 8)
        ).pack(
            anchor="w",
            padx=16,
            pady=(3, 0)
        )

        self.heat_fig = Figure(
            figsize=(6.0, 4.3),
            dpi=95,
            facecolor=S.WHITE
        )

        self.heat_ax = self.heat_fig.add_subplot(111)

        self.heat_fig.subplots_adjust(
            left=0.24,
            right=0.98,
            top=0.94,
            bottom=0.23
        )

        self.heat_canvas = FigureCanvasTkAgg(
            self.heat_fig,
            master=self.heat_card
        )

        self.heat_canvas.get_tk_widget().pack(
            fill="both",
            expand=True,
            padx=8,
            pady=6
        )

        # RELATIONSHIP EXPLORER

        self.pair_card = tk.Frame(
            body,
            bg=S.WHITE,
            highlightbackground=S.BORDER,
            highlightthickness=1
        )

        self.pair_card.pack(
            side="right",
            fill="both",
            expand=True
        )

        tk.Label(
            self.pair_card,
            text="Relationship explorer",
            bg=S.WHITE,
            fg=S.TEXT,
            font=(S.FONT, 11, "bold")
        ).pack(
            anchor="w",
            padx=16,
            pady=(14, 0)
        )

        controls = tk.Frame(
            self.pair_card,
            bg=S.WHITE
        )

        controls.pack(
            fill="x",
            padx=14,
            pady=(8, 0)
        )

        options = list(VARIABLES.keys())

        self.x_var = tk.StringVar(
            value="Average temperature (°C)"
        )

        self.y_var = tk.StringVar(
            value="Sea level rise (mm)"
        )

        tk.Label(
            controls,
            text="X",
            bg=S.WHITE,
            fg=S.MUTED,
            font=(S.FONT, 8, "bold")
        ).pack(side="left")

        self.x_combo = ttk.Combobox(
            controls,
            textvariable=self.x_var,
            values=options,
            state="readonly",
            width=22
        )

        self.x_combo.pack(
            side="left",
            padx=(5, 10)
        )

        tk.Label(
            controls,
            text="Y",
            bg=S.WHITE,
            fg=S.MUTED,
            font=(S.FONT, 8, "bold")
        ).pack(side="left")

        self.y_combo = ttk.Combobox(
            controls,
            textvariable=self.y_var,
            values=options,
            state="readonly",
            width=22
        )

        self.y_combo.pack(
            side="left",
            padx=(5, 0)
        )

        self.x_combo.bind(
            "<<ComboboxSelected>>",
            self._selection_changed
        )

        self.y_combo.bind(
            "<<ComboboxSelected>>",
            self._selection_changed
        )

        self.pair_fig = Figure(
            figsize=(6.0, 3.55),
            dpi=95,
            facecolor=S.WHITE
        )

        self.pair_ax = self.pair_fig.add_subplot(111)

        self.pair_fig.subplots_adjust(
            left=0.12,
            right=0.97,
            top=0.91,
            bottom=0.17
        )

        self.pair_canvas = FigureCanvasTkAgg(
            self.pair_fig,
            master=self.pair_card
        )

        self.pair_canvas.get_tk_widget().pack(
            fill="both",
            expand=True,
            padx=8,
            pady=(0, 0)
        )

        self.result = tk.Label(
            self.pair_card,
            text="Choose two variables to inspect their relationship.",
            bg=S.WHITE,
            fg=S.TEXT,
            font=(S.FONT, 9, "bold")
        )

        self.result.pack(
            anchor="w",
            padx=16,
            pady=(0, 13)
        )

        self.df = None

    def _selection_changed(self, event=None):

        if self.df is not None:
            self.draw_pair(self.df)

    def update(self, df):

        self.df = df.copy()

        self.draw_heatmap(self.df)

        self.draw_pair(self.df)

    def draw_heatmap(self, df):

        columns = list(VARIABLES.values())

        labels = [
            SHORT[c] for c in columns
        ]

        matrix = np.full(
            (len(columns), len(columns)),
            np.nan,
            dtype=float
        )

        for i, col1 in enumerate(columns):

            for j, col2 in enumerate(columns):

                x = df[col1].to_numpy(dtype=float)
                y = df[col2].to_numpy(dtype=float)

                r, n = pairwise_corr(x, y)

                matrix[i, j] = r

        self.heat_ax.clear()

        self.heat_ax.set_facecolor(S.WHITE)

        im = self.heat_ax.imshow(
            matrix,
            cmap="RdYlBu_r",
            vmin=-1,
            vmax=1,
            aspect="auto"
        )

        self.heat_ax.set_xticks(
            range(len(labels)),
            labels=labels,
            rotation=42,
            ha="right",
            fontsize=7
        )

        self.heat_ax.set_yticks(
            range(len(labels)),
            labels=labels,
            fontsize=7
        )

        for i in range(len(labels)):

            for j in range(len(labels)):

                value = matrix[i, j]

                label = (
                    f"{value:.2f}"
                    if np.isfinite(value)
                    else "N/A"
                )

                self.heat_ax.text(
                    j,
                    i,
                    label,
                    ha="center",
                    va="center",
                    fontsize=6.5,
                    color=(
                        "#183F34"
                        if not np.isfinite(value)
                        or abs(value) < 0.62
                        else "white"
                    )
                )

        self.heat_ax.set_title(
            "Pairwise Pearson r",
            loc="left",
            color=S.TEXT,
            fontsize=8,
            pad=6
        )

        for spine in self.heat_ax.spines.values():
            spine.set_visible(False)

        if hasattr(self, "heat_colorbar"):

            try:
                self.heat_colorbar.remove()
            except Exception:
                pass

        self.heat_colorbar = self.heat_fig.colorbar(
            im,
            ax=self.heat_ax,
            fraction=0.046,
            pad=0.04
        )

        self.heat_colorbar.ax.tick_params(
            labelsize=7,
            colors=S.MUTED
        )

        self.heat_canvas.draw_idle()

    def draw_pair(self, df):

        xcol = VARIABLES[self.x_var.get()]
        ycol = VARIABLES[self.y_var.get()]

        x = df[xcol].to_numpy(dtype=float)
        y = df[ycol].to_numpy(dtype=float)

        valid = np.isfinite(x) & np.isfinite(y)

        x = x[valid]
        y = y[valid]

        r, n = pairwise_corr(x, y)

        self.pair_ax.clear()

        self.pair_ax.set_facecolor(S.WHITE)

        if n:

            self.pair_ax.scatter(
                x,
                y,
                s=14,
                alpha=0.48,
                color=S.BLUE,
                edgecolors="none"
            )

            if n >= 2 and np.std(x) > 0:

                slope, intercept = np.polyfit(
                    x,
                    y,
                    1
                )

                line_x = np.linspace(
                    np.min(x),
                    np.max(x),
                    100
                )

                self.pair_ax.plot(
                    line_x,
                    slope * line_x + intercept,
                    color=S.CORAL,
                    linewidth=2
                )

        self.pair_ax.grid(
            axis="both",
            linestyle=(0, (2, 3)),
            linewidth=0.6,
            color=S.BORDER
        )

        self.pair_ax.spines["top"].set_visible(False)
        self.pair_ax.spines["right"].set_visible(False)

        self.pair_ax.spines["left"].set_color(S.BORDER)
        self.pair_ax.spines["bottom"].set_color(S.BORDER)

        self.pair_ax.tick_params(
            labelsize=7,
            colors=S.MUTED,
            length=0
        )

        self.pair_ax.set_xlabel(
            SHORT[xcol],
            color=S.MUTED,
            fontsize=8
        )

        self.pair_ax.set_ylabel(
            SHORT[ycol],
            color=S.MUTED,
            fontsize=8
        )

        self.pair_ax.set_title(
            "Country-year observations",
            loc="left",
            color=S.TEXT,
            fontsize=8
        )

        self.pair_canvas.draw_idle()

        if np.isfinite(r):

            strength = (
                "very strong" if abs(r) >= 0.8
                else "strong" if abs(r) >= 0.6
                else "moderate" if abs(r) >= 0.4
                else "weak" if abs(r) >= 0.2
                else "very weak"
            )

            direction = (
                "positive" if r > 0
                else "negative" if r < 0
                else "near-zero"
            )

            self.result.config(
                text=(
                    f"Pearson r = {r:+.3f}  ·  "
                    f"{strength} {direction} linear association  ·  "
                    f"n = {n:,}"
                )
            )

        else:

            self.result.config(
                text=(
                    "Pearson r unavailable for these data  ·  "
                    f"valid paired records n = {n:,}"
                )
            )