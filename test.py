import requests

url = "http://211.213.193.67:8000/signup/"
headers = {"Content-Type": "application/json"}
data = {
    "name": "John Doe",
    "phone_number": "010-1234-5678",
    "city": "Seoul",
    "town": "Gangnam",
    "village": "Apgujeong",
    "role": "Admin"
}

response = requests.post(url, json=data, headers=headers)
print(response.status_code, response.json())