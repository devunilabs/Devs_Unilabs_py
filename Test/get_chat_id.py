import requests

TOKEN = "490481985:AAEK31071Egpys7j7l1qyxrvhokh6X9ff9o"  # tu token
url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"

resp = requests.get(url)
print(resp.json())
