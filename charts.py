import numpy as np

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import styles as S


class ClimateChart:

    def __init__(self, parent):

        self.fig = Figure(
            figsize=(7.2, 3.2),
            dpi=100,
            facecolor=S.WHITE
        )

        self.ax = self.fig.add_subplot(111)

        self.fig.subplots_adjust(
            left=0.08,
            right=0.98,
            top=0.94,
            bottom=0.19
        )

        self.canvas = FigureCanvasTkAgg(
            self.fig,
            master=parent
        )

        self.widget = self.canvas.get_tk_widget()

        self.widget.configure(
            highlightthickness=0,
            background=S.WHITE
        )

    def draw(self, years, values, period_label):

        self.ax.clear()
        self.ax.set_facecolor(S.WHITE)

        if len(years):

            years = np.asarray(years)
            values = np.asarray(values, dtype=float)

            valid = np.isfinite(values)

            years = years[valid]
            values = values[valid]

            if len(years):

                self.ax.plot(
                    years,
                    values,
                    color=S.CORAL,
                    linewidth=2.4
                )

                baseline = np.nanmin(values)

                self.ax.fill_between(
                    years,
                    values,
                    baseline,
                    color=S.CORAL,
                    alpha=0.12
                )

                self.ax.set_xlim(
                    min(years),
                    max(years) if max(years) > min(years)
                    else min(years) + 1
                )

                self.ax.set_xticks(
                    years if len(years) <= 12
                    else years[::max(1, len(years) // 8)]
                )

            else:

                self.ax.text(
                    0.5,
                    0.5,
                    "No numeric data for this period",
                    ha="center",
                    va="center",
                    transform=self.ax.transAxes,
                    color=S.MUTED
                )

        else:

            self.ax.text(
                0.5,
                0.5,
                "No data available",
                ha="center",
                va="center",
                transform=self.ax.transAxes,
                color=S.MUTED
            )

        self.ax.grid(
            axis="y",
            linestyle=(0, (2, 3)),
            linewidth=0.7,
            color=S.BORDER
        )

        self.ax.spines["top"].set_visible(False)
        self.ax.spines["right"].set_visible(False)
        self.ax.spines["left"].set_visible(False)

        self.ax.spines["bottom"].set_color(S.BORDER)

        self.ax.tick_params(
            axis="both",
            colors=S.MUTED,
            labelsize=8,
            length=0,
            pad=8
        )

        self.ax.set_ylabel(
            "Average temperature (°C)",
            color=S.MUTED,
            fontsize=8
        )

        self.ax.set_title(
            f"Annual average · {period_label}",
            loc="left",
            fontsize=9,
            color=S.TEXT,
            pad=8
        )

        self.canvas.draw_idle()