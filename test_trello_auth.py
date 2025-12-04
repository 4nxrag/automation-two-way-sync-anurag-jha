import requests
from config import Config

# Test authentication
url = f"https://api.trello.com/1/boards/{Config.TRELLO_BOARD_ID}"
params = {
    "key": Config.TRELLO_API_KEY,
    "token": Config.TRELLO_TOKEN
}

response = requests.get(url, params=params)

if response.status_code == 200:
    board = response.json()
    print(f"✓ Authentication successful!")
    print(f"  Board Name: {board['name']}")
    print(f"  Board ID: {board['id']}")
else:
    print(f"✗ Authentication failed: {response.status_code}")
    print(f"  Error: {response.text}")
