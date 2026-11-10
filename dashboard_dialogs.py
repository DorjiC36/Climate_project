import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import webbrowser
from pathlib import Path

from calculations import completeness, country_summary, safe_mean
from data_manager import DEFAULT_DATA, load_dataset
from dashboard_layout import SOURCE_URL
import styles as S


class DashboardDialogsMixin:

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
