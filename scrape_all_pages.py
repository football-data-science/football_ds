from pathlib import Path
import json
from scrape_page import Match
import time

dir = Path(__file__).parent 
RAW_DATA_PATH = dir /'raw_data/match_links.json'

FIN_DATA_PATH = dir /'raw_data/stats.json'


def scrape_all_pages():

    with open(RAW_DATA_PATH, 'r') as f:
        raw_links = json.load(f)

    all_matches_data = []
    count = 0
    for each_match in raw_links:
        print("creating match object")
        match_object = Match(each_match['home'],each_match['away'],each_match['link'])
        print('home team: ', match_object.home_team,'away team:', match_object.away_team)
        cleaned_data = match_object.run_all()
        print('run successful')
        if count <= 3:
            print(cleaned_data)
        all_matches_data.append(cleaned_data)
        count += 1
        print(f'scraped {count} matches')
        time.sleep(1)

    with open(FIN_DATA_PATH,"w") as f:
        json.dump(all_matches_data, f, indent=1)  


if __name__ == "__main__":
    scrape_all_pages()