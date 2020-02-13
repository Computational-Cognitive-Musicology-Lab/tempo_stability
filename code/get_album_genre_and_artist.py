import spotipy
import json
from spotipy.oauth2 import SpotifyClientCredentials
import sqlite3
from copy import deepcopy
import spotifyapi as spapi

conn = sqlite3.connect('sp_data_for_tempo.db')
c = conn.cursor()
conn2 = sqlite3.connect('sp_data_for_tempo.db')
c2 = conn2.cursor()
client_credentials_manager = SpotifyClientCredentials(client_id="e90c5ed628d443819c60714f29cc8186",client_secret="e7632ab680d44aa3ab55434315075309")
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

artist_sql = 'select distinct artist_id from album_artist aa where aa.artist_id not in (select id from artist)'
i = 0
artist_ids = []
for row in c.execute(artist_sql):
    artist_ids.append(row[0])
for row in artist_ids:
    try:
        artist = sp.artist(row)
    except Exception as ap:
        print("artist ",ap, row)
        continue
        
    id = row
    uri = artist['uri']
    followers = artist['followers']['total']
    href = artist['href']
    genres = artist['genres']
    genre_string = '::'
    genre_string = genre_string.join(genres)
    name = artist['name']
    popularity = artist['popularity']
    #print("artist ",id)
    
    c2.execute('insert into artist values (?,?,?,?,?,?,?)',[id,genre_string,href,name,popularity,uri,followers])
    conn2.commit()

genre_sql = 'select distinct id from album'
album_ids = []
for row in c.execute(genre_sql):
    album_ids.append(row[0])
i = 0
for row in album_ids:
    try:
        album = sp.album(row)
    except Exception as al:
        print("al ",al, row)
    id = row
    #print('genres ',album['genres'])
    for genre in album['genres']:
        c2.execute('insert into album_genre values(?,?)',[id,genre])
        conn2.commit()
    

