import requests
import json

def register_user():
    response = ""
    url = "http://localhost:8080/api/v1/auth/register"

    payload = {
        "firstname": "name",
        "lastname": "name",
        "email": "name@gmail.com",
        "password": "1234"
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        print("Status Code:", response.status_code)
        return response.json()
    except json.decoder.JSONDecodeError:
        print("Status Code:", response.status_code)

def generate_bearer_token():
    url = "http://localhost:8080/api/v1/auth/authenticate"

    payload = {
        "email": "name@gmail.com",
        "password": "1234"
    }

    response = requests.post(url, json=payload)
    print("Status Code:", response.status_code)
    tokens = response.json()
    return tokens["token"]



