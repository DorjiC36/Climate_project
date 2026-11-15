import numpy as np
from tkinter import filedialog, messagebox, simpledialog

from calculations import (
    annual_series,
    completeness,
    country_summary,
    safe_mean,
)
from data_manager import export_csv
import styles as S


class DashboardActionsMixin:

    def toggle_theme(self):

        self.period = self.range_var.get()
        active_page = self.active_page

        correlation = self.correlation_section
        correlation_state = (
            correlation.heatmap_palette_var.get(),
            correlation.x_var.get(),
            correlation.y_var.get()
        )

        S.set_dark_mode(not S.DARK_MODE)
        self.canvas.unbind_all("<MouseWheel>")

        for widget in self.root.winfo_children():
            widget.destroy()

        self._style()
        self._build()

        self.correlation_section.heatmap_palette_var.set(
            correlation_state[0]
        )
        self.correlation_section.x_var.set(correlation_state[1])
        self.correlation_section.y_var.set(correlation_state[2])

        if active_page == "findings":
            self.show_findings()

        self.refresh()

    def on_period(self):

        self.period = self.range_var.get()
        self.refresh()


    def refresh(self):

        df = self.df

        years = df["Year"].to_numpy(dtype=int)

        maxyear = int(np.max(years))
        minyear = int(np.min(years))

        if self.period == "Day":
            start = maxyear
        elif self.period == "Month":
            start = max(years.min(), maxyear - 11)
        elif self.period == "Year":
            start = max(minyear, maxyear - 4)
        else:
            start = minyear

        view = df[
            df["Year"] >= start
        ].copy()

        self.filtered = view

        ys, vals = annual_series(
            view,
            "Avg Temperature (°C)"
        )

        self.chart.draw(
            ys,
            vals,
            self.period
        )

        # UPDATE CORRELATION ANALYSIS

        self.correlation_section.update(view)
        self.findings_section.update(view, self.period)

        # SUMMARY CARDS

        metrics = [

            (
                "AVG TEMPERATURE",
                f"{safe_mean(view['Avg Temperature (°C)']):.1f}°C",
                "Mean across country-year records"
            ),

            (
                "CO₂ EMISSIONS / CAPITA",
                f"{safe_mean(view['CO2 Emissions (Tons/Capita)']):.2f} t",
                "Mean tons per capita"
            ),

            (
                "SEA LEVEL RISE",
                f"{safe_mean(view['Sea Level Rise (mm)']):.2f} mm",
                "Mean recorded value"
            ),

            (
                "RENEWABLE ENERGY",
                f"{safe_mean(view['Renewable Energy (%)']):.1f}%",
                "Mean renewable energy share"
            )
        ]

        for (lab, val, desc), (l, v, d) in zip(
            metrics,
            self.metric_cards
        ):

            l.config(text=lab)
            v.config(text=val)
            d.config(text=desc)

        # REGIONAL INDICATORS

        cols = [
            ("Avg Temperature (°C)", S.CORAL),
            ("CO2 Emissions (Tons/Capita)", S.GOLD),
            ("Sea Level Rise (mm)", S.MINT),
            ("Renewable Energy (%)", S.BLUE)
        ]

        for (col, color), (val, bar, _bar_color) in zip(
            cols,
            self.region_rows
        ):

            m = safe_mean(view[col])

            arr = view[col].to_numpy(dtype=float)

            finite = arr[np.isfinite(arr)]

            maxv = (
                float(np.max(finite))
                if finite.size
                else 1
            )

            val.config(
                text=f"{m:.2f}" if np.isfinite(m) else "N/A"
            )

            bar["value"] = min(
                100,
                max(0, (m / maxv * 100 if maxv else 0))
            )

            style_name = {
                S.CORAL: "coral",
                S.GOLD: "gold",
                S.MINT: "mint",
                S.BLUE: "blue"
            }.get(color, "Horizontal")

            bar.configure(
                style=f"{style_name}.Horizontal.TProgressbar"
            )

        # DATA QUALITY

        quality = completeness(df)

        self.side_records.config(
            text=(
                f"{len(df):,} records · "
                f"{df['Year'].min()}–{df['Year'].max()}"
            )
        )

        self.side_progress["value"] = quality

        self.side_quality.config(
            text=f"Numeric completeness {quality:.1f}%"
        )

        self.quality_label.config(
            text=f"{quality:.1f}% numeric completeness"
        )

        self.quality_bar["value"] = quality

        self.health_records.config(
            text=(
                f"{len(df):,} rows · "
                f"{df['Country'].nunique()} countries"
            )
        )

        missing = int(
            df.isna().sum().sum()
        )

        self.health_stats.config(
            text=(
                f"Rows with missing values: "
                f"{int(df.isna().any(axis=1).sum())}\n"
                f"Missing cells: {missing}\n"
                f"Year range: {df['Year'].min()}–{df['Year'].max()}"
            )
        )

        self.populate_table(view)


    def populate_table(self, df):

        for item in self.tree.get_children():
            self.tree.delete(item)

        summary = country_summary(df).sort_values(
            "temperature",
            ascending=self._table_sort_ascending
        )

        for _, r in summary.iterrows():

            self.tree.insert(
                "",
                "end",
                values=(
                    r["Country"],
                    f'{r["temperature"]:.1f}',
                    f'{r["co2"]:.2f}',
                    f'{r["sea_level"]:.2f}',
                    f'{r["renewable"]:.1f}'
                )
            )


    def export(self):

        path = filedialog.asksaveasfilename(
            title="Export displayed climate data",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile="climatelens_export.csv"
        )

        if path:

            try:

                export_csv(
                    self.filtered,
                    path
                )

                messagebox.showinfo(
                    "Export complete",
                    f"Exported {len(self.filtered):,} records to:\n{path}"
                )

            except Exception as e:

                messagebox.showerror(
                    "Export failed",
                    str(e)
                )


    def filter_country(self):

        country = simpledialog.askstring(
            "Filter country",
            "Enter a country name (leave blank to show all):",
            parent=self.root
        )

        if country is None:
            return

        if not country.strip():

            self.populate_table(self.filtered)
            return

        mask = self.filtered["Country"].str.contains(
            country.strip(),
            case=False,
            na=False
        )

        result = self.filtered[mask]

        if result.empty:

            messagebox.showinfo(
                "No matches",
                f"No country matching “{country}”."
            )

            return

        self.populate_table(result)


    def sort_table(self):

        self._table_sort_ascending = not self._table_sort_ascending
        self.populate_table(self.filtered)
