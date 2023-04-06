import json
import spotipy
from musicObjects import Track
from spotipy.oauth2 import SpotifyClientCredentials
from math import ceil

from mPrint import mPrint as mp
def mPrint(tag, value):mp(tag, 'spotifyParser', value)

#Since I had problems getting getenv to work on linux for some reason I'm writing my own function in case someone else has the same problems
import getevn

CLIENT_ID = getevn.getenv('SPOTIFY_ID')
CLIENT_SECRET = getevn.getenv('SPOTIFY_SECRET')

SOURCE = "spotify"

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

def fetchTracks(URL:str, urlsync:list[dict]) -> list[Track]:
    if not authenticated:
        return -1
    id, type = spotifyUrlParser(URL)

    if type == "playlist": tracks = getTracksFromPlaylist(id, urlsync)
    elif type == "album": tracks = getTracksFromAlbum(id, urlsync)
    elif type == "track": tracks = getTracksFromTrack(id, urlsync)
    else: return -2

    return tracks

#"spsync": [], # {spotify_uri: {query: str, spotify_url: str, youtube_url: str, soundcloud_url?: str}}
def getTracksFromPlaylist(URL, urlsync: list[dict]) -> list[Track]:
    # mPrint('FUNC', f"spotifyParser.getTracksFromPlaylist({URL=}, urlsync)")
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
            
            yt_url = None
            for d in urlsync:
                if d['spotify_url'] == trackData["external_urls"]["spotify"]:
                    mPrint('DEBUG', f"urlsync match {trackData['external_urls']['spotify']}")
                    yt_url = d['youtube_url']
                    break

            try:
                if trackData['is_local'] == False:
                    tracks.append(Track(
                        SOURCE,
                        trackData['external_urls']['spotify'],
                        trackData['name'],
                        artists,
                        trackData['duration_ms']/1000,
                        yt_url,
                        explicit = trackData['explicit'],
                        spotifyThumbnail = trackData['album']['images'][-1]['url'],
                        spotifyURL = trackData['external_urls']['spotify']
                    ))
                else:
                    #For non local tracks the bot will try to get the youtube query when needed
                    tracks.append(Track(
                        SOURCE,
                        None,
                        trackData["name"],
                        artists,
                        trackData['duration_ms']/1000
                    ))
            except:
                mPrint('ERROR', f'Track \ntitle: {trackData["name"]}; {artists=}')
                mPrint('TEST', json.dumps(trackData, indent=2))

    return tracks

def getTracksFromAlbum(URL, urlsync) -> list[Track]:
    # mPrint('FUNC', f"spotifyParser.getTracksFromAlbum({URL=}, urlsync)")
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
            
            yt_url = None
            for d in urlsync:
                if d['spotify_url'] == trackData["external_urls"]["spotify"]:
                    mPrint('DEBUG', f"urlsync match {trackData['external_urls']['spotify']}")
                    yt_url = d['youtube_url']
                    break
            
            tracks.append(Track(
                SOURCE,
                trackData['external_urls']['spotify'],
                trackData['name'],
                artists,
                trackData['duration_ms']/1000,
                yt_url,
                explicit = trackData['explicit'],
                spotifyThumbnail = None, # Album search does not give image data :(
                spotifyURL = trackData["external_urls"]["spotify"]
            ))

    return tracks

def getTracksFromTrack(URL, urlsync) -> list[Track]:
    # mPrint('FUNC', f"spotifyParser.getTracksFromTrack({URL=}, urlsync)")
    resData:dict = sp.track(URL)

    #make a list of artist names
    artists = []
    for a in resData['artists']:
        artists.append(a['name'])

    yt_url = None
    for d in urlsync:
        if d['spotify_url'] == resData["external_urls"]["spotify"]:
            mPrint('DEBUG', f"urlsync match {resData['external_urls']['spotify']}")
            yt_url = d['youtube_url']
            break

    #return a single item list with the data
    return [Track(
        SOURCE,
        resData["external_urls"]["spotify"],
        resData['name'],
        artists,
        resData['duration_ms']/1000,
        yt_url,
        explicit = resData['explicit'],
        spotifyThumbnail = resData['album']['images'][-1]['url'],
        spotifyURL = resData["external_urls"]["spotify"]
    )]
