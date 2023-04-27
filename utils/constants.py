SETTINGS_TEMPLATE = {
    "id": {
        "responseSettings": {
            "disabled_channels":[],
            "join_message": "",
            "leave_message": "",
            "send_join_msg": False,
            "send_leave_msg": False,
            "response_perc": 35,
            "other_response": 9,
            "response_to_bots_perc": 35,
            "will_respond_to_bots": False,
            "use_global_words": False,
            "custom_words": ["butt"]
        },
        "chessGame": {
            "disabled_channels": [],
            "default_board": "default",
            "boards": {},
            "default_design": "default",
            "designs": {}
        },
        "musicbot": {
            "player_shuffle": True,
            "disabled_channels": [],
            "saved_playlists": {},
            "urlsync": [], # [{youtube_url: str, query: str, spotify_url: str, soundcloud_url?: str}] # youtube_url can be treated as an ID
            "timeline_precision": 14
        }
    }
}
