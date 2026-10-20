import requests

url = "http://127.0.0.1:8000/webhook"
payload = {
    "type": "checkout.session.completed",
    "data": {"object": {"customer_details": {"email": "test@example.com"}}}
}
response = requests.post(url, json=payload)
print(f"Status Code: {response.status_code}")
print(f"Response: {response.json()}")