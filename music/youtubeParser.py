# import json #used for testing
import yt_dlp
from musicObjects import Track, ydl_opts, youtubeDomain, download

from mPrint import mPrint as mp
def mPrint(tag, text):
    mp(tag, 'youtubeParser', text)

SOURCE = "youtube"

def searchYTurl(query) -> str:
    """
    gets the url of the first song in queue (the one to play)
    """
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]
        try:
            int(result['duration'])
        except TypeError: #If duration is null video is probably was live, just skip it
            mPrint('DEBUG', f'Skipping live video {youtubeDomain}{result["url"]}')
            return None
        return f'{youtubeDomain}{result["url"]}'

def stampToSec(str : str) -> int:
    seconds = 0
    str = str.split(':')[::-1] # [sec, min, hr, ...]
    if len(str) >= 1: #we have seconds
        seconds += int(str[0])
    if len(str) >= 2: #we have minutes
        seconds += int(str[1]) * 60
    if len(str) >= 3: #we have hrs
        seconds += int(str[2]) * 60
    return seconds

def fetchTracks(url: str) -> list[Track]:
    # mPrint('FUNC', f"youtubeParser.fetchTracks({url=})")
    if "music.youtube.com" in url: #target is youtube music URL
        #replacing the strings gets the same link in youtube video form
        url = url.replace("music.youtube.com", "www.youtube.com", 1)

    elif "www.youtube.com" not in url and "youtu.be" not in url: #Avoid other links
        for x in ['http://', 'https://', 'www.']:
            if x in url: 
                mPrint('DEBUG', 'Link is not a valid URL')
                return None
            
        mPrint("DEBUG", "Link is not a youtube link, using query")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                r_result = ydl.extract_info(f"ytsearch:{url}", download=False)
                result = r_result['entries'][0]
                url = f'{youtubeDomain}{result["url"]}'
                mPrint('DEBUG', f'Found url:{url}')
            except TypeError:
                mPrint('WARN', 'Query result is null (?)')
                return None            

    # Parse url to get IDs for video and playlist, as well as the current index
    linkData = url.split('&')
    video = linkData[0]
    playlist = None
    index = 1
    for u in linkData:
        if 'list' in u:
            playlist = u.strip('list=')
        elif 'index' in u:
            index = int(u.strip('index='))

    #Extract data from the url NB: videos and playlists have a different structure
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            result = ydl.extract_info(url, download)
        except yt_dlp.utils.DownloadError:
            mPrint('ERROR', 'yt_dlp.utils.DownloadError: (Probably) Age restricted video')
            return None

    # Parse uploader data (assuming it's the song artist)
    artist = [{"name": result["uploader"], "url": result["uploader_url"]}]

    # Playlist link only returns one song
    tracks : list[Track] = []
    
    if playlist != None: #link is a playlist
        def addTracks(i) -> None:
            videoData = result['entries'][i]

            #Append Track foreach video in playlist
            try:
                duration = int(videoData['duration'])
            except TypeError: #If duration is null video is probably was live, just skip it
                mPrint('DEBUG', f'Skipping live video {youtubeDomain}{videoData["url"]}')
                return -1

            tracks.append(Track(
                SOURCE,
                f"{youtubeDomain}{videoData['url']}",
                videoData["title"],
                artist,
                duration,
                f"{youtubeDomain}{videoData['url']}",
                None
            ))

        # add songs in the same order as the one in the youtube playlist
        # starting @ the video that the user took the link from
        for i in range(index-1, len(result['entries'])):
            addTracks(i)
        for i in range(index-1):
            addTracks(i)

    else: #link is a video
        tracks.append(Track(
            SOURCE,
            result['webpage_url'],
            result['title'],
            artist,
            int(result['duration']),
            result['webpage_url'],
            result['thumbnail']
        ))

    
    return tracks
