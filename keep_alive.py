
import requests
import time
from utils import *
import datetime

url = "localhost:8111/stay_alive"

time.sleep(3)

while True:
    try:
        _ = requests.get(url, stream=True)
    except:
        text = f'Camera activity: Camera not reachable. time is {datetime.datetime.now()}' 
        sms.send(payload=text)
        print(text)
        break 
        
    time.sleep(10)
