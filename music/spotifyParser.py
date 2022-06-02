import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from math import ceil

load_dotenv()#Sensitive data is stored in a ".env" file
CLIENT_ID = os.getenv('SPOTIFY_ID')[1:-1]
CLIENT_SECRET = os.getenv('SPOTIFY_SECRET')[1:-1]

authenticated = False

#Authentication
try:
    client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
    sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)
    authenticated = True
except spotipy.oauth2.SpotifyOauthError:
    print('WARNING: Spotify keys are wrong or not present. The bot won\'t be able to play music from spotify')


def spotifyUrlParser(URL:str) -> tuple[str, str]:
    """gets a spotify link and returns a tuple with (URL, type); type can be playlist, album, track"""

    id = URL.split("/")[-1].split("?")[0]
    type = URL.split("/")[-2]
    return (id, type)

def getSongs(URL:str) -> list[dict]:
    if not authenticated:
        return "SPOTIFY AUTH FAILED."
    id, type = spotifyUrlParser(URL)

    if type == "playlist":
        tracks = getSongsFromPlaylist(id, URL)

    elif type == "album":
        tracks = getSongsFromAlbum(id, URL)
    
    elif type == "track":
        tracks = getSongFromTrack(id, URL)

    return tracks

def getSongsFromAlbum(URL, long_url):
    trackNumber = sp.album_tracks(URL)["total"]
    trackLimit = sp.album_tracks(URL)["limit"]
    tracks = []
    #make sure to not be limited by API limit
    for i in range( ceil(trackNumber / trackLimit) ):
        rawTracks = sp.album_tracks(URL)["items"]
        for t in rawTracks:
            artists = ""
            for a in t['artists']:
                artists += f"{a['name']}, "
            artists = artists[:-2]
            tracks.append({
                'trackName':t['name'],
                'artist':artists,
                'search':f"{t['name']}{t['artists'][0]['name']}",
                'duration_sec': t['duration_ms']/1000,
                'base_link': long_url,
            })
    return tracks

def getSongsFromPlaylist(URL, long_url):
    trackNumber = sp.playlist_tracks(URL)["total"]
    trackLimit = sp.playlist_tracks(URL)["limit"]
    tracks = []
    #make sure to not be limited by API limit
    for i in range( ceil(trackNumber / trackLimit) ):
        rawTracks = sp.playlist_tracks(URL, offset=i*trackLimit)["items"]
        for t in rawTracks:
            t = t['track']
            artists = ""
            for a in t['artists']:
                artists += f"{a['name']}, "
            artists = artists[:-2]
            tracks.append({
                'trackName':t['name'],
                'artist':artists,
                'search':f"{t['name']} {t['artists'][0]['name']}",
                'duration_sec': t['duration_ms']/1000,
                'base_link': long_url,
            })
    return tracks

def getSongFromTrack(URL, long_url):
    t = sp.track(URL)
    #return single item list for omogeneità
    artists = ""
    for a in t['artists']:
        artists += f"{a['name']}, "
    artists = artists[:-2]
    return [{
        'trackName':t['name'],
        'artist':artists,
        'search':f"{t['name']} {t['artists'][0]['name']}",
        'duration_sec': t['duration_ms']/1000,
        'base_link': long_url,
    }]


# TESTING PURPOSES TODO DELETE
# for i, x in enumerate(getSongs("https://open.spotify.com/track/6ZSvhLZRJredt15aJiBQqv?si=0cc36d8193254fac")):
#      print(f'{i+1}. {x}')

# URL = "https://open.spotify.com/track/6ZSvhLZRJredt15aJiBQqv?si=0cc36d8193254fac"
# print(sp.track(URL))
#suggestion: maybe sp.tracks() can join the 3 dumb functions, try later

