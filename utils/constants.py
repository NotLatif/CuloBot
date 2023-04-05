SETTINGS_TEMPLATE = {
    "id": {
        "responseSettings": {
            "disabled_channels":[],
            "join_message":"%name% wants the butt",
            "leave_message":"%name% ha ragequittato",
            "send_join_msg":False,
            "send_leave_msg":False,
            "response_perc":35,
            "other_response":9,
            "response_to_bots_perc":35,
            "will_respond_to_bots":False,
            "use_global_words":False,
            "custom_words":["butt"]
        },
        "chessGame": {
            "disabled_channels":[],
            "default_board":"default",
            "boards": {},
            "default_design":"default",
            "designs": {}
        },
        "musicbot": {
            "player_shuffle": True,
            "disabled_channels":[],
            "saved_playlists":{},
            "urlsync": [], # [{youtube_url: str, query: str, spotify_url: str, soundcloud_url?: str}] # youtube_url can be treated as an ID
            "timeline_precision": 14
        }
    }
}


"""
{
  "Sanctuary Joji": "https://www.youtube.com/watch?v=3ywtudi0Pto",
  "Fabio Rovazzi - Tutto Molto Interessante (Official Video) Fabio Rovazzi": "https://www.youtube.com/watch?v=vFdiB6xefbs",
  "LEWANDOWSKI VIII (64 Bars) Ernia (Explicit)": "https://www.youtube.com/watch?v=l8oJnpwvIfg",
  "Many Men (Wish Death) 50 Cent (Explicit)": "https://www.youtube.com/watch?v=7CVGDPqnZj8",
  "Your Man Joji": "https://www.youtube.com/watch?v=dS8w5B6cBJY",
  "The Real Slim Shady Eminem (Explicit)": "https://www.youtube.com/watch?v=FA2j9qlFyDU",
  "531 THE KOXX": "https://www.youtube.com/watch?v=mZf7fUwqSYU",
  "Brivido Gu\u00e8 (Explicit)": "https://www.youtube.com/watch?v=aM40h9zY5C8",
  "Signore del bosco Dardust": "https://www.youtube.com/watch?v=rVAdzEUaIys",
  "All Eyez On Me (ft. Big Syke) 2Pac (Explicit)": "https://www.youtube.com/watch?v=H1HdZFgR-aA",
  "Mo Money Mo Problems (feat. Puff Daddy & Mase) - 2014 Remaster The Notorious B.I.G. (Explicit)": "https://www.youtube.com/watch?v=ss142Aix2Bo",
  "The Notorious B.I.G. - Mo Money Mo Problems (Official Music Video) [4K] The Notorious B.I.G.": "https://www.youtube.com/watch?v=ss142Aix2Bo",
  "LUNEDI' Salmo (Explicit)": "https://www.youtube.com/watch?v=HxyaKsFfLXc",
  "Window Joji (Explicit)": "https://www.youtube.com/watch?v=pCZiIRvXyT4",
  "Cos Cos Cos Clementino (Explicit)": "https://www.youtube.com/watch?v=1MK_0U9Snc0",
  "Big Poppa - 2005 Remaster The Notorious B.I.G. (Explicit)": "https://www.youtube.com/watch?v=QceVTChhlJM",
  "2 Of Amerikaz Most Wanted 2Pac (Explicit)": "https://www.youtube.com/watch?v=9wVtWAwTMPU",
  "SCASSI IL CAZZO FREESTYLE Nello Taver (Explicit)": "https://www.youtube.com/watch?v=t7kDClcGsJc",
  "Sorpresa (feat. Nayt) CanovA": "https://open.spotify.com/track/2JbrFFQEv0HgWZnsXaY4v7",
  "Dentro Alla Scatola Mondo Marcio (Explicit)": "https://www.youtube.com/watch?v=9N-9RRN_T1g",
  "COS\u00cc STUPIDI Ernia (Explicit)": "https://www.youtube.com/watch?v=3IMfVLNWBmw",
  "Salmo - A DIO (Video Animation) SalmoOfficialVEVO": "https://www.youtube.com/watch?v=KMeYQMpUAHQ",
  "Last Man Standing Nitro (Explicit)": "https://www.youtube.com/watch?v=KMeYQMpUAHQ",
  "Gemitaiz 13 - Ye Ye Ye QVC8 - Quello che vi consiglio vol.8": "https://www.youtube.com/watch?v=QEq0Ip_4ciw"
}




[{query: str, spotify_url: str, youtube_url: str, soundcloud_url?: str}]

[{query: str, spotify_url: str, youtube_url: str, soundcloud_url?: str}]
"""
