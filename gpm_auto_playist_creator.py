from gmusicapi import Mobileclient
import sys
from datetime import datetime
import time
import logging
import os

# CONSTANTS
HOURS_INTERVAL = 1 # Will run every hour
CONFIG_FILE_NAME = os.path.join(os.path.abspath(os.path.dirname(__file__)), ".google_play_music_auto_playlist_creator_config")
PLAYLIST_NAME = "Non-played"


logging.basicConfig(filename=os.path.join(os.path.abspath(os.path.dirname(__file__)), 'log.txt'),
		level=logging.INFO,
		format="%(asctime)s %(levelname)s %(module)s %(message)s",
		datefmt='%Y-%m-%d %H:%M:%S %Z')
api = Mobileclient()

with open(CONFIG_FILE_NAME) as conf_file:
	username, password = conf_file.read().split("\n")[:2]
	logged_in = api.login(username, password, Mobileclient.FROM_MAC_ADDRESS)

	if not logged_in:
		logging.error("Error: could not log in.")
		sys.exit(1)

all_songs = api.get_all_songs()

non_played_songs = [song for song in all_songs if song["playCount"] == 0]

all_playlists = api.get_all_playlists()

playlist_id = None

for playlist in all_playlists:
	if playlist["name"] == PLAYLIST_NAME:
		playlist_id = playlist["id"]
		logging.info("Found playlist id: %s", playlist_id)
		break

if not playlist_id:
	playlist_id = api.create_playlist(PLAYLIST_NAME)
	logging.info("Created new playlist: id %s", playlist_id)

all_playlists = api.get_all_user_playlist_contents()

logging.info("Clearing the playlist")

manipulated_playlist = [pl for pl in all_playlists if pl["name"] == PLAYLIST_NAME][0]
api.remove_entries_from_playlist([track["id"] for track in manipulated_playlist["tracks"]])

logging.info("Adding new tracks to the playlist")
api.add_songs_to_playlist(playlist_id=playlist_id, song_ids=[song["id"] for song in non_played_songs])
