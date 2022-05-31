import json
from youtubesearchpython import VideosSearch, Playlist, Video

def stampToSec(str : str):
    seconds = 0
    str = str.split(':')[::-1] # [sec, min, hr, ...]
    if len(str) >= 1: #we have seconds
        seconds += int(str[0])
    if len(str) >= 2: #we have minutes
        seconds += int(str[1]) * 60
    if len(str) >= 3: #we have hrs
        seconds += int(str[2]) * 60
    return seconds

def getSongs(url : str):
    tracks = None
    if "www.youtube.com" not in url:
        #query youtube for the url of the first result
        if "music.youtube.com" in url:
            url = url.replace("music.youtube.com", "www.youtube.com", 1)
            try:
                url = url.split('&list=')[0]
            except:
                pass
        else:
            url = VideosSearch(url).result()["result"][0]['link']


    if 'list=' in url:
        try:
            tracks = Playlist.getVideos(url)["videos"] # None if unavailable
        except AttributeError:
            pass #link was not a playlist

    else:
        #if link was not a playlist, search for a video
        tracks = [Video.get(url)]

    for t in tracks:
        if type(t['duration']) == dict:
            t['duration'] = t['duration']['secondsText']
        else:
            t['duration'] = stampToSec(t['duration'])

    return [{
            'trackName': t["title"],
            'artist': t["channel"]["name"],
            'search': f"{t['title']} {t['channel']['name']}",
            'duration_sec': t['duration']
        } for t in tracks ]



# url = 'https://www.youtube.com/watch?v=kt1KWL9NZzo'
# url = 'https://www.youtube.com/watch?v=2XM1OF2_6_4&list=OLAK5uy_lxsKqDHchO8VpAxRCPoayWUCyCVWfeJNg'
# url = "Unlike Pluto - Everything Black (feat. Mike Taylor)"
# url = 'https://www.youtube.com/watch?v=jNQXAC9IVRw'
# url = 'https://www.youtube.com/watch?v=56lkofpjOAs'
# url = 'https://www.youtube.com/watch?v=Bv5bOJekegA&list=PLRrWCmzNJAWo0vKTtO5DpYMgxC1iHnycF'

# url = 'https://music.youtube.com/watch?v=jH8Yox66CtQ&list=RDAMVMjH8Yox66CtQ'
# url = 'https://music.youtube.com/playlist?list=OLAK5uy_kg7ISwHyM0ZuQ1jWshC74yrnPmPdNNRoY'
# url = 'https://music.youtube.com/watch?v=J7p4bzqLvCw&list=RDAMVMJ7p4bzqLvCw'
# getSongs(url)
