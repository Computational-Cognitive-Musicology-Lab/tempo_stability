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
target_sql = 'select track_id from track'
for row in c1.execute(target_sql):
    targets.append(row[0])
print("len ",len(targets))


#fname = open("song_data.csv","w",newline='')
# songwriter = csv.writer(fname,delimiter='|',quotechar='|',quoting=csv.QUOTE_MINIMAL)
# songwriter.writerow(['ID','Title','Song Tempo','Time Signature','Secstart','Seclen','SecTempo','SecKey','SecMode','Barstart','Barlen','BarConf'])

sql = "select t.track_id,t.name,t.popularity,tf.tempo,tf.time_signature,tf.duration_ms, "
sql = sql + 'ts.start as secstart,ts.duration as seclen,ts.tempo as sec_tempo,ts.key as seckey,ts.mode as secmode, '
sql = sql + 'a.label,a.popularity as album_popularity,ar.genres,ar.name as artist_name,ar.popularity as artist_popularity,ar.followers, '
sql = sql + 'substr(a.release_date,1,4) '
sql = sql + 'from track t left outer join ' 
sql = sql + 'track_feature tf on t.track_id = tf.track_id left outer JOIN '
sql = sql + 'track_section ts on ts.track_id = t.track_id left outer JOIN '
sql = sql + 'album_track at on at.track_id = t.track_id left outer join '
sql = sql + 'album a on at.album_id = a.id left outer join '
sql = sql + 'album_artist aa on aa.album_id = a.id left outer join '
sql = sql + 'artist ar on ar.id = aa.artist_id '  

#sql = sql + "where t.track_id = '" + track_id + "' "
sql = sql + "group by t.track_id,t.name,t.popularity,tf.tempo,tf.time_signature, "
sql = sql + "ts.start, ts.duration,ts.tempo,ts.key,ts.mode,a.label,a.popularity,ar.genres,ar.name,ar.popularity,ar.followers "
#sql = sql + "tb.start ,tb.duration,tb.confidence " 
#for track_id in targets:    
    # for row in c.execute(sql):
    #     csvrow = []
    #     for field in range(len(row)):
    #         csvrow.append(row[field])
    #     songwriter.writerow(csvrow)
tempo_analysis_df = pd.read_sql(sql,conn)
tempo_analysis_df.fillna(0)

tempo_analysis_df.sort_values(['track_id','secstart'],inplace=True)
tempo_analysis_df['zero_tempo'] = False
tempo_analysis_df['tempo_shift'] = False
tempo_analysis_df.loc[tempo_analysis_df['sec_tempo'] == 0,'zero_tempo'] = True
tempo_analysis_df.loc[tempo_analysis_df['zero_tempo'] == True,'sec_tempo'] = tempo_analysis_df.groupby(['track_id'])['sec_tempo'].transform('median')
tempo_analysis_df['song_zero_tempo'] = False
zero_tempos = tempo_analysis_df.loc[tempo_analysis_df.zero_tempo == True,['track_id']]
#print('zt ',zero_tempos)
tempo_analysis_df.loc[tempo_analysis_df['track_id'].isin(zero_tempos.track_id),'song_zero_tempo'] = True
tempo_analysis_df['sec_tempo_max'] = tempo_analysis_df.groupby(['track_id'])['sec_tempo'].transform('max') 
tempo_analysis_df['sec_tempo_min'] = tempo_analysis_df.groupby(['track_id'])['sec_tempo'].transform('min') 
tempo_analysis_df['sec_tempo_mean'] = tempo_analysis_df.groupby(['track_id'])['sec_tempo'].transform('mean')
tempo_analysis_df['sec_tempo_range'] = tempo_analysis_df['sec_tempo_max'] - tempo_analysis_df['sec_tempo_min'] 
tempo_analysis_df['sec_tempo_range_normalized'] = tempo_analysis_df['sec_tempo_range'] / tempo_analysis_df['sec_tempo_max']
tempo_analysis_df['sec_tempo_diff'] = tempo_analysis_df.groupby('track_id')['sec_tempo'].diff()
tempo_analysis_df['sec_tempo_diff'].fillna(0,inplace=True)

tempo_analysis_df['sec_tempo_first'] = tempo_analysis_df.groupby('track_id')['sec_tempo'].transform('first')
tempo_analysis_df['sec_tempo_last'] = tempo_analysis_df.groupby('track_id')['sec_tempo'].transform('last')
tempo_analysis_df['sec_tempo_ratio'] = (tempo_analysis_df['sec_tempo_first'] - tempo_analysis_df['sec_tempo_last']) / tempo_analysis_df['sec_tempo_last']
#tempo_analysis_df.loc[tempo_analysis_df.groupby(['track_id']).first()['sec_tempo_diff']] = 0
tempo_analysis_df['sec_tempo_diff_normalized'] = tempo_analysis_df['sec_tempo_diff'] / tempo_analysis_df['sec_tempo_max'] 
tempo_analysis_df['tempo_shift'] = np.where(tempo_analysis_df['sec_tempo_diff_normalized'] > .1,True,False)
tempo_analysis_df['double_time'] = np.where(tempo_analysis_df.sec_tempo_diff - tempo_analysis_df.sec_tempo  > -10,True,False)
tempo_analysis_df['triple_time'] = np.where(tempo_analysis_df.sec_tempo_diff - (tempo_analysis_df.sec_tempo * 2 / 3) > -10,True,False)
tempo_analysis_df.loc[tempo_analysis_df.triple_time == True,'double_time'] = False
tempo_analysis_df['genre_count'] = tempo_analysis_df.genres.str.count("::")
tempo_analysis_df['genre_list'] = tempo_analysis_df.genres.str.split("::")
tempo_analysis_df = tempo_analysis_df.explode('genre_list')
# print('df ',tempo_analysis_df[['track_id','sec_tempo','sec_tempo_range']].head(100))
tempo_analysis_df.to_csv('song_data_section_tempo_with_artists.csv')
#print(tempo_analysis_df.sec_tempo_diff_normalized.hist(bins=10))
print("unique ",tempo_analysis_df.track_id.nunique())
#print("id ",tempo_analysis_df.loc[tempo_analysis_df.track_id == '00AREEHn53hfNdh7HxuK6P','sec_tempo_range_normalized'])

    

        