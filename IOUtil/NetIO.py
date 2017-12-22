import urllib.request
import requests
import zlib

def readJsonFrom(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

    response = requests.get(url, headers=headers)
    data = response.content
    # print(data)
    data = data.decode('utf-8')
    return data

def readDataFrom(url):
    request = urllib.request.Request(url)
    response = urllib.request.urlopen(request)
    data = response.read()
    data = data.decode('utf-8')

    data=data.replace('\n','')
    return data

