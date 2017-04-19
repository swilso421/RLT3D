import requests

url = "https://www.wayfair.com/v/api/three_d_model/models?page=1"

headers = {
    'Accept': "*/*",
    'Accept-Encoding': "gzip, deflate",
    'Authorization': "Basic dHVnNTk0MTRAdGVtcGxlLmVkdTo1OGRkMTA2MzJmNGE3",
    'Cache-Control': "no-cache",
    'Connection': "close",
    'Host': "www.wayfair.com",
    #'postman-token': "477bfdb5-032f-2140-9c3b-c95ad96b50a3"
    'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0"
    }

response = requests.request("GET", url, headers=headers)

data = response.json()

print(data)
