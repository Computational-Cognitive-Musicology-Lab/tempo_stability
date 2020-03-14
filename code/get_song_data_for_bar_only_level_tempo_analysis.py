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
targets = []
# with open('./max martin songs.csv') as csvfile:
#         readCSV = csv.reader(csvfile, delimiter=',')
#         next(readCSV, None)
#         for row in readCSV:
#             if len(row[4]) > 11:
#                 targets.append(row[4].replace("spotify:track:",""))
target_sql = 'select track_id from track limit 10'
for row in c1.execute(target_sql):
    targets.append(row[0])
print("len ",len(targets))


#fname = open("song_data.csv","w",newline='')
# songwriter = csv.writer(fname,delimiter='|',quotechar='|',quoting=csv.QUOTE_MINIMAL)
# songwriter.writerow(['ID','Title','Song Tempo','Time Signature','Secstart','Seclen','SecTempo','SecKey','SecMode','Barstart','Barlen','BarConf'])

sql = "select t.track_id,t.name,t.popularity,tf.tempo,tf.time_signature,tf.duration_ms, "
sql = sql + 'ts.start as secstart,ts.duration as seclen,ts.tempo as sec_tempo,ts.key as seckey,ts.mode as secmode, '
sql = sql + 'a.label,a.popularity as album_popularity, '
#sql = sql + 'ar.genres,ar.name as artist_name,ar.popularity as artist_popularity,ar.followers, '
sql = sql + 'tb.start as bar_start,tb.duration as bar_duration,tb.confidence as bar_confidence,'
sql = sql + 'substr(a.release_date,1,4) '
sql = sql + 'from track t left outer join ' 
sql = sql + 'track_feature tf on t.track_id = tf.track_id left outer JOIN '
sql = sql + 'track_section ts on ts.track_id = t.track_id left outer JOIN '
sql = sql + 'track_bar tb on tb.track_id = t.track_id left outer join '
sql = sql + 'album_track at on at.track_id = t.track_id left outer join '
sql = sql + 'album a on at.album_id = a.id '
#sql = sql + 'left outer join '
#sql = sql + 'album_artist aa on aa.album_id = a.id left outer join '
#sql = sql + 'artist ar on ar.id = aa.artist_id '  

#sql = sql + "where t.track_id = '" + track_id + "' "
sql = sql + "group by t.track_id,t.name,t.popularity,tf.tempo,tf.time_signature, "
sql = sql + "ts.start, ts.duration,ts.tempo,ts.key,ts.mode,tb.start,tb.duration,tb.confidence "
sql = sql + "order by t.track_id,secstart,bar_start limit 1000"
#sql = sql + "a.label,a.popularity,ar.genres,ar.name,ar.popularity,ar.followers "
#sql = sql + "tb.start ,tb.duration,tb.confidence " 
#for track_id in targets:    
    # for row in c.execute(sql):
    #     csvrow = []
    #     for field in range(len(row)):
    #         csvrow.append(row[field])
    #     songwriter.writerow(csvrow)

sql2 = """select t.track_id,ts.start as secstart,'section' as type,substr(a.release_date,1,4) as release_date 
    from track t left outer join album_track at on at.track_id = t.track_id left outer join 
    album a on at.album_id = a.id left outer join 
        track_section ts on ts.track_id = t.track_id order by t.track_id,secstart"""
        
sql3 = """ select t.track_id,tb.start as bar_start,tb.duration as bar_duration,'bar' as type from track t left outer join 
        track_bar tb on tb.track_id = t.track_id order by t.track_id, bar_start"""


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
df2.to_csv('song_data_section_tempo_with_bars_only.csv')



        