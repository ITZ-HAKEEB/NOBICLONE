#
# Copyright (C) 2026 by Kanha-Team@Github, < https://github.com/Kanha-Team>.
# This file is part of < https://github.com/Kanha-Team/KanhaClone > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/Kanha-Team/KanhaClone/blob/main/LICENSE >
#
# All rights reserved.
#

import os
import re

import aiohttp
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from py_yt import VideosSearch

import config
from .Youtube import API_KEY, API_URL

FALLBACK_API_URL = os.environ.get("MEOW_FALLBACK_API_URL", "https://play.yukiapi.site")
DOWNLOAD_DIR = "downloads"


class SpotifyAPI:
    def __init__(self):
        self.regex = r"^(https:\/\/open.spotify.com\/)(.*)$"
        self.client_id = config.SPOTIFY_CLIENT_ID
        self.client_secret = config.SPOTIFY_CLIENT_SECRET
        if config.SPOTIFY_CLIENT_ID and config.SPOTIFY_CLIENT_SECRET:
            self.client_credentials_manager = SpotifyClientCredentials(
                self.client_id, self.client_secret
            )
            self.spotify = spotipy.Spotify(
                client_credentials_manager=self.client_credentials_manager
            )
        else:
            self.spotify = None

    async def valid(self, link: str):
        if re.search(self.regex, link):
            return True
        else:
            return False

    @staticmethod
    def extract_track_id(link: str):
        match = re.search(r"open\.spotify\.com/(?:intl-[a-z]+/)?track/([A-Za-z0-9]+)", link)
        if match:
            return match.group(1)
        if re.fullmatch(r"[A-Za-z0-9]{22}", link.strip()):
            return link.strip()
        return None

    async def download(self, link: str):
        """
        Spotify track ka audio API se download karta hai.
        Pehle primary API, fail hone par fallback API try karta hai.
        Returns file path ya None.
        """
        track_id = self.extract_track_id(link)
        if not track_id:
            return None

        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        file_path = os.path.join(DOWNLOAD_DIR, f"spotify_{track_id}.mp3")

        if os.path.exists(file_path) and os.path.getsize(file_path) > 10000:
            return file_path

        for base in (API_URL, FALLBACK_API_URL):
            if not base:
                continue
            stream_url = f"{base.rstrip('/')}/stream/spotify/{track_id}?key={API_KEY}"
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        stream_url, timeout=aiohttp.ClientTimeout(total=300)
                    ) as resp:
                        if resp.status != 200:
                            continue
                        with open(file_path, "wb") as f:
                            async for chunk in resp.content.iter_chunked(131072):
                                f.write(chunk)
                if os.path.exists(file_path) and os.path.getsize(file_path) > 10000:
                    return file_path
            except Exception:
                pass
            # Adhura ya chhota file hata do, agli API try ho
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception:
                    pass
        return None

    async def track(self, link: str):
        track = self.spotify.track(link)
        info = track["name"]
        for artist in track["artists"]:
            fetched = f' {artist["name"]}'
            if "Various Artists" not in fetched:
                info += fetched
        results = VideosSearch(info, limit=1)
        for result in (await results.next())["result"]:
            ytlink = result["link"]
            title = result["title"]
            vidid = result["id"]
            duration_min = result["duration"]
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
        track_details = {
            "title": title,
            "link": ytlink,
            "vidid": vidid,
            "duration_min": duration_min,
            "thumb": thumbnail,
        }
        return track_details, vidid

    async def playlist(self, url):
        playlist = self.spotify.playlist(url)
        playlist_id = playlist["id"]
        results = []
        for item in playlist["tracks"]["items"]:
            music_track = item["track"]
            info = music_track["name"]
            for artist in music_track["artists"]:
                fetched = f' {artist["name"]}'
                if "Various Artists" not in fetched:
                    info += fetched
            results.append(info)
        return results, playlist_id

    async def album(self, url):
        album = self.spotify.album(url)
        album_id = album["id"]
        results = []
        for item in album["tracks"]["items"]:
            info = item["name"]
            for artist in item["artists"]:
                fetched = f' {artist["name"]}'
                if "Various Artists" not in fetched:
                    info += fetched
            results.append(info)

        return (
            results,
            album_id,
        )

    async def artist(self, url):
        artistinfo = self.spotify.artist(url)
        artist_id = artistinfo["id"]
        results = []
        artisttoptracks = self.spotify.artist_top_tracks(url)
        for item in artisttoptracks["tracks"]:
            info = item["name"]
            for artist in item["artists"]:
                fetched = f' {artist["name"]}'
                if "Various Artists" not in fetched:
                    info += fetched
            results.append(info)

        return results, artist_id
