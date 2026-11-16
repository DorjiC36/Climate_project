## Run the Streamlit dashboard

Install the project dependencies and start the dashboard from the project
directory:

```powershell
python -m pip install -r requirements.txt
python -m streamlit run dashboard.py
```

The dashboard loads `data/climate_change_dataset.csv` by default. Use the
sidebar to upload a replacement CSV, choose a time window and countries, or
switch between the overview and research findings. The overview includes
downloadable filtered data.

To switch between the forest-green light and dark themes, open the top-right
app menu and choose **System**, **Light**, or **Dark**.
