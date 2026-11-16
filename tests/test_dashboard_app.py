import unittest
from pathlib import Path

import pandas as pd
from streamlit.testing.v1 import AppTest

from dashboard import _pair_correlation


class DashboardAppTests(unittest.TestCase):

    def test_pair_correlation_requires_valid_variation(self):
        pairs_without_comparison = (
            pd.DataFrame(columns=["x", "y"]),
            pd.DataFrame({"x": [1], "y": [2]}),
            pd.DataFrame({"x": [1, 1], "y": [2, 3]}),
            pd.DataFrame({"x": [1, 2], "y": [3, 3]}),
        )
        for pair in pairs_without_comparison:
            with self.subTest(pair=pair.to_dict()):
                self.assertIsNone(_pair_correlation(pair))

        self.assertAlmostEqual(
            _pair_correlation(
                pd.DataFrame({"x": [1, 2, 3], "y": [2, 4, 6]})
            ),
            1.0,
        )

    def test_dashboard_filters_and_switches_to_findings(self):
        dashboard = Path(__file__).resolve().parents[1] / "dashboard.py"
        app = AppTest.from_file(str(dashboard)).run(timeout=30)

        self.assertFalse(app.exception)
        self.assertEqual(len(app.dataframe), 1)

        app.selectbox(key="heatmap_palette").set_value("Red–blue").run()
        self.assertFalse(app.exception)

        variable = app.selectbox(key="relationship_x").value
        app.selectbox(key="relationship_y").set_value(variable).run()
        self.assertFalse(app.exception)

        country_widget = app.multiselect(key="countries")
        self.assertTrue(country_widget.options)
        country_widget.select([country_widget.options[0]]).run()
        self.assertFalse(app.exception)
        self.assertIn(
            country_widget.options[0],
            app.dataframe[0].value["Country"].tolist(),
        )

        app.radio(key="page").set_value("Research findings").run()
        self.assertFalse(app.exception)
        self.assertEqual(len(app.expander), 8)


if __name__ == "__main__":
    unittest.main()
