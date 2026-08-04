import os
import requests
from dotenv import load_dotenv

load_dotenv(override=True)
user = os.getenv("BCC_API_USER")
password = os.getenv("BCC_API_PASS")

url = "https://si3.bcentral.cl/SieteRestWS/SieteRestWS.ashx"
params = {
    "user": user,
    "pass": password,
    "function": "GetSeries",
    "timeseries": "F073.TCO.PRE.Z.D",
    "firstdate": "2026-05-25",
    "lastdate": "2026-06-05"
}

response = requests.get(url, params=params, verify=False)
print("Status:", response.status_code)
print("JSON:", response.json())
