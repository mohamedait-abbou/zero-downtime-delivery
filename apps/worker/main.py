import os
import time
import urllib.request

API_URL = os.getenv("API_URL", "http://api:8000")
INTERVAL_S = float(os.getenv("INTERVAL_S", "5"))


def call_api():
    with urllib.request.urlopen(f"{API_URL}/work?n=1", timeout=3) as response:
        return response.status, response.read().decode()


while True:
    try:
        status, body = call_api()
        print(f"ok status={status} body={body}", flush=True)
    except Exception as error:
        print(f"error {type(error).__name__}: {error}", flush=True)
    time.sleep(INTERVAL_S)
