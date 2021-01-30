import spotipy
import json
import h5py
from spotipy.oauth2 import SpotifyClientCredentials
import sqlite3
#conn = sqlite3.connect('sp_data.db')
conn = sqlite3.connect('/users/bclark66/sp_data_for_tempo_test2.db')
c = conn.cursor()
client_credentials_manager = SpotifyClientCredentials(client_id="e90c5ed628d443819c60714f29cc8186",client_secret="e7632ab680d44aa3ab55434315075309")
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
# trk = sp.track("spotify:track:0hCB0YR03f6AmQaHbwWDe8")
# aud = sp.audio_analysis("spotify:track:0hCB0YR03f6AmQaHbwWDe8")
#audobj = json.load(aud)
# numsegs = 0
# for x in aud['segments']:
#     print(x['start'])
#     print(x['duration'])
#     numsegs += 1
def flatten_dict(d, result={}, prv_keys=[]):
    for k, v in d.items():
        print("k  ",k)
        if isinstance(v, dict):
            flatten_dict(v, result, prv_keys + [k])
        else:
            result['.'.join(prv_keys + [k])] = v

    return result





def get_audio_analysis(track_id):
    #results = sp.audio_analysis('spotify:track:06JmNnH3iXKENNRKifqu0v')
    try:
        results = sp.audio_analysis(track_id)
    except Exception as noData:
        return("no data for ",track_id)

    #print("results keys ",results.keys())
    if results is None:
        return("no data")
    else:
        flat_result = flatten_dict(results)
    track_bar = []
    
    for x in range(len(flat_result['bars'])):
        s = flat_result['bars'][x]['start']
        d = flat_result['bars'][x]['duration']
        conf = flat_result['bars'][x]['confidence']
        track_bar.append([track_id,s,d,conf])
    try:
        print("inserting",track_id)
        c.executemany('INSERT INTO track_bar VALUES (?,?,?,?)', track_bar)
        conn.commit()
    except Exception as insertproblem:
        print("insert bar",insertproblem)


    
    

track_sql = "select track_id from track where track_id not in (select distinct track_id from track_bar)"
targets = []
for row in c.execute(track_sql):
    targets.append(row[0])
for track in targets:
    get_audio_analysis(track)