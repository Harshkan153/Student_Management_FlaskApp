import requests

# Create a session to persist cookies
session = requests.Session()

# Login request
login_url = "http://127.0.0.1:5000/students/login"
payload = {"username": "mangal", "password": "12345"}
headers = {"Content-Type": "application/json"}

res = session.post(login_url, json=payload, headers=headers)

print("Login:", res.status_code, res.text)

# If login is successful, fetch students data
if res.status_code == 200:
    students_url = "http://127.0.0.1:5000/students/students"
    res = session.get(students_url)  # Using the same session
    print("Fetch Students:", res.status_code, res.text)


