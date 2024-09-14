import requests
import json

BASE_URL = "http://127.0.0.1:5001"  # Adjust if your server is running on a different port

def test_endpoint(method, path, data=None):
    url = f"{BASE_URL}{path}"
    if method == "GET":
        response = requests.get(url)
    elif method == "POST":
        response = requests.post(url, json=data)
    elif method == "PUT":
        response = requests.put(url, json=data)
    elif method == "DELETE":
        response = requests.delete(url)
    else:
        return f"Unsupported method: {method}"

    print(f"{method} {path}: Status Code {response.status_code}")
    try:
        return response.json()
    except json.JSONDecodeError:
        return response.text

# Test endpoints
print("Testing API endpoints...\n")

# Config
print(test_endpoint("GET", "/api/config"))

# Map
print(test_endpoint("GET", "/api/map"))

# User Authentication & Authorization
print(test_endpoint("POST", "/api/v1/auth/register", {"username": "testuser", "password": "testpass"}))
print(test_endpoint("POST", "/api/v1/auth/login", {"username": "testuser", "password": "testpass"}))
print(test_endpoint("POST", "/api/v1/auth/logout"))
print(test_endpoint("GET", "/api/v1/auth/me"))

# Vehicle Management
print(test_endpoint("GET", "/api/v1/vehicles"))
print(test_endpoint("POST", "/api/v1/vehicles", {"name": "Test Vehicle", "type": "car"}))
print(test_endpoint("GET", "/api/v1/vehicles/1"))
print(test_endpoint("PUT", "/api/v1/vehicles/1", {"name": "Updated Vehicle"}))
print(test_endpoint("DELETE", "/api/v1/vehicles/1"))

# Fleet Management
print(test_endpoint("GET", "/api/v1/fleets"))
print(test_endpoint("POST", "/api/v1/fleets", {"name": "Test Fleet"}))
print(test_endpoint("GET", "/api/v1/fleets/1"))
print(test_endpoint("PUT", "/api/v1/fleets/1", {"name": "Updated Fleet"}))
print(test_endpoint("DELETE", "/api/v1/fleets/1"))

# Trip Management
print(test_endpoint("GET", "/api/v1/trips"))
print(test_endpoint("POST", "/api/v1/trips", {"vehicle_id": 1, "start_time": "2023-09-14T10:00:00Z"}))
print(test_endpoint("GET", "/api/v1/trips/1"))
print(test_endpoint("PUT", "/api/v1/trips/1", {"end_time": "2023-09-14T11:00:00Z"}))

# Maintenance
print(test_endpoint("GET", "/api/v1/maintenance"))
print(test_endpoint("POST", "/api/v1/maintenance", {"vehicle_id": 1, "description": "Oil change"}))

# Reporting
print(test_endpoint("GET", "/api/v1/reports"))
print(test_endpoint("POST", "/api/v1/reports", {"title": "Test Report", "content": "This is a test report"}))

print("\nAPI endpoint testing completed.")