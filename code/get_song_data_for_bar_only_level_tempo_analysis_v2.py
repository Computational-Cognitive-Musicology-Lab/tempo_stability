import argparse
import sqlite3
import csv
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

conn = sqlite3.connect('/users/bclark66/sp_data_for_tempo_test2.db')
c = conn.cursor()

        
sql3 = """ select t.track_id,tb.start as bar_start,tb.duration as bar_duration,  
        t.year as release_date,t.popularity,t.category,popularity as artist_popularity
        from track t left outer join 
        track_bar tb on tb.track_id = t.track_id 
        order by t.track_id, bar_start"""


#df1 = pd.read_sql(sql2,conn)
#df1 = df1.rename(columns={'secstart':'start'})
#df1['secname'] = df1.type + df1.start.astype(str)


df2 = pd.read_sql(sql3,conn)
df2 = df2.rename(columns={'bar_start':'start'})

#df1 = df1.merge(df2,how='outer',left_on=['track_id','start','type'],right_on=['track_id','start','type']).reset_index(drop=True)
#df1 = df1.sort_values(['track_id','start']).reset_index(drop=True)
#df1['secname'].fillna(method='ffill',inplace=True)
df2['bar_mean'] = df2.groupby('track_id')['bar_duration'].transform('mean')
df2['bar_stdev'] = df2.groupby('track_id')['bar_duration'].transform('std')
df2['bar_stdev_normalized'] = df2['bar_stdev'] / df2['bar_mean']
df2['bar_max'] = df2.groupby('track_id')['bar_duration'].transform('max')
df2['bar_min'] = df2.groupby('track_id')['bar_duration'].transform('min')
df2['bar_diff'] = df2.groupby('track_id')['bar_duration'].diff()
df2['bar_diff'].fillna(0,inplace=True)
df2['bar_range'] = df2['bar_max'] - df2['bar_min']
df2['bar_range_normalized'] = df2['bar_range'] / df2['bar_mean']
df2['bar_diff_normalized'] = df2['bar_diff'] / df2['bar_mean']
df2['bar_diff_stdev'] = df2.groupby('track_id')['bar_diff'].transform('std')
df2['region_5pct'] = df2['bar_diff_normalized'].abs() > .05
df2['region_2pct'] = df2['bar_diff_normalized'].abs() > .025
df2['region_5pct'] = df2['region_5pct'].astype('int')
df2['region_2pct'] = df2['region_2pct'].astype('int')
df2['region_5pct_count'] = df2.groupby('track_id')['region_5pct'].transform('sum')
df2['region_2pct_count'] = df2.groupby('track_id')['region_2pct'].transform('sum')
df2['region_5pct_cumsum'] = df2.groupby('track_id')['region_5pct'].transform('cumsum')
df2['region_2pct_cumsum'] = df2.groupby('track_id')['region_2pct'].transform('cumsum')
df2['bar_count'] = df2.groupby('track_id')['region_5pct'].transform('count')
df2['region_5pct_bar_count'] = df2.groupby(['track_id','region_5pct_cumsum'])['region_5pct'].transform('count')
df2['region_2pct_bar_count'] = df2.groupby(['track_id','region_2pct_cumsum'])['region_5pct'].transform('count')
#df2 = df2.groupby('track_id')['region_1pct'].apply(lambda x: (x == 'TRUE').sum()).reset_index(name='nbr_regions_1pct')
#print("df2 ",df2[df2.bar_diff_normalized.gt(.05).groupby(df2.track_id).transform('any')])
# indexnames = df2[df2['type'] == 'bar'].index
# df2.drop(indexnames,inplace=True)
df2 = df2.drop(columns=['start','bar_duration','bar_diff','bar_diff_normalized','region_5pct','region_2pct'])
df2 = df2.drop_duplicates()
df2.to_csv('song_data_tempo_with_bars_onlyv2.csv')



        