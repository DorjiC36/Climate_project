import unittest

import pandas as pd

from research_findings import build_findings


class ResearchFindingsTests(unittest.TestCase):

    def setUp(self):
        self.data = pd.DataFrame({
            "Year": list(range(2000, 2008)),
            "Country": ["A", "A", "B", "B", "C", "C", "D", "D"],
            "Avg Temperature (°C)": [1, 2, 3, 4, 5, 6, 7, 8],
            "CO2 Emissions (Tons/Capita)": [1, 2, 3, 4, 5, 6, 7, 8],
            "Sea Level Rise (mm)": [8, 7, 6, 5, 4, 3, 2, 1],
            "Rainfall (mm)": [10, 11, 12, 13, 14, 15, 16, 17],
            "Population": [100, 110, 120, 130, 140, 150, 160, 170],
            "Renewable Energy (%)": [1, 2, 3, 4, 4, 3, 2, 1],
            "Forest Area (%)": [50, 49, 48, 47, 46, 45, 44, 43],
            "Extreme Weather Events": [1, 1, 2, 2, 3, 3, 4, 4]
        })

    def test_findings_cover_questions_and_hypothesis_decisions(self):
        findings = build_findings(self.data, "All")

        self.assertEqual(len(findings["questions"]), 5)
        self.assertEqual(len(findings["hypotheses"]), 3)
        self.assertIn("Reject H₀₁", findings["hypotheses"][0][1])
        self.assertIn("Reject H₀₂", findings["hypotheses"][1][1])
        self.assertIn(
            "Fail to reject H₀₃",
            findings["hypotheses"][2][1]
        )
        self.assertIn(
            "CO₂ emissions vs sea-level rise",
            findings["questions"][2][1]
        )

    def test_constant_pair_is_reported_as_untestable(self):
        self.data["Sea Level Rise (mm)"] = 1

        findings = build_findings(self.data, "All")

        self.assertIn(
            "Insufficient valid variation",
            findings["hypotheses"][1][1]
        )


if __name__ == "__main__":
    unittest.main()
