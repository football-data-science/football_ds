import sys
import json
import lxml.html
import requests
from urllib.parse import urlparse
from pathlib import Path

URL = "https://fbref.com/en/comps/9/schedule/Premier-League-Scores-and-Fixtures"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36"
}   

dir = Path(__file__).parent 
RAW_DATA_PATH = dir /'raw_data/match_links.json'

class Get_links:

    def __init__(self,URL,file_store_path):
        self.url = URL
        self.headers = HEADERS
        self.response_tree = None
        self.storage_path = file_store_path
        self.link_data = None

    @staticmethod    
    def make_link_absolute(rel_url, current_url):
        """
        Given a relative URL like "/abc/def" or "?page=2"
        and a complete URL like "https://example.com/1/2/3" this function will
        combine the two yielding a URL like "https://example.com/abc/def"

        Parameters:
            * rel_url:      a URL or fragment
            * current_url:  a complete URL used to make the request that 
            contained a link to rel_url

        Returns:
            A full URL with protocol & domain that refers to rel_url.
        """
        url = urlparse(current_url)
        if rel_url.startswith("/"):
            return f"{url.scheme}://{url.netloc}{rel_url}"
        elif rel_url.startswith("?"):
            return f"{url.scheme}://{url.netloc}{url.path}{rel_url}"
        else:
            return rel_url
    
    def get_links(self):
        response = requests.get(self.url, headers = self.headers)
        if response.status_code != 200:
            print(f"error with status code {response.status_code}")
            return 
        self.response_tree = lxml.html.fromstring(response.text)
        rows = self.response_tree.cssselect("#sched_2023-2024_9_1 > tbody > tr")
        url_full = []
        for row in rows:
            for td in row.cssselect('td'):
                away_node = td.cssselect('td[data-stat="away_team"]')
                home_node = td.cssselect('td[data-stat="home_team"]')
                match_link = td.cssselect('td[data-stat="match_report"]')
                if away_node!= []:
                    try:
                        away_name = away_node[0].cssselect('a')[0].text
                    except:
                        continue
                if home_node!= []:
                    try:
                        home_name = home_node[0].cssselect('a')[0].text
                    except:
                        continue
                if match_link != []:
                    try:
                        link = match_link[0].cssselect('a')[0].get('href')
                    except:
                        continue
                    temp_dict = {'home':home_name, 'away': away_name, \
                            'link':self.make_link_absolute(link, self.url)}
                    url_full.append(temp_dict)
        self.link_data = url_full

    def json_creator(self):
        with open(str(self.storage_path), "w") as f:
            json.dump(self.link_data, f, indent=1)

    def run_all(self):
        self.get_links()
        self.json_creator()
        print(f"successfully created the links json and stored in \
              {RAW_DATA_PATH} ")

if __name__ == "__main__":
    page = Get_links(URL, RAW_DATA_PATH)
    page.run_all()
