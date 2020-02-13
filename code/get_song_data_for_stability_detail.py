import argparse
import sqlite3
import csv
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

conn = sqlite3.connect('/Users/bclark66/musi7100/sp_data_for_tempo.db')
conn2 = sqlite3.connect('/Users/bclark66/musi7100/sp_data_for_tempo.db')
c = conn.cursor()
c1 = conn2.cursor()



sql = "select t.track_id,t.start,t.duration,t.confidence from track_beat t where track_id in "
sql += "('3bRGevbopP3SRXCExhtoMk','2qYZPN1Frrp1KIaab3Dbt4','028pJgI2yCyGrhOfStge8l',"
sql += "'5dUY6JwWCdkaEJuDlvFCij','0KFAM8DHNyrJq4mcPQzPkR')"

tempo_analysis_df = pd.read_sql(sql,conn)
tempo_analysis_df.fillna(0)

tempo_analysis_df.sort_values(['track_id','start'],inplace=True)

# print('df ',tempo_analysis_df[['track_id','sec_tempo','sec_tempo_range']].head(100))
tempo_analysis_df.to_csv('song_data_beat_detail.csv')
#print(tempo_analysis_df.sec_tempo_diff_normalized.hist(bins=10))
print("unique ",tempo_analysis_df.track_id.nunique())
#print("id ",tempo_analysis_df.loc[tempo_analysis_df.track_id == '00AREEHn53hfNdh7HxuK6P','sec_tempo_range_normalized'])

    

        