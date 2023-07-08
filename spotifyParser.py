#
 # This file is part of the SpotifyHistoryParser distribution (https://github.com/Chareste/SpotifyHistoryParser).
 # Copyright (c) 2023 Chareste.
 #
 # This program is free software: you can redistribute it and/or modify
 # it under the terms of the GNU General Public License as published by
 # the Free Software Foundation, version 3.
 #
 # This program is distributed in the hope that it will be useful, but
 # WITHOUT ANY WARRANTY; without even the implied warranty of
 # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
 # General Public License for more details.
 #
 # You should have received a copy of the GNU General Public License
 # along with this program. If not, see <http://www.gnu.org/licenses/>.
 #
import json
import os

import configparser
import requests
import urllib.parse
from pathlib import Path


print("Welcome to the Spotify Parser for your last year's data!")
print("It's VERY important to read the README.txt and follow accordingly.")
print("Press enter to continue or ctrl+C to exit.")
input()

config = configparser.ConfigParser()
config.read('settings.ini')
config.sections()

d ={
    "grant_type": "client_credentials",
    "client_id": config['SETTINGS']['clientID'],
    "client_secret": config['SETTINGS']['clientSecret']
}
if (d["client_id"] == "YOUR_CLIENT_ID") or (d["client_secret"] == "YOUR_CLIENT_SECRET"):
    print("Check if you have put your ID and secret in the program and try again.")
    exit(1)

api_key = requests.post("https://accounts.spotify.com/api/token", data = d).json()["access_token"]

session = requests.Session()
session.headers.update({"Authorization": f"Bearer  {api_key}"})

# loading StreamingHistory
with open(os.getcwd()+'/MyData/StreamingHistory0.json') as json_file:
    filemap = json.load(json_file)

filesNr = int(config['SETTINGS']['filesNumber'])
for x in range(1, filesNr):
    with open(os.getcwd() + '/MyData/StreamingHistory'+str(x)+'.json') as json_filex:
        filemap += json.load(json_filex)


dump_path = Path(os.getcwd()+'/out/dump/dump.json')
if dump_path.is_file():
    with open(dump_path) as dump_file:
        songdatini = json.load(dump_file)
else:
    songdatini = {}

err_path = Path(os.getcwd() + '/out/dump/error.json')
if err_path.is_file():
    with open(err_path) as err_file:
        errors = json.load(err_file)
else:
    errors = {}


addinf_path = Path(os.getcwd() + '/out/dump/additionalInfo.json')
if addinf_path.is_file():
    with open(addinf_path) as addinf_file:
        additionalInfo = json.load(addinf_file)
else:
    with open(os.getcwd()+"/MyData/Identity.json") as id_file:
        identifier = json.load(id_file)
        additionalInfo = {"User": identifier['displayName'],"TotalMS": 0,
                          "DayDistribution": [0]*24, "LastUpdated": "in progress", "IsExtended": "False"}

# lastVal is the last save point reached
# it is saved in the config file
lastVal = int(config['SETTINGS']['lastValue'])
if lastVal < len(filemap):
    print("Phase 1: parsing your data")
    print("Total records:",len(filemap),"- starting from record number",lastVal+1)
    for i, val in enumerate(filemap):
        if i<lastVal:
            continue

        request = urllib.parse.quote(f"{val['trackName']}%20track:{val['trackName']}%20artist:{val['artistName']}")
        #print(request)
        try:
            resp = (session.get("https://api.spotify.com/v1/search?q="+request+"&type=track&limit=1"))
            if resp.status_code == 400: #bad request
                #print(i,":",resp)
                errors[i] = {"Error": "[400] - name too long", "ID": i}
                #input()
                continue
            elif resp.status_code != 200:
                print(resp)
                print("Error, saving file and closing at "+str(i))
                with open(dump_path,'w') as dump, open(err_path,'w') as er,open(
                        'settings.ini','w') as settings, open(addinf_path,'w') as addinf_file:
                    json.dump(songdatini,dump)
                    json.dump(errors, er)
                    json.dump(additionalInfo, addinf_file)
                    config['SETTINGS']['lastValue'] = str(i)
                    config.write(settings)
                print("Save completed: first "+str(i)+" rows saved")
                #input()
                exit(1)


        except Exception as e:
            print(resp.content)
            errors[i] = {"Error": str(resp.content),"ID": i}
            #input()
            continue
        
        response = resp.json()
        #print(response)
        try:
            trackID = response["tracks"]["items"][0]["id"]
            track_ms = response["tracks"]["items"][0]["duration_ms"]
            popularity =response["tracks"]["items"][0]["popularity"]
            artistPopularity =response["tracks"]["items"][0]["artist"][0]["popularity"]

            if trackID not in songdatini:
                songdatini[trackID]={"Artist": val['artistName'], "Title": val['trackName'], "msDuration": track_ms,
                                     "TimesPlayed": 0, "msPlayed": 0, "timeDistribution": [0]*8, "Popularity": popularity,
                                     "ArtistPopularity": artistPopularity}
      
            songdatini[trackID]["TimesPlayed"] += 1 if val['msPlayed']>track_ms/3 else 0
            songdatini[trackID]["msPlayed"] += val['msPlayed']

            time = val['endTime'].split(" ")[1].split(":")[0]
            songdatini[trackID]["timeDistribution"][int(time)//3] +=1 if val['msPlayed']>track_ms/3 else 0
            additionalInfo["DayDistribution"][int(time)]+=1 if val['msPlayed']>track_ms/3 else 0
            additionalInfo["TotalMS"]+= val["msPlayed"]
            
        except IndexError as e:
            errors[i] = {"Error": "Track not found - try a different query","ID": i}

            # print(e)
        lastVal+=1
        #print(i+1,"out of",len(filemap))
        if (i+1)%100 == 0:
            with open(dump_path,'w') as dump, open('settings.ini','w') as settings, open(
                err_path,'w') as er,open(addinf_path,'w') as addinf_file:
                json.dump(songdatini,dump)
                json.dump(errors, er)
                json.dump(additionalInfo, addinf_file)
                config['SETTINGS']['lastValue'] = str(i+1)
                config.write(settings)
                print("Save completed: first "+str(i+1)+" records elaborated.")

    additionalInfo['LastUpdated'] = filemap[len(filemap) - 1]["endTime"]

    with open(dump_path,'w') as dump, open('settings.ini','w') as settings, open(
        err_path,'w') as er, open(addinf_path,'w') as addinf_file:
        print("Phase 1 completed! you have",len(songdatini),"tracks and",len(errors),"errors!")
        json.dump(songdatini,dump)
        json.dump(errors, er)
        json.dump(additionalInfo, addinf_file)
        config['SETTINGS']['lastValue'] = str(len(filemap))
        config.write(settings)



print("Starting phase 2: processing errors")

api_key = requests.post("https://accounts.spotify.com/api/token", data = d).json()["access_token"]
# print(api_key)
session = requests.Session()
session.headers.update({"Authorization": f"Bearer  {api_key}"})

ids = []
discardedRecords = {}


for val in errors:
   ids.append(val)

print(len(ids),"to check, starting...")
for i, val in enumerate(filemap):
   if i not in ids:
       continue
   else:
      request = urllib.parse.quote(f"%20track:{val['trackName']}%20artist:{val['artistName']}")
      resp = (session.get("https://api.spotify.com/v1/search?q="+request+"&type=track&limit=1"))
      response = resp.json()

      # feel free to add other inputs to test but if it fails there's a good chance
      # the track doesn't exist anymore
      tryInput =["asdasd",val['artistName'],"%20",val['trackName'][:15],"123456", "palle"]
      ctr=0
      try:
          while True:
              try:
                trackID = response["tracks"]["items"][0]["id"]
                track_ms= response["tracks"]["items"][0]["duration_ms"]
                popularity = response["tracks"]["items"][0]["popularity"]
                artistPopularity = response["tracks"]["items"][0]["artist"]["popularity"]
                break
              except IndexError:
                #print("Trying input "+tryInput[ctr]+" on ID "+str(i))
                request = urllib.parse.quote(f"{tryInput[ctr]}%20track:"
                                             f"{val['trackName']}%20artist:{val['artistName']}")
                resp = (session.get("https://api.spotify.com/v1/search?q=" + request + "&type=track&limit=1"))
                response = resp.json()
                ctr+=1
      except IndexError:
        print("all inputs tried for "+str(i)+", proceeding to the next input.")
        discardedRecords[i] = filemap[i]
        # print(discardedRecords[i])
        continue


      if trackID not in songdatini:
         songdatini[trackID]={"Artist": val['artistName'], "Title": val['trackName'], "msDuration": track_ms,
                              "TimesPlayed": 0, "msPlayed": 0, "timeDistribution": [0]*8, "Popularity": popularity,
                              "ArtistPopularity": artistPopularity}
      
      songdatini[trackID]["TimesPlayed"] += 1 if val['msPlayed']>track_ms/3 else 0
      songdatini[trackID]["msPlayed"] += val['msPlayed']

      time = val['endTime'].split(" ")[1].split(":")[0]
      songdatini[trackID]["timeDistribution"][int(time)//3] +=1 if val['msPlayed']>track_ms/3 else 0
      additionalInfo["DayDistribution"][int(time)]+=1 if val['msPlayed']>track_ms/3 else 0
      
      additionalInfo["TotalMS"]+= val["msPlayed"]

with open(os.getcwd()+'/out/data.json', 'w') as data, open(
        os.getcwd()+'/out/discarded.json', 'w') as dr, open(
        os.getcwd()+'/out/additionalInfo.json','w') as ad:
    json.dump(songdatini, data)
    json.dump(discardedRecords, dr)
    json.dump(additionalInfo, ad)

    print("Completed! you have", len(songdatini), "tracks and", len(discardedRecords), "records discarded")


        
    