
import requests
import time

url = "0.0.0.0:8111/stay_alive"

time.sleep(3)

while True:
    _ = requests.get(url, stream=True)
    time.sleep(10)
