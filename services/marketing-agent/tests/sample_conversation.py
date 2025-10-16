import requests, json, sys

BASE_URL = "http://localhost:8002"

messages = [
    "Hola",
    "Necesito ayuda con redes sociales",
    "Quiero información",
    "¿Cuánto cuesta?",
    "Quiero agendar una reunión",
    "El lunes en la tarde"
]

sender = "test-user"
for m in messages:
    resp = requests.post(f"{BASE_URL}/webhooks/rest/webhook", json={"sender": sender, "message": m})
    if resp.status_code != 200:
        print("Error:", resp.status_code, resp.text)
        sys.exit(1)
    data = resp.json()
    print(f"User: {m}")
    for d in data:
        print("Bot:", d.get("text"))
    print("-"*40)
