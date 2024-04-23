def json_loader(self):
    with open(str(self.storage_path), "r") as f:
        load_json = json.load(f)


URL = "https://fbref.com/en/comps/9/schedule/Premier-League-Scores-and-Fixtures"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36"
}   
dir = Path(__file__).parent 
RAW_DATA_PATH = dir /'raw_data/match_links.json'

