
import requests

url = "'0.0.0.0':8111/stay_alive"

_ = requests.get(url, stream=True)



