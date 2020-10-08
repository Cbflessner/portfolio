import requests
from bs4 import BeautifulSoup as bs
import re
from datetime import date
import os.path
import os
import pprint
import pandas as pd

#Transforms HTML into soup object from beautiful soup library
def create_soup(url):
    try:
        page = requests.get(url)
    except requests.exceptions.RequestException as e:
        print('the URL you passed to create_soup() had an issue\n')
        raise(e)
        return
    soup = bs(page.content, 'lxml')
    return soup

#excludes any link that doesn't contain http 
#exclueds any link that does contain google
def non_google_links(href):
    article = re.compile('http')
    google = re.compile('google')
    if href is None:
        return False
    elif article.search(href) and not google.search(href):
        return True
    else:
        return False

#Returns a panda series of URLs gotten from google
def google_top_results(n, ext):
    url = 'https://www.google.com' + ext
    soup = create_soup(url)
    main = soup.find(id='main')
    links = main.find_all(href=non_google_links)
    news = []
    for link in links:
        clean_link = link.get('href')
        regex = re.compile(r'(http[s]?://.*?)&sa')
        m = regex.search(clean_link)
        news.append(m.group(1))
    news = pd.Series(news)
    news = pd.Series(news.unique())
    return news[:n]

#removes all links from soup. 
#might not actually want this at the end of the day as some links are embeded in the text of the article
def remove_links(soup):
    links = soup('a')
    for link in links:
        link.decompose()
    return soup

#extracts text from the html relying on the the create_soup function defined above
def html_to_string(url):
    # connect to url and transrom to soup
    soup = create_soup(url)
    #Optional: Get rid of links in page using remove_links() function above
    #extract the text
    text = soup.text
    return text

#removes whitespace from text scraped out of the HTML
def clean_news(text, words4paragraph):
    #break text into elements based on blank lines
    regex = re.compile('^[\n\r]', re.MULTILINE)
    clean_text = pd.Series(regex.split(text))
    cleaner = clean_text.str.replace('\t', '').str.replace('\n','').str.replace('\r', '').str.strip()
    clean = cleaner[cleaner.str.count(' ') >= words4paragraph]
    return clean

#Used for debugging
# def save_file(type_of_file, num, url, text):
#     today = str(date.today())
#     num += 1
#     file_name = type_of_file+'_'+str(num)+'_'+today+'.txt'
#     if os.path.isfile(file_name):
#         os.remove(file_name)
#     f = open(file_name, 'a')
#     f.write(url+'\n')
#     for k in text:
#         f.write(k + '\n\n')
#     f.close