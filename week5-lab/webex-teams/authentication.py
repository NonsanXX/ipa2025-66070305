from dotenv import load_dotenv
import requests
import json
import os

load_dotenv()
access_token = os.getenv('TOKEN')
url = 'https://webexapis.com/v1/people/me'
headers = {
    'Authorization': 'Bearer {}'.format(access_token)
}
res = requests.get(url, headers=headers)
print(json.dumps(res.json(), indent=4))