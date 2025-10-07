import requests
import json


def send(cellphone, message):
    url = "https://api.infobip.com/sms/1/text/single"
    payload = json.dumps({
        "from": "Unilabs",
        "to": "{}{}".format("+51", cellphone),
        "text": message
    })
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'Basic dW5pbGFicy5hcGk6VW5pbGFic0AyMDIw'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    return response.text

