import tkinter as tk
from tkinter import messagebox

from data_manager import load_dataset
from dashboard_actions import DashboardActionsMixin
from dashboard_dialogs import DashboardDialogsMixin
from dashboard_layout import DashboardLayoutMixin


class ClimateLensApp(
    DashboardLayoutMixin,
    DashboardActionsMixin,
    DashboardDialogsMixin,
):

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
