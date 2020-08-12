import requests
import pprint

url = 'https://www.google.com/search?q=chicago&tbm=nws'
page = requests.get(url)    

pprint(page)