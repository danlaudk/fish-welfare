# Open-Meteo Historical Weather API Documentation

## Overview
Open-Meteo offers a free Historical Weather API based on reanalysis datasets (ERA5 and ERA5-Land). This documentation provides instructions for downloading weather history for specific locations in Andhra Pradesh, India.

## Target Locations
Based on repository analysis, "Eleru" in the request refers to **Eluru**, a major aquaculture hub.

| Location | Latitude | Longitude | Timezone |
| :--- | :--- | :--- | :--- |
| **Eluru** | 16.7119 | 81.0949 | Asia/Kolkata |
| **Nellore** | 14.4426 | 79.9865 | Asia/Kolkata |

## Time Period
- **Start Date**: `2021-06-01`
- **End Date**: `2026-02-28`

## API Configuration
- **Base URL**: `https://archive-api.open-meteo.com/v1/archive`
- **Data Model**: `era5_land` (Recommended for higher resolution land data)

### Mandatory Parameters
- `latitude`, `longitude`: Decimal coordinates.
- `start_date`, `end_date`: `YYYY-MM-DD`.
- `timezone`: `Asia/Kolkata`.
- `hourly` or `daily`: List of variables to include.

### Suggested Variables
- **Hourly**: `temperature_2m`, `relative_humidity_2m`, `precipitation`, `wind_speed_10m`, `soil_temperature_0_to_7cm`.
- **Daily**: `temperature_2m_max`, `temperature_2m_min`, `precipitation_sum`.

---

## Instructions for Coding Agent

### 1. API Request Construction
Construct the URL by appending parameters. Example for Eluru:
`https://archive-api.open-meteo.com/v1/archive?latitude=16.7119&longitude=81.0949&start_date=2021-06-01&end_date=2026-02-28&hourly=temperature_2m,relative_humidity_2m,precipitation&timezone=Asia%2FKolkata`

### 2. Implementation Script (Python)
Use the following pattern to download and process the data:

```python
import openmeteo_requests
import pandas as pd
from retry_requests import retry

# Setup the API client with retry on error
retry_strategy = retry(backoff_factor=1)
openmeteo = openmeteo_requests.Client(session=retry_strategy)

url = "https://archive-api.open-meteo.com/v1/archive"
params = {
    "latitude": [16.7119, 14.4426], # Eluru, Nellore
    "longitude": [81.0949, 79.9865],
    "start_date": "2021-06-01",
    "end_date": "2026-02-28",
    "hourly": ["temperature_2m", "relative_humidity_2m", "precipitation"],
    "timezone": "Asia/Kolkata"
}

responses = openmeteo.weather_api(url, params=params)

# Process the first location (Eluru)
response = responses[0]
hourly = response.Hourly()
data = {
    "date": pd.date_range(
        start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
        end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
        freq=pd.Timedelta(seconds=hourly.Interval()),
        inclusive="left"
    ),
    "temperature_2m": hourly.Variables(0).ValuesAsNumpy(),
    "precipitation": hourly.Variables(2).ValuesAsNumpy()
}
df = pd.DataFrame(data)
```

### 3. Error Handling
- The API returns HTTP 400 for invalid parameters with a JSON error body.
- No API key is required for non-commercial use, but rate limits apply (approx. 10,000 requests per day).

## Source URLs
- [Open-Meteo Historical Weather API Documentation](https://open-meteo.com/en/docs/historical-weather-api)
- [Open-Meteo Python SDK (GitHub)](https://github.com/open-meteo/openmeteo-python)
- [ERA5-Land Dataset Info](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land?tab=overview)
