import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import numpy as np
import webbrowser
from pathlib import Path

from data_manager import (
    load_dataset,
    export_csv,
    DEFAULT_DATA
)

from calculations import (
    safe_mean,
    completeness,
    annual_series,
    country_summary
)

from charts import ClimateChart
from correlation_analysis import CorrelationSection

import styles as S


SOURCE_URL = "https://climateknowledgeportal.worldbank.org/"


class ClimateLensApp:

    def __init__(self, root):

        self.root = root

        self.root.title("ClimateLens – Data Studio")
        self.root.geometry("1450x920")
        self.root.minsize(1120, 740)

        self.df = load_dataset()

        self.period = "All"
        self.filtered = self.df.copy()

        self._style()
        self._build()
        self.refresh()

    def _style(self):

        self.root.configure(bg=S.BG)

        style = ttk.Style()

        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(
            "Treeview",
            background=S.WHITE,
            fieldbackground=S.WHITE,
            foreground=S.TEXT,
            rowheight=34,
            borderwidth=0,
            font=(S.FONT, 9)
        )

        style.configure(
            "Treeview.Heading",
            background=S.WHITE,
            foreground=S.MUTED,
            font=(S.FONT, 8, "bold"),
            relief="flat"
        )

        style.map(
            "Treeview",
            background=[("selected", "#DDEFE5")],
            foreground=[("selected", S.TEXT)]
        )

        style.configure(
            "Horizontal.TProgressbar",
            troughcolor="#DDE4DE",
            background=S.MINT,
            bordercolor="#DDE4DE"
        )

        for name, color in [
            ("coral", S.CORAL),
            ("gold", S.GOLD),
            ("mint", S.MINT),
            ("blue", S.BLUE)
        ]:

            style.configure(
                f"{name}.Horizontal.TProgressbar",
                troughcolor="#41675B",
                background=color,
                bordercolor="#41675B"
            )

    def _build(self):

        # SIDEBAR

        self.sidebar = tk.Frame(
            self.root,
            bg=S.SIDEBAR,
            width=220
        )

        self.sidebar.pack(
            side="left",
            fill="y"
        )

        self.sidebar.pack_propagate(False)

        brand = tk.Frame(
            self.sidebar,
            bg=S.SIDEBAR
        )

        brand.pack(
            fill="x",
            padx=22,
            pady=(22, 32)
        )

        tk.Label(
            brand,
            text="♧",
            bg=S.MINT,
            fg=S.TEXT,
            font=(S.FONT, 18, "bold"),
            width=2
        ).pack(
            side="left",
            padx=(0, 10)
        )

        btxt = tk.Frame(
            brand,
            bg=S.SIDEBAR
        )

        btxt.pack(side="left")

        tk.Label(
            btxt,
            text="climatelens",
            bg=S.SIDEBAR,
            fg="white",
            font=(S.FONT, 14, "bold")
        ).pack(anchor="w")

        tk.Label(
            btxt,
            text="D A T A   S T U D I O",
            bg=S.SIDEBAR,
            fg=S.MUTED,
            font=(S.FONT, 7)
        ).pack(anchor="w")

        tk.Label(
            self.sidebar,
            text="E X P L O R E",
            bg=S.SIDEBAR,
            fg="#6D9A8B",
            font=(S.FONT, 8, "bold")
        ).pack(
            anchor="w",
            padx=26
        )

        self.nav_label = tk.Label(
            self.sidebar,
            text="▦   Overview        ●",
            bg=S.SIDEBAR_HI,
            fg="white",
            font=(S.FONT, 10, "bold"),
            anchor="w",
            padx=14,
            pady=12
        )

        self.nav_label.pack(
            fill="x",
            padx=14,
            pady=(10, 24)
        )

        tk.Label(
            self.sidebar,
            text="W O R K S P A C E",
            bg=S.SIDEBAR,
            fg="#6D9A8B",
            font=(S.FONT, 8, "bold")
        ).pack(
            anchor="w",
            padx=26
        )

        for label, cmd in [
            ("◎   Datasets", self.manage_sources),
            ("☷   Settings", self.settings_dialog)
        ]:

            tk.Button(
                self.sidebar,
                text=label,
                command=cmd,
                bg=S.SIDEBAR,
                fg="#AFC5BE",
                activebackground=S.SIDEBAR_HI,
                activeforeground="white",
                relief="flat",
                anchor="w",
                padx=26,
                pady=10,
                font=(S.FONT, 10),
                cursor="hand2"
            ).pack(
                fill="x",
                pady=1
            )

        # DATASET STATUS CARD

        self.status_card = tk.Frame(
            self.sidebar,
            bg="#2B5045",
            highlightbackground="#41675B",
            highlightthickness=1
        )

        self.status_card.pack(
            side="bottom",
            fill="x",
            padx=15,
            pady=16
        )

        tk.Label(
            self.status_card,
            text="◉   SAMPLE DATA",
            bg="#2B5045",
            fg=S.MINT,
            font=(S.FONT, 8, "bold")
        ).pack(
            anchor="w",
            padx=14,
            pady=(14, 8)
        )

        tk.Label(
            self.status_card,
            text="climate_change_dataset.csv",
            bg="#2B5045",
            fg="white",
            font=(S.FONT, 9, "bold"),
            wraplength=190
        ).pack(
            anchor="w",
            padx=14
        )

        self.side_records = tk.Label(
            self.status_card,
            text="",
            bg="#2B5045",
            fg=S.MUTED,
            font=(S.FONT, 8)
        )

        self.side_records.pack(
            anchor="w",
            padx=14,
            pady=6
        )

        self.side_progress = ttk.Progressbar(
            self.status_card,
            maximum=100,
            length=170
        )

        self.side_progress.pack(
            padx=14,
            pady=4
        )

        self.side_quality = tk.Label(
            self.status_card,
            text="",
            bg="#2B5045",
            fg=S.MINT,
            font=(S.FONT, 8)
        )

        self.side_quality.pack(
            anchor="w",
            padx=14,
            pady=(2, 14)
        )

        # SCROLLABLE MAIN CONTENT

        outer = tk.Frame(
            self.root,
            bg=S.BG
        )

        outer.pack(
            side="left",
            fill="both",
            expand=True
        )

        self.canvas = tk.Canvas(
            outer,
            bg=S.BG,
            highlightthickness=0
        )

        scrollbar = ttk.Scrollbar(
            outer,
            orient="vertical",
            command=self.canvas.yview
        )

        self.canvas.configure(
            yscrollcommand=scrollbar.set
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        self.canvas.pack(
            side="left",
            fill="both",
            expand=True
        )

        self.content = tk.Frame(
            self.canvas,
            bg=S.BG
        )

        self.content_id = self.canvas.create_window(
            (0, 0),
            window=self.content,
            anchor="nw"
        )

        self.content.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.bind(
            "<Configure>",
            lambda e: self.canvas.itemconfigure(
                self.content_id,
                width=e.width
            )
        )

        self.canvas.bind_all(
            "<MouseWheel>",
            lambda e: self.canvas.yview_scroll(
                int(-e.delta / 120),
                "units"
            )
        )

        pad = tk.Frame(
            self.content,
            bg=S.BG
        )

        pad.pack(
            fill="both",
            expand=True,
            padx=34,
            pady=26
        )

        # HEADER

        head = tk.Frame(
            pad,
            bg=S.BG
        )

        head.pack(
            fill="x",
            pady=(0, 22)
        )

        left = tk.Frame(
            head,
            bg=S.BG
        )

        left.pack(
            side="left",
            fill="x",
            expand=True
        )

        tk.Label(
            left,
            text="•  R E S E A R C H  D A S H B O A R D",
            bg=S.BG,
            fg=S.CORAL,
            font=(S.FONT, 8, "bold")
        ).pack(anchor="w")

        tk.Label(
            left,
            text="The planet is telling\nus something.",
            bg=S.BG,
            fg=S.TEXT,
            font=(S.FONT, 30, "bold"),
            justify="left"
        ).pack(
            anchor="w",
            pady=(8, 8)
        )

        tk.Label(
            left,
            text=(
                "Explore the signals behind our changing climate, "
                "grounded in the\nuploaded dataset and its recorded "
                "country-year observations."
            ),
            bg=S.BG,
            fg=S.MUTED,
            font=(S.FONT, 10),
            justify="left"
        ).pack(anchor="w")

        tools = tk.Frame(
            head,
            bg=S.BG
        )

        tools.pack(
            side="right",
            anchor="s",
            pady=(0, 4)
        )

        self.range_var = tk.StringVar(value="All")

        view_selector = ttk.Combobox(
            tools,
            textvariable=self.range_var,
            values=[
                "Day",
                "Month",
                "Year",
                "All"
            ],
            state="readonly",
            width=12
        )

        view_selector.pack(
            side="left",
            ipady=5,
            padx=(0, 8)
        )

        self.range_var.trace_add(
            "write",
            lambda *_: self.on_period()
        )

        tk.Button(
            tools,
            text="↓  Export CSV",
            command=self.export,
            bg=S.SIDEBAR,
            fg="white",
            activebackground=S.SIDEBAR_HI,
            relief="flat",
            font=(S.FONT, 9, "bold"),
            padx=13,
            pady=9,
            cursor="hand2"
        ).pack(side="left")

        # FOUR CLIMATE METRIC CARDS

        self.metric_frame = tk.Frame(
            pad,
            bg=S.BG
        )

        self.metric_frame.pack(
            fill="x",
            pady=(0, 14)
        )

        self.metric_cards = []

        for i in range(4):

            card = tk.Frame(
                self.metric_frame,
                bg=S.WHITE,
                highlightbackground=S.BORDER,
                highlightthickness=1
            )

            card.grid(
                row=0,
                column=i,
                sticky="nsew",
                padx=(0 if i == 0 else 10, 0),
                ipady=5
            )

            self.metric_frame.grid_columnconfigure(
                i,
                weight=1,
                uniform="metric"
            )

            label = tk.Label(
                card,
                text="",
                bg=S.WHITE,
                fg=S.MUTED,
                font=(S.FONT, 8, "bold")
            )

            label.pack(
                anchor="w",
                padx=16,
                pady=(17, 8)
            )

            value = tk.Label(
                card,
                text="",
                bg=S.WHITE,
                fg=S.TEXT,
                font=(S.FONT, 19, "bold")
            )

            value.pack(
                anchor="w",
                padx=16
            )

            desc = tk.Label(
                card,
                text="",
                bg=S.WHITE,
                fg=S.MUTED,
                font=(S.FONT, 8)
            )

            desc.pack(
                anchor="w",
                padx=16,
                pady=(5, 15)
            )

            self.metric_cards.append(
                (label, value, desc)
            )

        # MAIN CHART AND REGIONAL CARD

        mainrow = tk.Frame(
            pad,
            bg=S.BG
        )

        mainrow.pack(
            fill="x",
            pady=(0, 16)
        )

        chartcard = tk.Frame(
            mainrow,
            bg=S.WHITE,
            highlightbackground=S.BORDER,
            highlightthickness=1,
            height=390
        )

        chartcard.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 12)
        )
        chartcard.pack_propagate(False)

        charthead = tk.Frame(
            chartcard,
            bg=S.WHITE
        )

        charthead.pack(
            fill="x",
            padx=18,
            pady=(15, 0)
        )

        tk.Label(
            charthead,
            text="Global temperature trend",
            bg=S.WHITE,
            fg=S.TEXT,
            font=(S.FONT, 12, "bold")
        ).pack(anchor="w")

        tk.Label(
            charthead,
            text=(
                "Annual mean of Avg Temperature (°C) · "
                "grouped across countries"
            ),
            bg=S.WHITE,
            fg=S.MUTED,
            font=(S.FONT, 8)
        ).pack(
            anchor="w",
            pady=(4, 0)
        )

        self.chart = ClimateChart(chartcard)

        self.chart.widget.pack(
            fill="both",
            expand=True,
            padx=12,
            pady=4
        )

        legend = tk.Frame(
            chartcard,
            bg=S.WHITE
        )

        legend.pack(
            fill="x",
            padx=18,
            pady=(0, 13)
        )

        tk.Label(
            legend,
            text="●",
            fg=S.CORAL,
            bg=S.WHITE
        ).pack(side="left")

        tk.Label(
            legend,
            text="Annual average temperature",
            fg=S.MUTED,
            bg=S.WHITE,
            font=(S.FONT, 8)
        ).pack(
            side="left",
            padx=4
        )

        tk.Button(
            legend,
            text="View dataset ↗",
            command=lambda: webbrowser.open(SOURCE_URL),
            bg=S.WHITE,
            fg=S.TEXT,
            relief="flat",
            font=(S.FONT, 8, "bold")
        ).pack(side="right")

        # REGIONAL INDICATORS

        region = tk.Frame(
            mainrow,
            bg=S.SIDEBAR,
            highlightbackground=S.SIDEBAR,
            highlightthickness=1,
            width=370,
            height=390
        )

        region.pack(
            side="right",
            fill="y"
        )

        region.pack_propagate(False)

        tk.Label(
            region,
            text="Where climate indicators\nare changing",
            bg=S.SIDEBAR,
            fg="white",
            font=(S.FONT, 18, "bold"),
            justify="left"
        ).pack(
            anchor="w",
            padx=18,
            pady=(18, 7)
        )

        tk.Label(
            region,
            text="Country averages from the loaded dataset.",
            bg=S.SIDEBAR,
            fg="#AFC5BE",
            font=(S.FONT, 8),
            wraplength=330
        ).pack(
            anchor="w",
            padx=18,
            pady=(0, 15)
        )

        self.region_rows = []

        for name, color in [
            ("Temperature", S.CORAL),
            ("CO₂ per capita", S.GOLD),
            ("Sea level rise", S.MINT),
            ("Renewable energy", S.BLUE)
        ]:

            box = tk.Frame(
                region,
                bg=S.SIDEBAR
            )

            box.pack(
                fill="x",
                padx=18,
                pady=7
            )

            top = tk.Frame(
                box,
                bg=S.SIDEBAR
            )

            top.pack(fill="x")

            tk.Label(
                top,
                text=name,
                bg=S.SIDEBAR,
                fg="#D7E4DE",
                font=(S.FONT, 8)
            ).pack(side="left")

            val = tk.Label(
                top,
                text="—",
                bg=S.SIDEBAR,
                fg="white",
                font=(S.FONT, 8, "bold")
            )

            val.pack(side="right")

            bar = ttk.Progressbar(
                box,
                maximum=100,
                length=220
            )

            bar.pack(
                fill="x",
                pady=(6, 0)
            )

            self.region_rows.append(
                (val, bar, color)
            )

        tk.Button(
            region,
            text="Explore country data ↗",
            command=self.country_dialog,
            bg=S.SIDEBAR,
            fg="white",
            activebackground=S.SIDEBAR_HI,
            relief="solid",
            bd=1,
            highlightbackground="#42665B",
            font=(S.FONT, 9, "bold"),
            pady=8
        ).pack(
            fill="x",
            padx=18,
            pady=(17, 16)
        )

        # COUNTRY SNAPSHOT TABLE

        bottom = tk.Frame(
            pad,
            bg=S.BG
        )

        bottom.pack(
            fill="both",
            expand=True
        )

        tablecard = tk.Frame(
            bottom,
            bg=S.WHITE,
            highlightbackground=S.BORDER,
            highlightthickness=1
        )

        tablecard.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 12)
        )

        ttop = tk.Frame(
            tablecard,
            bg=S.WHITE
        )

        ttop.pack(
            fill="x",
            padx=18,
            pady=(15, 8)
        )

        tk.Label(
            ttop,
            text="Country snapshot",
            bg=S.WHITE,
            fg=S.TEXT,
            font=(S.FONT, 12, "bold")
        ).pack(anchor="w")

        tk.Label(
            ttop,
            text="Average indicators across available years",
            bg=S.WHITE,
            fg=S.MUTED,
            font=(S.FONT, 8)
        ).pack(
            anchor="w",
            pady=(3, 8)
        )

        controls = tk.Frame(
            ttop,
            bg=S.WHITE
        )

        controls.pack(fill="x")

        tk.Button(
            controls,
            text="Filter country",
            command=self.filter_country,
            bg=S.WHITE,
            fg=S.TEXT,
            relief="solid",
            bd=1,
            padx=10,
            pady=4
        ).pack(side="left")

        tk.Button(
            controls,
            text="Sort by temperature ↕",
            command=self.sort_table,
            bg=S.WHITE,
            fg=S.TEXT,
            relief="solid",
            bd=1,
            padx=10,
            pady=4
        ).pack(
            side="left",
            padx=6
        )

        cols = (
            "country",
            "temp",
            "co2",
            "sea",
            "renew"
        )

        self.tree = ttk.Treeview(
            tablecard,
            columns=cols,
            show="headings",
            height=5
        )

        for col, title, width in zip(
            cols,
            [
                "COUNTRY",
                "AVG TEMP °C",
                "CO₂ / CAPITA",
                "SEA LEVEL mm",
                "RENEWABLE %"
            ],
            [130, 100, 100, 100, 100]
        ):

            self.tree.heading(
                col,
                text=title
            )

            self.tree.column(
                col,
                width=width,
                anchor="w"
            )

        self.tree.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=(0, 12)
        )

        self.tree.bind(
            "<Double-1>",
            self.row_detail
        )

        # DATASET HEALTH

        health = tk.Frame(
            bottom,
            bg=S.WHITE,
            highlightbackground=S.BORDER,
            highlightthickness=1,
            width=290
        )

        health.pack(
            side="right",
            fill="y"
        )

        health.pack_propagate(False)

        tk.Label(
            health,
            text="Dataset health",
            bg=S.WHITE,
            fg=S.TEXT,
            font=(S.FONT, 12, "bold")
        ).pack(
            anchor="w",
            padx=18,
            pady=(17, 4)
        )

        tk.Label(
            health,
            text="Loaded CSV · computed from file",
            bg=S.WHITE,
            fg=S.MUTED,
            font=(S.FONT, 8)
        ).pack(
            anchor="w",
            padx=18
        )

        inset = tk.Frame(
            health,
            bg=S.PALE
        )

        inset.pack(
            fill="x",
            padx=14,
            pady=14
        )

        tk.Label(
            inset,
            text="climate_change_dataset.csv",
            bg=S.PALE,
            fg=S.TEXT,
            font=(S.FONT, 8, "bold"),
            wraplength=240
        ).pack(
            anchor="w",
            padx=12,
            pady=(12, 6)
        )

        self.quality_label = tk.Label(
            inset,
            text="",
            bg=S.PALE,
            fg=S.TEXT,
            font=(S.FONT, 10, "bold")
        )

        self.quality_label.pack(
            anchor="w",
            padx=12
        )

        self.quality_bar = ttk.Progressbar(
            inset,
            maximum=100
        )

        self.quality_bar.pack(
            fill="x",
            padx=12,
            pady=7
        )

        self.health_records = tk.Label(
            inset,
            text="",
            bg=S.PALE,
            fg=S.MUTED,
            font=(S.FONT, 8)
        )

        self.health_records.pack(
            anchor="w",
            padx=12,
            pady=(0, 12)
        )

        self.health_stats = tk.Label(
            health,
            text="",
            bg=S.WHITE,
            fg=S.TEXT,
            font=(S.FONT, 9),
            justify="left"
        )

        self.health_stats.pack(
            anchor="w",
            padx=18,
            pady=4
        )

        tk.Button(
            health,
            text="Manage sources",
            command=self.manage_sources,
            bg=S.WHITE,
            fg=S.TEXT,
            relief="solid",
            bd=1,
            pady=8
        ).pack(
            fill="x",
            padx=16,
            pady=14
        )

        # CORRELATION ANALYSIS SECTION

        self.correlation_section = CorrelationSection(pad)

        # FOOTER

        foot = tk.Frame(
            pad,
            bg=S.BG
        )

        foot.pack(
            fill="x",
            pady=(20, 0)
        )

        tk.Frame(
            foot,
            bg=S.BORDER,
            height=1
        ).pack(
            fill="x",
            pady=(0, 12)
        )

        tk.Label(
            foot,
            text="ClimateLens · An open data science project",
            bg=S.BG,
            fg=S.MUTED,
            font=(S.FONT, 8)
        ).pack(side="left")

        tk.Label(
            foot,
            text="Built from the user-provided climate dataset",
            bg=S.BG,
            fg=S.MUTED,
            font=(S.FONT, 8)
        ).pack(side="right")

    # UPDATE DATE RANGE

    def on_period(self):

        self.period = self.range_var.get()
        self.refresh()

    # REFRESH DASHBOARD

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

    # COUNTRY TABLE

    def populate_table(self, df):

        for item in self.tree.get_children():
            self.tree.delete(item)

        summary = country_summary(df).sort_values(
            "temperature",
            ascending=False
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

    # EXPORT CSV

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

    # FILTER COUNTRY

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

    # SORT TABLE

    def sort_table(self):

        current = self.filtered.copy()

        sorted_data = current.sort_values(
            "Avg Temperature (°C)",
            ascending=False
        )

        self.populate_table(sorted_data)

    # COUNTRY DETAIL DIALOG

    def row_detail(self, event=None):

        sel = self.tree.selection()

        if not sel:
            return

        country = self.tree.item(
            sel[0],
            "values"
        )[0]

        d = self.df[
            self.df["Country"] == country
        ]

        win = tk.Toplevel(self.root)

        win.title(
            country + " · climate details"
        )

        win.configure(bg=S.BG)
        win.geometry("420x330")

        tk.Label(
            win,
            text=country,
            bg=S.BG,
            fg=S.TEXT,
            font=(S.FONT, 18, "bold")
        ).pack(
            anchor="w",
            padx=22,
            pady=(22, 8)
        )

        lines = [

            f"Records: {len(d)}",

            f"Years: {d['Year'].min()}–{d['Year'].max()}",

            f"Average temperature: "
            f"{safe_mean(d['Avg Temperature (°C)']):.2f} °C",

            f"CO₂ emissions per capita: "
            f"{safe_mean(d['CO2 Emissions (Tons/Capita)']):.2f} tons",

            f"Sea level rise: "
            f"{safe_mean(d['Sea Level Rise (mm)']):.2f} mm",

            f"Renewable energy: "
            f"{safe_mean(d['Renewable Energy (%)']):.2f}%",

            f"Extreme weather events (mean): "
            f"{safe_mean(d['Extreme Weather Events']):.2f}"
        ]

        tk.Label(
            win,
            text="\n".join(lines),
            bg=S.BG,
            fg=S.TEXT,
            font=(S.FONT, 10),
            justify="left"
        ).pack(
            anchor="w",
            padx=22,
            pady=10
        )

    # COUNTRY COMPARISON

    def country_dialog(self):

        summary = country_summary(
            self.df
        ).sort_values(
            "temperature",
            ascending=False
        )

        win = tk.Toplevel(self.root)

        win.title("Country comparison")
        win.geometry("580x420")
        win.configure(bg=S.BG)

        tk.Label(
            win,
            text="Country comparison",
            bg=S.BG,
            fg=S.TEXT,
            font=(S.FONT, 16, "bold")
        ).pack(
            anchor="w",
            padx=18,
            pady=14
        )

        tree = ttk.Treeview(
            win,
            columns=("country", "temp", "co2", "sea", "renew"),
            show="headings"
        )

        for c, t in zip(
            ("country", "temp", "co2", "sea", "renew"),
            (
                "Country",
                "Temp °C",
                "CO₂/capita",
                "Sea level mm",
                "Renewable %"
            )
        ):

            tree.heading(c, text=t)
            tree.column(c, width=105)

        tree.pack(
            fill="both",
            expand=True,
            padx=18,
            pady=(0, 18)
        )

        for _, r in summary.iterrows():

            tree.insert(
                "",
                "end",
                values=(
                    r["Country"],
                    f'{r["temperature"]:.2f}',
                    f'{r["co2"]:.2f}',
                    f'{r["sea_level"]:.2f}',
                    f'{r["renewable"]:.1f}'
                )
            )

    # TEMPORAL DETAIL VIEW

    def temporal_detail_dialog(self, granularity):

        win = tk.Toplevel(self.root)
        win.title(f"ClimateLens · {granularity} view")
        win.geometry("940x560")
        win.configure(bg=S.BG)
        win.minsize(760, 420)
        win.transient(self.root)

        header = tk.Frame(win, bg=S.WHITE)
        header.pack(fill="x")

        tk.Label(
            header,
            text=f"{granularity} detail view",
            bg=S.WHITE,
            fg=S.TEXT,
            font=(S.FONT, 16, "bold")
        ).pack(anchor="w", padx=22, pady=(16, 2))

        tk.Label(
            header,
            text=(
                "The bundled dataset is year-based. "
                "Daily and monthly views are summarized from annual records."
            ),
            bg=S.WHITE,
            fg=S.MUTED,
            font=(S.FONT, 9),
            wraplength=850,
            justify="left"
        ).pack(anchor="w", padx=22, pady=(0, 16))

        body = tk.Frame(win, bg=S.BG)
        body.pack(fill="both", expand=True, padx=18, pady=18)

        columns = ("period", "countries", "records", "temperature", "co2", "renewable")
        tree = ttk.Treeview(
            body,
            columns=columns,
            show="headings",
            height=18
        )

        headings = (
            granularity.upper(),
            "COUNTRIES",
            "RECORDS",
            "AVG TEMP °C",
            "CO₂ / CAPITA",
            "RENEWABLE %"
        )

        for column, heading, width in zip(
            columns,
            headings,
            (140, 100, 100, 120, 120, 120)
        ):
            tree.heading(column, text=heading)
            tree.column(column, width=width, anchor="w")

        yscroll = ttk.Scrollbar(
            body,
            orient="vertical",
            command=tree.yview
        )
        tree.configure(yscrollcommand=yscroll.set)
        tree.pack(side="left", fill="both", expand=True)
        yscroll.pack(side="right", fill="y")

        years = (
            sorted(self.df["Year"].unique())
            if granularity == "Year"
            else sorted(self.df["Year"].unique(), reverse=True)
        )

        for year in years:
            part = self.df[self.df["Year"] == year]
            period = (
                f"{year}-01-01"
                if granularity == "Day"
                else f"{year}-01"
                if granularity == "Month"
                else str(year)
            )
            tree.insert(
                "",
                "end",
                values=(
                    period,
                    part["Country"].nunique(),
                    len(part),
                    f"{safe_mean(part['Avg Temperature (°C)']):.2f}",
                    f"{safe_mean(part['CO2 Emissions (Tons/Capita)']):.2f}",
                    f"{safe_mean(part['Renewable Energy (%)']):.2f}"
                )
            )

    # DATASET MANAGEMENT

    def manage_sources(self):

        quality = completeness(self.df)

        win = tk.Toplevel(self.root)

        win.title("Dataset sources")
        win.geometry("500x320")
        win.configure(bg=S.BG)

        tk.Label(
            win,
            text="Dataset source and quality",
            bg=S.BG,
            fg=S.TEXT,
            font=(S.FONT, 16, "bold")
        ).pack(
            anchor="w",
            padx=22,
            pady=(22, 12)
        )

        text = (
            f"Loaded file: {DEFAULT_DATA.name}\n"
            f"Path: {DEFAULT_DATA}\n"
            f"Rows: {len(self.df):,}\n"
            f"Countries: {self.df['Country'].nunique()}\n"
            f"Year range: {self.df['Year'].min()}–{self.df['Year'].max()}\n"
            f"Numeric completeness: {quality:.2f}%\n\n"
            "This is the uploaded climate_change_dataset.csv. "
            "It is not identified as a NASA GISTEMP dataset."
        )

        tk.Label(
            win,
            text=text,
            bg=S.BG,
            fg=S.TEXT,
            justify="left",
            wraplength=450,
            font=(S.FONT, 9)
        ).pack(
            anchor="w",
            padx=22
        )

        tk.Button(
            win,
            text="Open climate data reference ↗",
            command=lambda: webbrowser.open(SOURCE_URL),
            bg=S.SIDEBAR,
            fg="white",
            relief="flat",
            padx=12,
            pady=8
        ).pack(
            anchor="w",
            padx=22,
            pady=16
        )

    # SETTINGS

    def settings_dialog(self):

        win = tk.Toplevel(self.root)
        win.title("ClimateLens settings")
        win.geometry("560x430")
        win.minsize(520, 390)
        win.configure(bg=S.BG)
        win.transient(self.root)

        tk.Label(
            win,
            text="Settings",
            bg=S.BG,
            fg=S.TEXT,
            font=(S.FONT, 20, "bold")
        ).pack(anchor="w", padx=28, pady=(24, 4))

        tk.Label(
            win,
            text="Manage the data source used by ClimateLens.",
            bg=S.BG,
            fg=S.MUTED,
            font=(S.FONT, 10)
        ).pack(anchor="w", padx=28, pady=(0, 18))

        panel = tk.Frame(
            win,
            bg=S.WHITE,
            highlightbackground=S.BORDER,
            highlightthickness=1
        )
        panel.pack(fill="x", padx=28)

        tk.Label(
            panel,
            text="ACTIVE DATASET",
            bg=S.WHITE,
            fg=S.MUTED,
            font=(S.FONT, 8, "bold")
        ).pack(anchor="w", padx=20, pady=(18, 4))

        current = getattr(self, "dataset_path", DEFAULT_DATA)
        tk.Label(
            panel,
            text=Path(current).name,
            bg=S.WHITE,
            fg=S.TEXT,
            font=(S.FONT, 12, "bold")
        ).pack(anchor="w", padx=20)

        path_label = tk.Label(
            panel,
            text=str(current),
            bg=S.WHITE,
            fg=S.MUTED,
            font=(S.FONT, 8),
            wraplength=470,
            justify="left"
        )
        path_label.pack(anchor="w", padx=20, pady=(4, 18))

        def load_replacement():
            selected = filedialog.askopenfilename(
                parent=win,
                title="Select climate dataset",
                filetypes=[("CSV files", "*.csv")]
            )
            if not selected:
                return

            try:
                replacement = load_dataset(selected)
            except Exception as e:
                messagebox.showerror(
                    "Could not load dataset",
                    str(e),
                    parent=win
                )
                return

            self.df = replacement
            self.dataset_path = Path(selected)
            self.filtered = replacement.copy()
            path_label.config(text=str(selected))
            win.after(100, self.refresh)
            messagebox.showinfo(
                "Dataset updated",
                f"Loaded {len(replacement):,} valid records.",
                parent=win
            )

        def restore_bundled():
            try:
                restored = load_dataset(DEFAULT_DATA)
            except Exception as e:
                messagebox.showerror(
                    "Could not restore dataset",
                    str(e),
                    parent=win
                )
                return

            self.df = restored
            self.dataset_path = DEFAULT_DATA
            self.filtered = restored.copy()
            path_label.config(text=str(DEFAULT_DATA))
            win.after(100, self.refresh)
            messagebox.showinfo(
                "Dataset restored",
                "The bundled dataset is active again.",
                parent=win
            )

        actions = tk.Frame(win, bg=S.BG)
        actions.pack(fill="x", padx=28, pady=18)

        tk.Button(
            actions,
            text="Choose CSV...",
            command=load_replacement,
            bg=S.SIDEBAR,
            fg="white",
            activebackground=S.SIDEBAR_HI,
            relief="flat",
            font=(S.FONT, 9, "bold"),
            padx=16,
            pady=10,
            cursor="hand2"
        ).pack(side="left")

        tk.Button(
            actions,
            text="Restore bundled data",
            command=restore_bundled,
            bg=S.WHITE,
            fg=S.TEXT,
            activebackground=S.PALE,
            relief="solid",
            bd=1,
            font=(S.FONT, 9),
            padx=16,
            pady=9,
            cursor="hand2"
        ).pack(side="left", padx=10)


def main():

    root = tk.Tk()

    try:

        ClimateLensApp(root)

    except Exception as e:

        messagebox.showerror(
            "ClimateLens could not start",
            f"Check the CSV and required columns.\n\nDetails: {e}"
        )

        root.destroy()
        return

    root.mainloop()