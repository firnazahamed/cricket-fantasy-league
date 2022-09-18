import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

def extract_bowling_data(series_id: str, match_id:str) -> pd.DataFrame:
    """
    Scrapes and returns the bowling data from Cricinfo bowling scorecard
    """

    URL = f'https://www.espncricinfo.com/series/{series_id}/scorecard/{match_id}'
    page = requests.get(URL)
    bs = BeautifulSoup(page.content, 'lxml')
    table_body=bs.find_all('tbody')
    
    bowler_data = []
    for i, table in enumerate(table_body[1:4:2]):
        if len(table.find_all(True,{"class":"font-weight-bold match-venue"})) == 0:
            rows = table.find_all('tr')
            for row in rows:
                player_id_col = row.find_all('a', href=True)
                if len(player_id_col)>0:
                    player_id = player_id_col[0]['href'].split("-")[-1]
                    cols=row.find_all('td')
                    cols=[col.text.strip() for col in cols]
                    cols.extend([(i==0)+1, player_id])
                    bowler_data.append(cols)

    bowler_df = pd.DataFrame(bowler_data, columns = ['Name', 'Overs', 'Maidens', 'Runs', 'Wickets',
                                            'Econ', 'Dots', '4s', '6s', 'Wd', 'Nb', 'Team', 'Player_id'])

    return bowler_df

def extract_batting_data(series_id: str, match_id: str) -> pd.DataFrame:
    """
    Scrapes and returns the batting data from Cricinfo batting scorecard
    """
    URL = f'https://www.espncricinfo.com/series/{series_id}/scorecard/{match_id}'
    page = requests.get(URL)
    bs = BeautifulSoup(page.content, 'lxml')
    table_body=bs.find_all('tbody')
    
    batsmen_data = []
    for i, table in enumerate(table_body[0:4:2]):
        rows = table.find_all('tr')

        #Loop through each row in the batting scorecard 
        for row in rows:
            player_id_col = row.find_all('a', href=True)

            if len(player_id_col) > 0: # Valid row if there's a player referenced
                player_id = player_id_col[0]['href'].split("-")[-1]
                cols=row.find_all('td')
                cols=[x.text.strip() for x in cols]

                if cols[0].lower() in ['extras','total']: # Skip extras and total 
                    continue
                elif 'not bat' in cols[0]:
                    #Extract batsmen info from did not bat row and add to data
                    dnb_batsmen = cols[0].split('not bat: ')[1].split(',')
                    for j, batsman in enumerate(dnb_batsmen):
                        batsmen_data.append([re.sub(r"\W+", ' ', batsman.split("(c)")[0]).strip(), 
                        "DNB", 0, 0, 0, 0, 0, i+1, player_id_col[j]['href'].split("-")[-1]])
                elif cols[1] == 'absent hurt': #Edge case for absent hurt scenario 
                    batsmen_data.append([re.sub(r"\W+", ' ', cols[0].split("(c)")[0]).strip(), 
                    cols[1], 0, 0, 0, 0, 0, i+1, player_id])
                else: 
                    batsmen_data.append([re.sub(r"\W+", ' ', cols[0].split("(c)")[0]).strip(), 
                    cols[1], cols[2], cols[3], cols[5], cols[6], cols[7], i+1, player_id])

    batsmen_df = pd.DataFrame(batsmen_data, columns=["Name","Desc","Runs", "Balls", 
                                            "4s", "6s", "SR", "Team","Player_id"])

    return batsmen_df
