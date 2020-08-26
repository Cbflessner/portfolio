'''
unit tests for the google scraper library
'''

import google_scraper
import requests


class TestGoogleScraper:

    def test_non_google_links(self):
        links = ['/search?q=chicago&ie=UTF-8&source=lnms&sa=X&ved=0ahUKEwi6s8zV4pvrAhXzdM0KHQVuBegQ_AUIBygA',
         'https://maps.google.com/maps?q=chicago&um=1&ie=UTF-8&sa=X&ved=0ahUKEwi6s8zV4pvrAhXzdM0KHQVuBegQ_AUICSgC',
         '/search?q=chicago&ie=UTF-8&tbm=isch&source=lnms&sa=X&ved=0ahUKEwi6s8zV4pvrAhXzdM0KHQVuBegQ_AUICigD',
         '/search?q=chicago&ie=UTF-8&tbm=vid&source=lnms&sa=X&ved=0ahUKEwi6s8zV4pvrAhXzdM0KHQVuBegQ_AUICygE',
         '/search?q=chicago&ie=UTF-8&tbm=shop&source=lnms&sa=X&ved=0ahUKEwi6s8zV4pvrAhXzdM0KHQVuBegQ_AUIDCgF',
         '/search?q=chicago&ie=UTF-8&tbm=bks&source=lnms&sa=X&ved=0ahUKEwi6s8zV4pvrAhXzdM0KHQVuBegQ_AUIDSgG',
         '/advanced_search',
         '/search?q=chicago&ie=UTF-8&tbm=nws&source=lnt&tbs=nrt:b&sa=X&ved=0ahUKEwi6s8zV4pvrAhXzdM0KHQVuBegQpwUIDw',
         '/search?q=chicago&ie=UTF-8&tbm=nws&source=lnt&tbs=qdr:h&sa=X&ved=0ahUKEwi6s8zV4pvrAhXzdM0KHQVuBegQpwUIEQ',
         '/search?q=chicago&ie=UTF-8&tbm=nws&source=lnt&tbs=qdr:d&sa=X&ved=0ahUKEwi6s8zV4pvrAhXzdM0KHQVuBegQpwUIEg',
         '/search?q=chicago&ie=UTF-8&tbm=nws&source=lnt&tbs=qdr:w&sa=X&ved=0ahUKEwi6s8zV4pvrAhXzdM0KHQVuBegQpwUIEw',
         '/search?q=chicago&ie=UTF-8&tbm=nws&source=lnt&tbs=qdr:m&sa=X&ved=0ahUKEwi6s8zV4pvrAhXzdM0KHQVuBegQpwUIFA',
         '/search?q=chicago&ie=UTF-8&tbm=nws&source=lnt&tbs=qdr:y&sa=X&ved=0ahUKEwi6s8zV4pvrAhXzdM0KHQVuBegQpwUIFQ',
         '/search?q=chicago&ie=UTF-8&tbm=nws&source=lnt&tbs=ar:1&sa=X&ved=0ahUKEwi6s8zV4pvrAhXzdM0KHQVuBegQpwUIFg',
         '/search?q=chicago&ie=UTF-8&tbm=nws&source=lnt&tbs=sbd:1&sa=X&ved=0ahUKEwi6s8zV4pvrAhXzdM0KHQVuBegQpwUIGA',
         '/url?q=https://www.foxnews.com/us/chicago-democrat-kim-foxx-looting-riots-raymond-lopez&sa=U&ved=2ahUKEwi6s8zV4pvrAhXzdM0KHQVuBegQxfQBMAB6BAgGEAE&usg=AOvVaw0e-PBR5wR5VL-9nSOKEviX',
         '/url?q=https://www.foxnews.com/us/chicago-democrat-kim-foxx-looting-riots-raymond-lopez&sa=U&ved=2ahUKEwi6s8zV4pvrAhXzdM0KHQVuBegQ0Y8FMAB6BAgGEAI&usg=AOvVaw2BXB9gLvaPL_Ev0TViJGz7',
         '/url?q=https://www.nbcchicago.com/news/local/chicago-protest-aims-to-shut-down-dan-ryan-expressway-this-weekend/2321821/&sa=U&ved=2ahUKEwi6s8zV4pvrAhXzdM0KHQVuBegQxfQBMAF6BAgJEAE&usg=AOvVaw2E_gEtLqZ43iC2G3QysJaV',
         '/url?q=https://www.nbcchicago.com/news/local/chicago-protest-aims-to-shut-down-dan-ryan-expressway-this-weekend/2321821/&sa=U&ved=2ahUKEwi6s8zV4pvrAhXzdM0KHQVuBegQ0Y8FMAF6BAgJEAI&usg=AOvVaw2cRM8K5J0lFh_QGP0x8lVa',
         '/url?q=https://www.chicagotribune.com/news/breaking/ct-chicago-looting-court-20200814-hv7kdbzlc5hmdmjkabaebu2yeq-story.html&sa=U&ved=2ahUKEwi6s8zV4pvrAhXzdM0KHQVuBegQxfQBMAJ6BAgIEAE&usg=AOvVaw3eiB9gnH8pi8T7TEkR7Api',
         '/url?q=https://www.chicagotribune.com/news/breaking/ct-chicago-looting-court-20200814-hv7kdbzlc5hmdmjkabaebu2yeq-story.html&sa=U&ved=2ahUKEwi6s8zV4pvrAhXzdM0KHQVuBegQ0Y8FMAJ6BAgIEAI&usg=AOvVaw1b5uLiDAlie2pWSIftQGjJ',
         '/url?q=https://www.foxnews.com/media/chicago-store-owner-is-looted-twice-i-dont-know-what-i-am-going-to-do&sa=U&ved=2ahUKEwi6s8zV4pvrAhXzdM0KHQVuBegQxfQBMAN6BAgHEAE&usg=AOvVaw2W_vwODMJFna90HVNaJIv7',
         '/url?q=https://www.foxnews.com/media/chicago-store-owner-is-looted-twice-i-dont-know-what-i-am-going-to-do&sa=U&ved=2ahUKEwi6s8zV4pvrAhXzdM0KHQVuBegQ0Y8FMAN6BAgHEAI&usg=AOvVaw1j5iDjQU5EMhCavgfhyb4v',
         '/url?q=https://chicago.suntimes.com/2020/8/14/21368202/calumet-river-army-corps-engineers-chicago-southeast-side-park-environment&sa=U&ved=2ahUKEwi6s8zV4pvrAhXzdM0KHQVuBegQxfQBMAR6BAgBEAE&usg=AOvVaw1LiEzEEBjp3qcRU4lo4oQ1',
         '/url?q=https://chicago.suntimes.com/2020/8/14/21368202/calumet-river-army-corps-engineers-chicago-southeast-side-park-environment&sa=U&ved=2ahUKEwi6s8zV4pvrAhXzdM0KHQVuBegQ0Y8FMAR6BAgBEAI&usg=AOvVaw0ZLaJPXL8cTKmPX7A1KLAp',
         '/url?q=https://www.chicagotribune.com/coronavirus/ct-covid-19-pandemic-chicago-illinois-news-20200814-2uedd64x5rg5xitgzlhy73puxm-story.html&sa=U&ved=2ahUKEwi6s8zV4pvrAhXzdM0KHQVuBegQxfQBMAV6BAgFEAE&usg=AOvVaw2gwBLsvuXhxGFbYy5S3Bgs',
         '/url?q=https://www.chicagotribune.com/coronavirus/ct-covid-19-pandemic-chicago-illinois-news-20200814-2uedd64x5rg5xitgzlhy73puxm-story.html&sa=U&ved=2ahUKEwi6s8zV4pvrAhXzdM0KHQVuBegQ0Y8FMAV6BAgFEAI&usg=AOvVaw3y07udsyhVU7B0L7pvu6v1',
         '/url?q=https://patch.com/illinois/chicago/brief-tornado-hits-rogers-park-derecho-blasts-chicago&sa=U&ved=2ahUKEwi6s8zV4pvrAhXzdM0KHQVuBegQxfQBMAZ6BAgEEAE&usg=AOvVaw3rpoX7cMzGTreDjlXUpSsm',
         '/url?q=https://patch.com/illinois/chicago/brief-tornado-hits-rogers-park-derecho-blasts-chicago&sa=U&ved=2ahUKEwi6s8zV4pvrAhXzdM0KHQVuBegQ0Y8FMAZ6BAgEEAI&usg=AOvVaw3td9bGhTonDxBdSLn8wRIY',
         '/url?q=https://abc7chicago.com/chicago-looting-police-mayor-lori-lightfoot-cpd/6370260/&sa=U&ved=2ahUKEwi6s8zV4pvrAhXzdM0KHQVuBegQxfQBMAd6BAgAEAE&usg=AOvVaw2JsJxYQKL-Sv-BTWgtheLs',
         '/url?q=https://abc7chicago.com/chicago-looting-police-mayor-lori-lightfoot-cpd/6370260/&sa=U&ved=2ahUKEwi6s8zV4pvrAhXzdM0KHQVuBegQ0Y8FMAd6BAgAEAI&usg=AOvVaw37cDH98rG8NVfZkNO-8hLJ',
         '/url?q=https://wgntv.com/news/macys-to-leave-water-tower-place-location/&sa=U&ved=2ahUKEwi6s8zV4pvrAhXzdM0KHQVuBegQxfQBMAh6BAgDEAE&usg=AOvVaw3K5elxa4JxzPvYzO806vZc',
         '/url?q=https://wgntv.com/news/macys-to-leave-water-tower-place-location/&sa=U&ved=2ahUKEwi6s8zV4pvrAhXzdM0KHQVuBegQ0Y8FMAh6BAgDEAI&usg=AOvVaw2yn6gGz7otLhpg0T4LWm2K',
         '/url?q=https://nypost.com/2020/08/13/pushback-in-chicago-as-blacks-are-sick-and-tired-of-looters-anarchists/&sa=U&ved=2ahUKEwi6s8zV4pvrAhXzdM0KHQVuBegQxfQBMAl6BAgCEAE&usg=AOvVaw1k5kPAAPayRbxFfXd0cO-J',
         '/url?q=https://nypost.com/2020/08/13/pushback-in-chicago-as-blacks-are-sick-and-tired-of-looters-anarchists/&sa=U&ved=2ahUKEwi6s8zV4pvrAhXzdM0KHQVuBegQ0Y8FMAl6BAgCEAI&usg=AOvVaw2EtGPZy4QBDX61FT81JgaI',
         '/search?q=chicago&ie=UTF-8&tbm=nws&ei=2hM3X7reJ_PptQaF3JXADg&start=10&sa=N',
         '/url?q=https://accounts.google.com/ServiceLogin%3Fcontinue%3Dhttps://www.google.com/search%253Fq%253Dchicago%2526tbm%253Dnws%26hl%3Den&sa=U&ved=0ahUKEwi6s8zV4pvrAhXzdM0KHQVuBegQxs8CCFc&usg=AOvVaw2UdTb6WMe54pWKVvmku14T',
         'https://www.google.com/preferences?hl=en&fg=1&sa=X&ved=0ahUKEwi6s8zV4pvrAhXzdM0KHQVuBegQ5fUCCFg',
         'https://policies.google.com/privacy?hl=en&fg=1',
         'https://policies.google.com/terms?hl=en&fg=1']

        google_status = [] 
        for link in links:
            google_status.append(google_scraper.non_google_links(link))
        assert 20 == sum(google_status)

    def test_valid_urls(self):
        n = 3
        result = google_scraper.google_top_results(n, '/search?q=chicago&tbm=nws')
        counter = 0
        for link in result:
            page = requests.get(link)
            if page.status_code == 200:
                counter += 1
        assert n == counter
