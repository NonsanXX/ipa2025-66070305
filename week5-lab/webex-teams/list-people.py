from dotenv import load_dotenv
import requests
import json
import os

load_dotenv()
access_token = os.getenv('TOKEN')
person_id = 'Y2lzY29zcGFyazovL3VzL1BFT1BMRS85M2VmYjI2ZS02YzQ2LTQ4ZWMtYWJjZi00Y2NjZGY5YTI1N2I'
url = 'https://webexapis.com/v1/people/{}'.format(person_id)
headers = {
    'Authorization': 'Bearer {}'.format(access_token),
    'Content-Type': 'application/json'
}
#params = {'email': '66070100@kmitl.ac.th'} 
res = requests.get(url, headers=headers)
print(json.dumps(res.json(), indent=4))