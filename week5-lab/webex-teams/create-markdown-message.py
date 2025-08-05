import requests
import os
from dotenv import load_dotenv
load_dotenv()
access_token = os.getenv('TOKEN')
room_id = os.getenv('ROOM_ID')

message = 'Hello **DevNet Associates**!!'
url = 'https://webexapis.com/v1/messages'
headers = {
	'Authorization': 'Bearer {}'.format(access_token),
	'Content-Type': 'application/json'
}
params = {'roomId': room_id, 'markdown': message}
res = requests.post(url, headers=headers, json=params)
print(res.json())