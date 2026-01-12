import requests
import json

BASE_URL = 'http://localhost:5000'

def pretty(res):
    try:
        print(json.dumps(res.json(), indent=4))
    except:
        print(res.text)

# Test user registration
print("\n Student signup")

res = requests.post(
    f"{BASE_URL}/signup",
    json = {
        'username' : "student1",
        'password' : "password123",
    }
)
pretty(res)

# test user login
print("\n Student login")
res = requests.post(
    f"{BASE_URL}/login",
    json = {
        "username" : "student1",
        "password" : "password123"
    }
)
pretty(res)

print("\n Test completed")