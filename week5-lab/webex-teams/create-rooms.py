import os
import requests
from dotenv import load_dotenv 

load_dotenv()
access_token = os.getenv('TOKEN')
 
url = 'https://webexapis.com/v1/rooms'
headers = {
    'Authorization': 'Bearer {}'.format(access_token),
    'Content-Type': 'application/json'
}
params = {'title': 'DevNet Associate Training!'}
res = requests.post(url, headers=headers, json=params)
print(res.json())