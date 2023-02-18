import json
import spotipy
from musicObjects import Track
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
    sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager, requests_timeout=10, retries=5)
    authenticated = True
except spotipy.oauth2.SpotifyOauthError:
    mPrint('WARN', 'Spotify keys are wrong or not present. The bot won\'t be able to play music from spotify')


def spotifyUrlParser(URL:str) -> tuple[str, str]:
    """gets a spotify link and returns a tuple with (URL, type); type can be playlist, album, track"""
    id = URL.split("/")[-1].split("?")[0]
    type = URL.split("/")[-2]
    return (id, type)

def getTracks(URL:str, overwritten:dict[str, str]) -> list[Track]:
    if not authenticated:
        return -1
    id, type = spotifyUrlParser(URL)

    if type == "playlist": tracks = getSongsFromPlaylist(id, overwritten)
    elif type == "album": tracks = getSongsFromAlbum(id, overwritten)
    elif type == "track": tracks = getSongFromTrack(id, overwritten)
    else: return -2

    return tracks

def getSongsFromPlaylist(URL, overwritten:dict[str, str]) -> list[Track]:
    #acquire playlist size and spotify GET limit
    trackNumber = sp.playlist_tracks(URL)["total"]
    trackLimit = sp.playlist_tracks(URL)["limit"]
    tracks : list[Track] = []

    # when size > limit (eg. 350 songs, 100max)
    # this will GET 100 songs at a time (eg. last GET req. will only have 50 songs)
    for i in range( ceil(trackNumber / trackLimit) ):
        playlistDataRes = sp.playlist_tracks(URL, offset=i*trackLimit)["items"]

        for trackData in playlistDataRes:
            trackData = trackData['track']
            
            artists = []
            for a in trackData['artists']:
                artists.append(a['name'])
            
            if f"{trackData['name']} {artists[0]}" in overwritten:
                mPrint('DEBUG', f"Found overwritten track ({trackData['name']} {artists[0]})")
                yt_url = overwritten[f"{trackData['name']} {artists[0]}"]
            else:
                yt_url = None

            try:
                if trackData['is_local'] == False:
                    tracks.append(Track(
                        trackData['external_urls']['spotify'],
                        trackData['name'],
                        artists,
                        trackData['duration_ms']/1000,
                        yt_url,
                        explicit = trackData['explicit'],
                        spotifyThumbnail = trackData['album']['images'][-1]['url']
                    ))
                else:
                    #For non local tracks the bot will try to get the youtube query when needed
                    tracks.append(Track(
                        None,
                        trackData["name"],
                        artists,
                        trackData['duration_ms']/1000
                    ))
            except:
                mPrint('ERROR', f'Track \ntitle: {trackData["name"]}; {artists=}')
                mPrint('TEST', json.dumps(trackData, indent=2))

    return tracks

def getSongsFromAlbum(URL, overwritten:dict[str, str]) -> list[Track]:
    #acquire playlist size and spotify GET limit
    trackNumber = sp.album_tracks(URL)["total"]
    trackLimit = sp.album_tracks(URL)["limit"]
    tracks : list[Track] = []

    # when size > limit (eg. 350 songs, 100max)
    # this will GET 100 songs at a time (last GET req. will only have 50 songs)

    for i in range( ceil(trackNumber / trackLimit) ):
        albumDataRes = sp.album_tracks(URL, offset=i*trackLimit)["items"]

        for trackData in albumDataRes:
            artists = []
            for a in trackData['artists']:
                artists.append(a['name'])
            
            if f"{trackData['name']} {artists[0]}" in overwritten:
                mPrint('DEBUG', f"Found overwritten track ({trackData['name']} {artists[0]})")
                yt_url = overwritten[f"{trackData['name']} {artists[0]}"]
            else:
                yt_url = None
            
            tracks.append(Track(
                trackData['external_urls']['spotify'],
                trackData['name'],
                artists,
                trackData['duration_ms']/1000,
                yt_url,
                explicit = trackData['explicit'],
                spotifyThumbnail = None # Album search does not give image data :(
            ))

    return tracks

def getSongFromTrack(URL, overwritten) -> list[Track]:
    resData:dict = sp.track(URL)

    #make a list of artist names
    artists = []
    for a in resData['artists']:
        artists.append(a['name'])

    if f"{resData['name']} {artists[0]}" in overwritten:
        mPrint('DEBUG', f"Found overwritten track ({resData['name']} {artists[0]})")
        yt_url = overwritten[f"{resData['name']} {artists[0]}"]
    else:
        yt_url = None

    #return a single item list with the data
    return [Track(
        resData["external_urls"]["spotify"],
        resData['name'],
        artists,
        resData['duration_ms']/1000,
        yt_url,
        explicit = resData['explicit'],
        spotifyThumbnail = resData['album']['images'][-1]['url']
    )]
