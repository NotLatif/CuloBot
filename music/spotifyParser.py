import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from math import ceil

from mPrint import mPrint as mp
def mPrint(tag, value):mp(tag, 'bot', value)

#Since I had problems getting getenv to work on linux for some reason I'm writing my own function in case someone else has the same problems
import getevn

CLIENT_ID = getevn.getenv('SPOTIFY_ID')
CLIENT_SECRET = getevn.getenv('SPOTIFY_SECRET')

authenticated = False

#Authentication
try:
    client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
    sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)
    authenticated = True
except spotipy.oauth2.SpotifyOauthError:
    mPrint('WARN', 'WARNING: Spotify keys are wrong or not present. The bot won\'t be able to play music from spotify')


def spotifyUrlParser(URL:str) -> tuple[str, str]:
    """gets a spotify link and returns a tuple with (URL, type); type can be playlist, album, track"""

    id = URL.split("/")[-1].split("?")[0]
    type = URL.split("/")[-2]
    return (id, type)

def getSongs(URL:str) -> list[dict]:
    if not authenticated:
        return -1
    id, type = spotifyUrlParser(URL)

    if type == "playlist":
        tracks = getSongsFromPlaylist(id, URL)

    elif type == "album":
        tracks = getSongsFromAlbum(id, URL)
    
    elif type == "track":
        tracks = getSongFromTrack(id, URL)

    return tracks

def getSongsFromAlbum(URL, long_url):
    #acquire playlist size and spotify GET limit
    trackNumber = sp.album_tracks(URL)["total"]
    trackLimit = sp.album_tracks(URL)["limit"]
    tracks = []

    # when size > limit (eg. 350 songs, 100max)
    # this will GET 100 songs at a time (last GET req. will only have 50 songs)

    for i in range( ceil(trackNumber / trackLimit) ):
        rawTracks = sp.album_tracks(URL, offset=i*trackLimit)["items"]
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
    #acquire playlist size and spotify GET limit
    trackNumber = sp.playlist_tracks(URL)["total"]
    trackLimit = sp.playlist_tracks(URL)["limit"]
    tracks = []

    # when size > limit (eg. 350 songs, 100max)
    # this will GET 100 songs at a time (last GET req. will only have 50 songs)
    for i in range( ceil(trackNumber / trackLimit) ): #huh?
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