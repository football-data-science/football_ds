import sys
import json
import lxml.html
import requests
from urllib.parse import urlparse
from pathlib import Path
import pandas as pd
import re

class Match:

    def __init__(self,home,away,url):
        self.url = url
        self.raw_tables = []
        self.home_team = home
        self.away_team = away
        self.summary = []
        self.passing= []
        self.passing_types = []
        self.misc = []
        self.defense = []
        self.posession = []
        self.goalkeepers =[]
        self.lineup = []
        self.non_lineup = []
        self.semi_cleaned =[]
        self.shots = []
        self.others = []

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
            if 'Performance_Gls' in col_names:
                self.summary.append({team_name:table})
            elif 'Medium_Att' in col_names:
                self.passing.append({team_name:table})
            elif 'Pass Types_TB' in col_names:
                self.passing_types.append({team_name:table})
            elif 'Tackles_Mid 3rd' in col_names:
                self.defense.append({team_name:table})
            elif 'Carries_PrgDist' in col_names:
                self.posession.append({team_name:table})
            elif 'Aerial Duels_Lost' in col_names:
                self.misc.append({team_name:table})
            elif 'Shot Stopping_Saves' in col_names:
                self.goalkeepers.append({team_name:table})
            elif 'Body Part' in col_names:
                self.shots.append({team_name:table})
            else:
                self.others.append({team_name:table})
                
    def run_all(self):
        self.read_table()
        self.level_transformer()
        self.split_tables()
        self.table_merger()
        self.table_sorter()
            
