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

def getSongs(url):
    tracks = None
    if "www.youtube.com" not in url:
        url = VideosSearch(url).result()["result"][0]['link']

    if tracks == None:
        try:
            tracks = Playlist.getVideos(url)["videos"] # None if unavailable
            print("found playlist")
            print(len(tracks))
            with open("tests/youtubeAPIplaylist.json", 'w') as f:
                json.dump(tracks, f, indent=2)
        except AttributeError:
            pass

    if tracks == None:
        tracks = [Video.get(url)]
        print("found video")

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
# getSongs(url)
