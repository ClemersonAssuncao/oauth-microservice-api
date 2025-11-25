import requests

# Test authentication with testuser
print("Testing authentication with testuser...")
response = requests.post(
    "http://localhost:8000/api/v1/auth/token",
    data={
        "username": "testuser",
        "password": "test123"
    }
)

print(f"Status Code: {response.status_code}")
if response.status_code == 200:
    print("✅ Authentication successful!")
    print(f"Response: {response.json()}")
else:
    print("❌ Authentication failed!")
    print(f"Response: {response.text}")

print("\n" + "="*50 + "\n")

# Test authentication with admin
print("Testing authentication with admin...")
response = requests.post(
    "http://localhost:8000/api/v1/auth/token",
    data={
        "username": "admin",
        "password": "admin123"
    }
)

print(f"Status Code: {response.status_code}")
if response.status_code == 200:
    print("✅ Authentication successful!")
    print(f"Response: {response.json()}")
else:
    print("❌ Authentication failed!")
    print(f"Response: {response.text}")
