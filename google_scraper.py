import requests
from bs4 import BeautifulSoup as bs
import re


def non_google_links(href):
    article = re.compile('http')
    google = re.compile('google')
    if href is None:
        return False
    elif article.search(href) and not google.search(href):
        return True
    else:
        return False


def google_top_results(n):
    url = 'https://www.google.com/search?q=chicago&tbm=nws'
    page = requests.get(url)
    soup = bs(page.content, 'lxml')
    main = soup.find(id='main')
    links = main.find_all(href=non_google_links)
    news = []
    for link in links:
        clean_link = link.get('href')
        regex = re.compile(r'(http[s]?://.*?)&sa')
        m = regex.search(clean_link)
        news.append(m.group(1))
    news = list(set(news))
    return news[:n]


# google_top_results(url, 3)

# conda create --name portfolio_venv --file requirements.txt
