import spotipy
import json
import h5py
from spotipy.oauth2 import SpotifyClientCredentials
import sqlite3
from copy import deepcopy
from datetime import datetime


conn = sqlite3.connect('/users/bclark66/sp_data_for_tempo_test.db')
cur = conn.cursor()

client_credentials_manager = SpotifyClientCredentials(client_id="e90c5ed628d443819c60714f29cc8186",client_secret="e7632ab680d44aa3ab55434315075309")
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
regional_words = {'chinese', 'taiwan', 'traditional', 'dutch', 'euro', 'israeli', 'swedish', 'celtic',
'italian', 'french', 'argentine', 'latin', 'spanish', 'czech', 'luxembourgian', 'brazilian', 'hungarian',
'arab', 'german', 'danish', 'icelandic', 'glam', 'norwegian', 'turkish', 'irish', 'colombian',
'iraqi', 'thai', 'dominican', 'indian', 'persian', 'lebanese', 'polish', 'chilean', 'sertanejo',
'swiss', 'belarusian', 'bolivian', 'italo', 'garifuna', 'manila', 'vietnamese', 'indo', 'indonesian',
'singaporean', 'greek', 'pakistani', 'breton', 'syrian', 'mexican', 'finnish', 'pagan', 'viking',
'quebec', 'russian', 'romanian', 'wellington', 'cumbia', 'baile', 'latvian', 'serbian', 'slovak',
'regional', 'suomi', 'japanese', 'croatian', 'lithuanian', 'euskal', 'perth', 'estonian', 'bahamian',
'guinean', 'mande', 'belgian', 'yugoslav', 'portuguese', 'baltic', 'african', 'armenian', 'kosovan',
'jewish', 'medieval', 'rune', 'brit', 'slovenian', 'sudanese', 'malian', 'ilocano', 'gothenburg',
'pinoy', 'anime', 'korean', 'austrian', 'welsh', 'beninese', 'tunisian', 'slavic', 'algerian',
'bulgarian', 'malaysian', 'puerto', 'rican', 'concepcion', 'maltese', 'bristol', 'galician', 'ecuadorian',
'cook', 'islands', 'polynesian', 'peruvian', 'catalan', 'montreal', 'venezuelan', 'basque', 'panamanian',
'nordic', 'rome', 'punjabi', 'paraguayan', 'albanian', 'national'}

classical_words = {'baroque', 'chamber','classical', 'early music','opera', 'orchestra,romantic'}
jazz_words = {'bebop', 'big band', 'bop','fusion', 'jazz','swing','boogie','Dixieland','jive'}
rock_words = {'funk','blues','country', 'disco', 'emo', 'folk', 'grunge', 'indie', 'metal','punk', 'reggae', 'rock', 'screamo'}
hip_hop_words = {'electro', 'electronica','hip hop', 'house', 'industrial','rap', 'techno', 'trance', 'trap'}

def flatten_dict(d, result={}, prv_keys=[]):
    for k, v in d.items():
        #print("k  ",k)
        if isinstance(v, dict):
            flatten_dict(v, result, prv_keys + [k])
        else:
            result['.'.join(prv_keys + [k])] = v

    return result

def get_artist_id(yr,c,jz,r,h,letter):
    
    query =  letter + ' year:' + yr
    results = sp.search(query,type='album',limit=50)
    flat_result = flatten_dict(results)
    #print(flat_result.keys())
    #print(flat_result["tracks.total"]," ",flat_result["tracks.next"]," ",flat_result["tracks.offset"])
    
    total = flat_result["albums.total"]
    now = datetime.now()

    current_time = now.strftime("%H:%M:%S")
    
    print("starting year: ",yr,current_time,total)
    
    current = 0
    track_count = 0
    classical_tracks_count_needed = c
    jazz_tracks_count_needed = jz
    rock_tracks_count_needed = r
    hip_hop_tracks_count_needed = h
    classical_tracks_count = 0
    jazz_tracks_count = 0
    rock_tracks_count = 0
    hip_hop_tracks_count = 0

    while current < total:
        try:
            results = sp.search(query,type='album',limit=50,offset=current)
        except Exception as toomany:
            print("# of albums ",current," # of tracks ",track_count,toomany)
            #yr,new_current,new_classical_tracks_count,new_jazz_tracks_count,new_rock_tracks_count,new_hip_hop_tracks_count = get_artist_id(yr,c,jz,r,h)
            # classical_tracks_count += new_classical_tracks_count
            # jazz_tracks_count += new_jazz_tracks_count
            # rock_tracks_count += new_rock_tracks_count
            # hip_hop_tracks_count += new_hip_hop_tracks_count
            break

        flat_result = flatten_dict(results)
        x = 0
        

        for item in flat_result["albums.items"]:
            if 'Live' in item['name'] or 'live' in item['name']:
                continue
            ts = []
            #print("album",item['id'])
            ts.append(item["id"])
            ts.append(item["name"])
            ts.append(item["release_date"])
            ts.append(item["release_date_precision"])
            ts.append(item["total_tracks"])
            ts.append(item["type"])
            ts.append(' ')
            ts.append(' ')
            ts.append(item['href'])
            #trks.append(ts[i])
            
            #print('ts ',ts[i])
            trks = [[0] * 2 for x in range(item['total_tracks'])]
            try:
                tracks_result = sp.album_tracks(ts[0])
            except Exception as notrack:
                print("no tracks",notrack)
                tracks_result = {'items':[]}
            
            track_count = 0
            for track in tracks_result["items"]:
                if 'Live' in track['name'] or 'live' in track['name']:
                    continue 
                trks[track_count][0] = item['id']
                trks[track_count][1] = track['id']
                track_count += 1
                if track_count > 1:
                    break


            ta = [[0] * 2 for i in range(len(item["artists"]))]
            artists = [[0] * 7 for x in range(len(item['artists']))]
            j = 0
            for row in item["artists"]:
                ta[j][0] = item["id"]
                ta[j][1] = row["id"]
                try:
                    artist_result = sp.artist(row['uri'])
                except Exception as noartist:
                    print("no artist",noartist)
                    break
                #genres = set(artist_result["genres"])
                genre_list = []
                for term in artist_result["genres"]:
                    if term == 'hip hop':
                        genre_list.append(term)
                    else:
                        term_list = term.split(" ")
                        for word in term_list:
                            genre_list.append(word)
                genres = set(genre_list)
                genre_string = '::'
                genre_strizng = genre_string.join(genre_list)
                artists[j][0] = row["id"]
                artists[j][1] = genre_string
                artists[j][2] = artist_result["href"]
                artists[j][3] = artist_result['name']
                artists[j][4] = artist_result['popularity']
                artists[j][5] = artist_result['uri']
                artists[j][6] = artist_result['followers']['total']
                
                
                contains_regional_word = list(genres & regional_words)
                genre_count = 0
                if len(contains_regional_word) > 0:
                    print("ctw",genres)
                    continue
                contains_classical_word = list(genres & classical_words)
                contains_jazz_word = list(genres & jazz_words)
                contains_rock_word = list(genres & rock_words)
                contains_hip_hop_word = list (genres & hip_hop_words) 
                print("counts",classical_tracks_count,jazz_tracks_count,rock_tracks_count,hip_hop_tracks_count)

                if len(contains_classical_word) > 0 and classical_tracks_count < classical_tracks_count_needed:
                    genre_count += 1
                if len(contains_jazz_word) > 0 and jazz_tracks_count < jazz_tracks_count_needed:
                    genre_count += 1
                if len(contains_rock_word) > 0 and rock_tracks_count < rock_tracks_count_needed:
                    genre_count +=1
                if len(contains_hip_hop_word) > 0 and hip_hop_tracks_count < hip_hop_tracks_count_needed:
                    genre_count +=1
                
                if genre_count == 1:
                    try:
                        print("about to insert album",ts[0])
                        cur.execute('insert into album values (?,?,?,?,?,?,?,?,?)',ts)
                        conn.commit()
                        #print("about to insert album_artist",ta[j])
                        cur.execute('insert into album_artist values (?,?)',ta[j])
                        #print("about to insert album_track",trks)
                        cur.executemany('insert into album_track VALUES (?,?)', trks)
                        #print("about to insert artists",artists[j])                    
                        cur.execute('insert into artist values(?,?,?,?,?,?,?)',artists[j])
                    except Exception as badinsert:
                        pass
                        #print("bad insert",badinsert,ta[j][1])
                    if len(contains_classical_word) > 0:
                        classical_tracks_count += track_count
                    elif len(contains_jazz_word) > 0:
                        jazz_tracks_count += track_count
                    elif len(contains_rock_word) > 0:
                        rock_tracks_count += track_count
                    elif len(contains_hip_hop_word) > 0:
                        hip_hop_tracks_count += track_count

                    
                    break  
                else:
                    print("skipped genres",genres,genre_count,)  
                j += 1
                    

            # # c.executemany('insert into track_artist VALUES (?,?,?)', ta)
            # i += 1    
        offset = flat_result["albums.offset"]
        #c.executemany('INSERT INTO track_search VALUES (?,?,?)', ts)
        
        
        #conn.commit()
        current += 50
        #print(current)
    print("year",yr,"# of albums ",current," # of tracks ",classical_tracks_count,jazz_tracks_count,rock_tracks_count,hip_hop_tracks_count)
    return(yr,current,classical_tracks_count,jazz_tracks_count,rock_tracks_count,hip_hop_tracks_count)
i = 0
#for row in c2.execute('SELECT artist_name,count(*) FROM songs group by artist_id order by 2 desc'):
#for row in c2.execute('select tan.track_id, count(*) from track_search tan left outer join track_analysis ta on ta.track_id = tan.track_id and ta.track_id is null group by tan.track_id'):
    # if i > 60:
    #     break
    # #print(row)
    # artist = row[0]
    # get_artist_id(artist)
    # i += 1
jazz_needs = [[1974,7],[1978,9],[1979,15],[1980,39],[1981,23],[1982,13],[1983,17],[1984,20],[1985,2]]
yr = "1980"
for needed_year in range(1978,1979):
    for letter in ('a','e','i','o','u','y'):
    # nbr_needed = jazz_needs[needed_year][1]
    # yr = jazz_needs[needed_year][0]
        get_artist_id(str(needed_year),100,100,100,100,letter)
# for row in c.execute('select distinct track_id from track_artist where track_id not in (select distinct track_id from track_analysis)'):
#    trks.append(row[0])
#print(trks)

