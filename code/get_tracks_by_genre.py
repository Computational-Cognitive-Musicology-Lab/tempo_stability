import spotipy
import json
import h5py
from spotipy.oauth2 import SpotifyClientCredentials
import sqlite3
from copy import deepcopy
from datetime import datetime


conn = sqlite3.connect('/users/bclark66/sp_data_for_tempo_test1922.db')
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

classical_words = ['classical','romantic','orchestra','baroque', 'chamber','early music','opera', ]
jazz_words = ['jazz','big band','bebop','bop','fusion','swing','boogie','Dixieland','jive']
rock_words = ['rock','metal','indie','punk','disco','reggae', 'grunge','funk','screamo','emo']
blues_words = ['blues']
country_words = ['country','folk','traditional']
hip_hop_words = ['hip-hop','rap','trap','hip hop']
electronic_words = ['electronica','techno','electro','house','industrial','trance']
def flatten_dict(d, result={}, prv_keys=[]):
    for k, v in d.items():
        #print("k  ",k)
        if isinstance(v, dict):
            flatten_dict(v, result, prv_keys + [k])
        else:
            result['.'.join(prv_keys + [k])] = v

    return result

def get_artist_id(yr,c,term,category):
    if len(term.split(" ")) > 1:
        query = 'genre:' + '"' + term + '" ' + yr
    else:
        query =  'genre:' + term + ' year:' + yr
    results = sp.search(query,type='track',limit=50)
    flat_result = flatten_dict(results)
    #print(flat_result.keys())
    #print(flat_result["tracks.total"]," ",flat_result["tracks.next"]," ",flat_result["tracks.offset"])
    
    total = flat_result["tracks.total"]
    
    now = datetime.now()

    current_time = now.strftime("%H:%M:%S")
    
    print("starting year: ",yr,current_time,term,total)
    
    current = 0
    track_count = 0
    track_count_needed = c
    

    while current < total:
        try:
            results = sp.search(query,type='track',limit=50,offset=current)
        except Exception as toomany:
            #print("# of albums ",current," # of tracks ",track_count,toomany)
            #yr,new_current,new_classical_tracks_count,new_jazz_tracks_count,new_rock_tracks_count,new_hip_hop_tracks_count = get_artist_id(yr,c,jz,r,h)
            # classical_tracks_count += new_classical_tracks_count
            # jazz_tracks_count += new_jazz_tracks_count
            # rock_tracks_count += new_rock_tracks_count
            # hip_hop_tracks_count += new_hip_hop_tracks_count
            break

        flat_result = flatten_dict(results)
        x = 0
        

        for item in flat_result["tracks.items"]:
            #print("keys",item.keys())
            if 'Live' in item['name'] or 'live' in item['name']:
                #print("live",item['name'])
                continue
            ts = []
            #print("album",item['id'])
            if int(item["album"]['release_date'][0:4]) != int(yr):
                #print("actual date",int(item["album"]['release_date'][0:4]))
                continue
            all_genres = []
            for artist in item["artists"]:
                try: 
                    current_artist = sp.artist(artist["id"])
                    current_genres = current_artist["genres"]
                    for g in current_genres:
                        all_genres = all_genres + current_genres
                except Exception as bad_artist:
                    print("bad_artist for",item["id"], bad_artist)
                    continue
            if term not in all_genres:
                #print("wrong genre",all_genres)
                continue



            ts.append(item["id"])
            ts.append(item['uri'])
            ts.append(item['duration_ms'])
            ts.append(item['type'])
            ts.append(item["name"])
            ts.append(item['popularity'])
            ts.append(item['explicit'])
            ts.append(item['href'])
            ts.append(term)
            ts.append(int(yr))
            ts.append(category)
            
            
            
            try:
                #print("about to insert album",ts[0])
                cur.execute('insert into track values (?,?,?,?,?,?,?,?,?,?,?)',ts)
                conn.commit()
            except Exception as badtrack:           
                print("bad track",badtrack)
                continue  
            track_count += 1
            if track_count > c:
                break        

            # # c.executemany('insert into track_artist VALUES (?,?,?)', ta)
            # i += 1    
        offset = flat_result["tracks.offset"]
        if track_count > c:
            break
        
        current += 50
        #print(current)
    
    return(yr,current,track_count)
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
for needed_year in range(1920,2021):
    needed_count = 100
    for term in classical_words:
        yr,current,count = get_artist_id(str(needed_year),needed_count,term,'classical')
        needed_count -= count
        if needed_count <= 0:
            break
    needed_count = 100
    for term in jazz_words:
        yr,current,count = get_artist_id(str(needed_year),needed_count,term,'jazz')
        needed_count -= count
        if needed_count <= 0:
            break
    needed_count = 100
    for term in rock_words:
        yr,current,count = get_artist_id(str(needed_year),needed_count,term,'rock')
        needed_count -= count
        if needed_count <= 0:
            break
    needed_count = 100
    for term in blues_words:
        yr,current,count = get_artist_id(str(needed_year),needed_count,term,'blues')
        needed_count -= count
        if needed_count <= 0:
            break
    needed_count = 100
    for term in country_words:
        yr,current,count = get_artist_id(str(needed_year),needed_count,term,'country')
        needed_count -= count
        if needed_count <= 0:
            break
    needed_count = 100
    for term in hip_hop_words:
        yr,current,count = get_artist_id(str(needed_year),needed_count,term,'hip hop')
        needed_count -= count
        if needed_count <= 0:
            break
    needed_count = 100
    for term in electronic_words:
        yr,current,count = get_artist_id(str(needed_year),needed_count,term,'electronic')
        needed_count -= count
        if needed_count <= 0:
            break
# for row in c.execute('select distinct track_id from track_artist where track_id not in (select distinct track_id from track_analysis)'):
#    trks.append(row[0])
#print(trks)

