# ClimateLens – Data Studio

A native Python desktop dashboard built with Tkinter/ttk, NumPy, Pandas, and Matplotlib. It provides one unified Overview screen; there are no separate Temperature, Emissions, or Sea Level pages.

## Important data note

The bundled `data/climate_change_dataset.csv` is the dataset supplied with the project. Its columns are country/year observations such as average temperature, CO₂ emissions per capita, sea-level rise, rainfall, population, renewable energy, extreme weather events, and forest area. It does **not** contain a global temperature-anomaly series or a NASA GISTEMP source identifier. Therefore, the dashboard labels the plot as annual average temperature, not as a verified NASA anomaly, and labels the data as sample/uploaded data rather than live data.

## Install

1. Install Python 3.10 or newer.
2. Open this `ClimateLens` folder in Visual Studio Code.
3. Create a terminal (`Terminal → New Terminal`).
4. Optionally create a virtual environment:
   - Windows: `py -m venv .venv`
   - Activate: `.venv\\Scripts\\activate`
5. Install packages: `python -m pip install -r requirements.txt`
6. Run: `python main.py`

Tkinter is normally included with the official Windows Python installer. On Linux, install the OS package for Tkinter (often `python3-tk`) if needed.

## Replacing the CSV

Replace `data/climate_change_dataset.csv` with your new CSV, keeping the required column names:
`Year`, `Country`, `Avg Temperature (°C)`, `CO2 Emissions (Tons/Capita)`, `Sea Level Rise (mm)`, `Rainfall (mm)`, `Population`, `Renewable Energy (%)`, `Extreme Weather Events`, and `Forest Area (%)`.

The app validates required columns and numeric fields on launch. Missing numeric cells are tolerated and excluded from numerical calculations. The chart, metric cards, country table, and quality summary are computed from the loaded data. Restart the app after replacing the file.

## Interactions

- `12M`, `5Y`, and `All` filter the chart and summary metrics by year.
- `Export CSV` exports the currently selected period.
- `Filter country` filters the country table by a typed country name.
- `Sort by temperature` sorts the displayed country summary.
- Double-click a country row to view its available measurements.
- `Explore country data` opens a country comparison dialog.
- Correlation heatmap shows Pearson r for all numeric climate variables.
- Relationship explorer lets you select any two indicators and view their scatter plot, least-squares trend line, Pearson r, and paired record count.
- `Manage sources` shows file, row count, year range, and computed completeness.

## NumPy use

NumPy is used for safe numeric arrays, finite-value filtering, means, annual series preparation, bar scaling, completeness calculations, pairwise Pearson correlation (`np.corrcoef`), and least-squares trend lines (`np.polyfit`). Pandas is used for CSV ingestion and grouping; Tkinter/ttk builds the desktop UI; Matplotlib renders the chart.

## Troubleshooting

- **`ModuleNotFoundError: numpy/pandas/matplotlib`**: run `python -m pip install -r requirements.txt` in the same environment used to launch the app.
- **`No module named tkinter`**: install Tk support for your Python distribution. On Windows, rerun the official Python installer and enable Tcl/Tk.
- **Missing columns**: check exact CSV header names listed above.
- **Window layout looks cramped**: maximize the window; the main content area is scrollable.
- **No chart data**: verify `Year` and `Avg Temperature (°C)` contain numeric values.

## Interpreting correlations

Pearson r ranges from -1 to +1. Positive values indicate that the variables tend to increase together; negative values indicate that one tends to decrease as the other increases; values near zero indicate little linear association. Correlation does not establish causation. Because records are repeated across countries and years, treat these as exploratory associations rather than causal conclusions.
