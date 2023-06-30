### - - IMPORTANT - -

This is NOT the parser for the **EXTENDED** Streaming History. It will be released too but *it's not available for now.*

# Spotify History Parser
A parser for the Streaming History of last year sent to you by Spotify [after requesting it there](https://www.spotify.com/us/account/privacy/).  
They are elaborated through the Spotify API so it requires an internet connection to function.

## Getting started

There are a few things you'll need to do before starting:
- Download *spotifyParser.py* and *settings.ini* and place them into the same folder. This will be your root.
- Create a new folder in your root called *out*, open it and create a new folder called *dump* inside.
- Put the folder of the data sent to you from Spotify (called MyData) in the root folder.
- Get your client ID and secret
- Update the settings.ini file
- Have **Python** installed

### How do I get my client ID and secret?

You have to access [Spotify Developers](https://developer.spotify.com/), then login.

You then have to access **dashboard > create app**, then fill the fields (not important with what).  
Once you have your app, access **dashboard > [YOUR-APP] > settings > basic informations**. Here you'll find your
client ID and your secret. These need to be added into the settings. 

### Update settings
You'll find a settings.ini file that contains the parameters that need to be edited for the correct functioning 
of the program. 
- ClientID: the client ID you got from the developers app
- ClientSecret: the client secret you got from the developers app
- filesNumber: how many StreamingHistory_.json are in the MyData folder.
  >Note: put the total number of StreamingHistory files and not the greatest index, they start from 0 and not 1!
- lastValue: the last index elaborated by the parser.  
  - don't touch it (you will miss records/have duplicates)
  - unless you want to [restart](#restarting-) 

### Installing Python
[There are plenty of guides in the sea but I'll link you one for ease](
https://gist.github.com/MichaelCurrin/57caae30bd7b0991098e9804a9494c23)

## Running the program

Open the terminal and move into the folder where you placed SpotifyParser.py. Then run it with Python with this command:  
```
python3 spotifyParser.py
```
Or, if you're on windows:
```
python spotifyParser.py
```
And it's done! Let it run, it will take a while depending on your internet connection.

### Restarting 
If you want to restart from scratch, make sure you delete **EVERYTHING** in your dump folder. 
Then set the *lastvalue* option in the settings file to 0 and you're good to go.


## Output

The program will return you the main JSON files in the /out folder.  

### data.json

This file contains the effective elaborated output with all the data elaborated from your streaming
history, minus the tracks that were discarded.

#### Structure
```
{
  "TRACK_ID": {
    "ID": TRACK_ID,
    "Artist": ARTIST_NAME,
    "Title": TRACK_NAME,
    "msDuration": LENGTH_IN_MILLISECONDS,
    "TimesPlayed": TIMES_PLAYED>=1/3_TRACK_LEN,
    "msPlayed": TOTAL_MILLIS_PLAYED
    "timeDistribution": [ PLAYS_PER_3HR_BLOCKS ]
  },
  [...]
  }
```
### additionalInfo.json

This file contains other data collected from the user that will be used by 
the stats analyzer.

#### Structure
```
{
  "User": SPOTIFY_USERNAME,
  "TotalMS": TOTAL_MILLIS_PLAYED,
  "DayDistribution": [ PLAYS_PER_HOUR ]
}
```


### discarded.json 

These are the listening instances of the tracks that couldn't be found. 
They most likely are deleted tracks.

It contains the JSON directly from the StreamingHistory file, 
indexed by the position in the (concatenation of) file(s). 
#### Structure 
```
"POSITION": {
    "endTime": INSTANCE_TIMESTAMP,
    "artistName": ARTIST_NAME,
    "trackName": TRACK_NAME,
    "msPlayed": MILLIS_PLAYED_INSTANCE
  }
```
### Dump folder
You'll find other kinds of files there: dump.json and error.json   
These are all files elaborated and saved during the first parsing phase and used in the second one.

## Troubleshooting

### Response [429]
If you got this response and the program closed, you have either reached the rate limit or the max quota. 
I never managed to reach the rate limit but only the quota while testing.   
It should be pretty hard to reach
on a normal use but in case I'd suggest you to generate another ID and secret by creating another app 
or try again in a few hours or the next day (no testing was done on the quota reset).  
*I am not aware of how the rate limit and the quota work exactly so this may be updated in the future.*

### Response [401]
Your program has been running for an hour and the key has expired. Rerunning the program will solve this issue.

### Other responses
- 5xx: server errors, wait and retry later.
- [check response codes here](https://developer.spotify.com/documentation/web-api/concepts/api-calls#response-status-codes)
