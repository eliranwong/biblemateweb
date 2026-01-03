import requests

# 1. Define the URL (ensure your NiceGUI app is running)
url = "http://localhost:33355/api/data"

# 2. Define your parameters
payload = {
    "query": ".help",  # Required
    "token": "my-secret-key-123"                  # Optional
}

# 3. Send the GET request
try:
    response = requests.get(url, params=payload)
    
    # 4. Check if the request was successful (Status Code 200)
    if response.status_code == 200:
        data = response.json()  # Convert JSON response to Python dict
        print("Success!")
        #print(f"Response: {data}")
        print(data.get("content"))
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

except requests.exceptions.ConnectionError:
    print("Could not connect to BibleMate. Is the NiceGUI app running?")