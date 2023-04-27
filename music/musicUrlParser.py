import traceback
from typing import Union
import youtubeParser
import spotifyParser
import musicObjects
from mPrint import mPrint as mp, tagType
def mPrint(tag: tagType, text):
    mp(tag, 'urlparser', text)

def getTracksURL(userQuery:str, overwritten, playlists : dict[str, list[str]]) -> Union[list[str], None]:
    """Parses user input and retuns a list of URLs"""
    #user searched a link
    if ',' in userQuery: #multiple search items
        links = userQuery.replace(" ", "").split(',') # NOTE: this also removes spaces between words eg."myplaylist"
    else: #one search item
        links = [userQuery]

    toReturn = []
    for search in links:
        mPrint('DEBUG', f"{search=}")
        if "spotify.com" in search or "youtube.com" in search or "youtu.be" in search:
            mPrint('INFO', f'FOUND SUPPORTED URL: {search}')
            toReturn.append(search)
        
        #user wants a saved playlist (playlists can have multiple tracks)
        elif search in [key.replace(" ", "") for key in playlists]:
            for k in playlists:
                if k.replace(" ", "") == userQuery:
                    key = k
                    break
            mPrint('INFO', f'FOUND SAVED PLAYLIST: {playlists[key]}')
            for track in playlists[key]:
                toReturn.append(track)
        
        #user submitted a youtube query
        else:
            mPrint('MUSIC', f'Searching for user requested song: ({search})')
            trackURL = youtubeParser.searchYTurl(search, overwritten)
            if trackURL == None:
                return 404
            mPrint('INFO', f'SEARCHED SONG URL: {trackURL}')
            toReturn.append(trackURL)

    return toReturn

def getTracksFromURL(url, overwritten) -> Union[list[musicObjects.Track], None]:
    """return a list of track objects found from an url, if the song is only 1, returns a list of one element"""
    #TODO check if url is a playlist
    if url == '': return
    
    if 'spotify.com' in url:
        try:
            tracks = spotifyParser.getTracks(url, overwritten)
            if tracks == -1:
                mPrint('ERROR', "SPOTIFY AUTH FAILED, add your keys in the .env file if you want to enable spotify functionalities")
                return None
            elif tracks == -2:
                mPrint('ERROR', "The spotify link could not be parsed correctly")
                return None

        except Exception:
            mPrint('ERROR', f"Spotify parser error:\nurl = {url}\n{traceback.format_exc()}")
            return None
    else:
        try:
            tracks = youtubeParser.getTracks(url)
            if tracks == None:
                mPrint('ERROR', f'Youtube parser error for: {url}')
                return None
        except Exception:
            mPrint('ERROR', f"Youtube parser error:\nurl = {url}\n{traceback.format_exc()}")
            return None

    return tracks

def evalUrl(url, ow) -> bool:
    """Returns ture if the url is valid, else false"""
    resp = getTracksFromURL(url, ow)
    if resp == None: 
        return False
    return True