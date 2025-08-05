import requests
import os
from dotenv import load_dotenv
load_dotenv()
access_token = os.getenv('TOKEN')
room_id = os.getenv('ROOM_ID')
person_email = 'new-user@example.com'
url = 'https://webexapis.com/v1/memberships'
headers = {
	'Authorization': 'Bearer {}'.format(access_token),
	'Content-Type': 'application/json'
}
params = {'roomId': room_id, 'personEmail': person_email}

res = requests.post(url, headers=headers, json=params)
print(res.json())