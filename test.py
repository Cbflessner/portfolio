import google_scraper as gs
from bs4 import BeautifulSoup as bs
import requests
from datetime import date
import re




path ='google_news/test/google_news_2_2020-08-25.txt'
f = open(path, 'r')
text = f.read()
f.close()

words4paragraph = 10
num = 2
url = 'www.test.com'
regex = re.compile('^[\n\r]', re.MULTILINE)
clean_text = regex.split(text)
remove = ['\t', '\n', '\r']
cleaner = [p.replace('\t', '').replace('\n','').replace('\r', '') for p in clean_text]
news = {p : str(len(p.split())) for p in cleaner if len(p.split())>=words4paragraph}
# gs.save_file('google_news/google_news', num, url, news)
print(cleaner)
