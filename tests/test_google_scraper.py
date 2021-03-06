'''
unit tests for the google scraper library
'''
#Add the portfolio directory to the PYPATH so it can see the web_scrapers pakcage
import sys, os
this_path = os.path.dirname(os.path.abspath(__file__))
path=this_path.split( '/')
path.pop(len(path)-1)
portfolio_path = "/".join(path)
sys.path.insert(0, portfolio_path)
print(portfolio_path)

import kafka.web_scrapers.google_scraper as gs
import requests
from bs4 import BeautifulSoup as bs
import pytest
import re
import pandas as pd
import numpy as np
from datetime import date


class TestGoogleScraper:

    test_url = 'https://www.google.com'
    broken_url = 'https://www.googl.com'
    test_text = pd.Series(['test', 'test', 'test'])
    today = str(date.today())
    test_messages ='''test message with newlines (backslash n) \n\ntest message with carriage retruns (backslash r)\r\r
    test message with \t\t\t tabs\n      test message with leading whitespace\n test message with trailing whitespace       \n'''

    def test_create_soup(self):
        soup = gs.create_soup(self.test_url)
        page = requests.get(self.test_url)
        assert type(soup) is type(bs(page.content, 'lxml'))

    def test_create_soup_broken_url(self):
        with pytest.raises(requests.exceptions.RequestException):
            gs.create_soup(self.broken_url)

    def test_non_google_links(self):
        links =[]
        with open(this_path+'/google_links.txt') as l:
            for line in l:
                line = line.replace('\n', '')
                links.append(line)

        google_status = [] 
        for link in links:
            google_status.append(gs.non_google_links(link))
        assert 20 == sum(google_status)

    def test_google_top_results(self):
        n = 3
        result = gs.google_top_results(n, '/search?q=chicago&tbm=nws')
        counter = 0
        for link in result:
            page = requests.get(link)
            if page.status_code == 200:
                counter += 1
        assert n == counter

    def test_remove_links(self):
        soup = gs.create_soup(self.test_url)
        clean_soup = gs.remove_links(soup)
        links = clean_soup('a')
        assert len(links) == 0

    def test_html_to_string(self):
        words = gs.html_to_string(self.test_url)
        test = 'test'
        assert type(words) is type(test)

    def test_clean_news_tabs(self):
        regex = re.compile(r'\t')
        clean = gs.clean_news(self.test_messages, 5)
        result = clean.str.findall(regex)
        expected = []
        for i in range(len(clean)):
            expected.append([])
        expected = pd.Series(expected)
        assert np.array_equal(result.values, expected.values)

    def test_clean_news_newline(self):
        regex = re.compile(r'\n|\r')
        clean = gs.clean_news(self.test_messages, 5)
        result = clean.str.findall(regex)
        expected = []
        for i in range(len(clean)):
            expected.append([])
        expected = pd.Series(expected)
        assert np.array_equal(result.values, expected.values)

    def test_clean_news_strip(self):
        regex = re.compile(r'^\s|\s$')
        clean = gs.clean_news(self.test_messages, 5)
        result = clean.str.findall(regex)
        expected = []
        for i in range(len(clean)):
            expected.append([])
        expected = pd.Series(expected)
        assert np.array_equal(result.values, expected.values)

    # def test_save_file_correct_name(self):
    #     assert os.path.isfile(self.file_name)

    # def test_save_file_correct_content(self):
    #     f = open(self.file_name, 'r')
    #     contents =f.read()
    #     expected = self.test_url+'\n'
    #     for i in self.test_text:
    #         expected = expected + i +'\n\n'
    #     f.close
    #     assert contents == expected

        
