import io
import unittest

from data_manager import load_dataset


class LoadDatasetTests(unittest.TestCase):

    def test_loads_and_normalizes_csv_stream(self):
        csv = io.BytesIO(
            b"Year,Country,Avg Temperature (\xc2\xb0C),"
            b"CO2 Emissions (Tons/Capita),Sea Level Rise (mm),"
            b"Rainfall (mm),Population,Renewable Energy (%),"
            b"Extreme Weather Events,Forest Area (%)\n"
            b"2020, Testland ,1,2,3,4,5,6,7,8\n"
        )

        data = load_dataset(csv)

        self.assertEqual(len(data), 1)
        self.assertEqual(data.loc[0, "Year"], 2020)
        self.assertEqual(data.loc[0, "Country"], "Testland")


if __name__ == "__main__":
    unittest.main()
