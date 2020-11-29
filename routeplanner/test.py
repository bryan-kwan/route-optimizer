import requests

BASE = "http://127.0.0.1:5000/"

#needs to input the database json
#might also need to wrap that json in {} (python dict)
#data = 
response = requests.get(BASE, data)
print(response.json())

