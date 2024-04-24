import pandas as pd
import re
import json

COLUMN_LIST_MAP = {
    'Performance_Gls': 'summary',
    'Medium_Att': 'passing',
    'Pass Types_TB': 'passing_types',
    'Tackles_Mid 3rd': 'defense',
    'Carries_PrgDist': 'possession',
    'Aerial Duels_Lost': 'misc',
    'Shot Stopping_Saves': 'goalkeepers',
    'Body Part': 'shots'
}

class Match:

    def __init__(self,home,away,url):
        self.url = url
        self.raw_tables = []
        self.home_team = home
        self.away_team = away
        self.lineup = []
        self.non_lineup = []
        self.semi_cleaned =[]
        self.others = []
        self.cleaned_stats = [{'home':self.home_team,'away':self.away_team}]


    def read_table(self):
        self.raw_tables = pd.read_html(self.url)

    @staticmethod
    def transform_levels(old_columns):
        new_columns = []
        for first_level, second_level in old_columns:
            if 'Unnamed' in first_level:
                new_columns.append(second_level)
            else:
                new_columns.append(f"{first_level}_{second_level}")
        return new_columns
    
    def level_transformer(self):
        for table in self.raw_tables:
            is_multilevel = isinstance(table.columns, pd.MultiIndex)
            if is_multilevel:
                table.columns = self.transform_levels(table.columns)        

    def split_tables(self):
        
        for table in self.raw_tables:
            pattern = re.compile(r'\(\d+-\d+-[^)]+\).*')
            columns_with_pattern = [col for col in table.columns \
                                    if pattern.search(col)]
            if columns_with_pattern:
                # Removing the pattern from the column names
                new_columns = [pattern.sub('', col).replace(' ', '') if col \
                               in columns_with_pattern else col for col \
                                in table.columns]
                # Rename the first column to 'number'
                new_columns[0] = 'number'
                new_columns[1].replace(' ','')
                table.columns = new_columns
                bench_index = table[table['number'] == 'Bench'].index[0]
                table['status'] = 'Starting'
                table.loc[bench_index:, 'status'] = 'Bench'
                table.drop(bench_index, inplace=True)
                table['team'] = table.columns[1]
                table.rename(columns={table.columns[1]: 'name'}, inplace=True)
                if 'status' in table.columns:
                    self.lineup.append(table)
            else:
                self.non_lineup.append(table)

    def table_merger(self):
        for df in self.non_lineup:
            if 'Squad' in df.columns:
                self.semi_cleaned.append(df)
                continue
            for each_df in self.lineup:
                try:
                    result = pd.merge(df, each_df, left_on='Player', \
                                      right_on='name', how='inner')
                    if len(result) < 2 :
                        continue
                    self.semi_cleaned.append(result[['team'] + \
                                                    list(df.columns)])
                except:
                    continue
  
    def table_sorter(self):

        for table in self.semi_cleaned:
            col_names = table.columns
            try:
                team_name = table['team'].unique()[0]
            except:
                if self.home_team in table['Squad'].unique() and \
                    self.away_team in table['Squad'].unique():
                    team_name = 'Combined shots'
                else:
                    team_name = table['Squad'].mode()[0]

            for key in COLUMN_LIST_MAP.keys():
                if key in col_names:
                    self.cleaned_stats.append\
                        ({f'{team_name}_{COLUMN_LIST_MAP[key]}': \
                          json.loads(table.to_json(orient='records'))})
                else:
                    self.others.append({team_name: \
                                        json.loads(table.\
                                                   to_json(orient='records'))})
                
    def run_all(self):
        self.read_table()
        self.level_transformer()
        self.split_tables()
        self.table_merger()
        self.cleaned_stats.append({'lineup': \
                                   [json.loads(df.\
                                               to_json(orient='records')) \
                                                for df in self.lineup]})
        self.table_sorter()
        return self.cleaned_stats
