import api_excercises.authentication as auth
import requests
import time

bearerToken = auth.generate_bearer_token()

time.sleep(1)

def get_resource(token):
    url = "http://localhost:8080/api/v1/demo-controller"

    headers = {
        "Authorization": f"Bearer {token}!"
    }
    response = requests.get(url, headers=headers)
    return response

secretResource = get_resource(bearerToken)
print("Status Code:", secretResource.status_code)
print(secretResource.text)