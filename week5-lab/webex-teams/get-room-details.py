import os
import requests
from dotenv import load_dotenv 

load_dotenv()
access_token = os.getenv('TOKEN')
 
room_id = os.getenv('ROOM_ID')
url = 'https://webexapis.com/v1/rooms/{}/meetingInfo'.format(room_id)
headers = {
	'Authorization': 'Bearer {}'.format(access_token),
	'Content-Type': 'application/json'
}
res = requests.get(url, headers=headers)
print(res.json())