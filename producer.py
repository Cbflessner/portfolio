import google_scraper as gs
import os.path


google_news = gs.google_top_results(3, '/search?q=chicago&tbm=nws')
for num in range(len(google_news)):
    url = google_news.iloc[num]
    text = gs.html_to_string(url)
    news = gs.clean_news(text, 20)
    gs.save_file('google_news/google_news', num, url, news)

