import requests
from dotenv import dotenv_values

config = dotenv_values(".env")
APP_TOKEN = config.get("PUSHOVER_APP_TOKEN")
USER_KEY = config.get("PUSHOVER_USER_KEY")
URL = "https://api.pushover.net/1/messages.json"

title = "Title Test"
myMsg = "Hello from mac book!"

if not APP_TOKEN or not USER_KEY:
    raise ValueError("Brak wymaganych zmiennych środowiskowych")

payload = {
    "token": APP_TOKEN,
    "user": USER_KEY,
    "message": myMsg,
    "title": title,
}

try:
    resp = requests.post(URL, data=payload, timeout=15)
    resp.raise_for_status()
    result = resp.json()

    if result.get("status") == 1:
        print(f"✓ Powiadomienie wysłane: {result}")
    else:
        print(f"✗ Błąd API: {result.get('errors', 'Unknown error')}")

except requests.exceptions.RequestException as e:
    print(f"✗ Błąd połączenia: {e}")
except ValueError as e:
    print(f"✗ Błąd JSON: {e}")
