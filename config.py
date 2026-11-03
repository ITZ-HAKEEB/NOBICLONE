#
# Copyright (C) 2026 by Kanha-Team@Github, < https://github.com/Kanha-Team>.
# This file is part of < https://github.com/Kanha-Team/KanhaClone > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/Kanha-Team/KanhaClone/blob/main/LICENSE >
#
# All rights reserved.
#

import re
from os import getenv
from dotenv import load_dotenv
from pyrogram import filters

load_dotenv()


def _env(name, default=None):
    """Read an env var, treating empty / whitespace-only values as missing."""
    value = getenv(name)
    if value is None:
        return default
    value = value.strip()
    return value or default


def _int_env(name, default=None, required=False):
    """Read an int env var with a readable error instead of a bare ValueError."""
    raw = _env(name)
    if raw is None:
        if required:
            raise SystemExit(
                f"[ERROR] - {name} is missing. Add it to your .env file "
                "(see sample.env)."
            )
        return default
    try:
        return int(raw)
    except ValueError:
        raise SystemExit(f"[ERROR] - {name} must be a number, got: {raw!r}")


API_ID = _int_env("API_ID", 0)
API_HASH = _env("API_HASH")

BOT_TOKEN = _env("BOT_TOKEN")
BOT_ID = _env("BOT_ID")

OWNER_USERNAME = _env("OWNER_USERNAME", "")
BOT_USERNAME = _env("BOT_USERNAME", "")
BOT_NAME = _env("BOT_NAME", "")
ASSUSERNAME = _env("ASSUSERNAME", "")
BOT_LINK = _env("BOT_LINK", "https://t.me/MeowClonerbot")

# MONGO_URI is accepted as an alias so older .env files keep working.
MONGO_DB_URI = _env("MONGO_DB_URI") or _env("MONGO_URI")


DURATION_LIMIT_MIN = _int_env("DURATION_LIMIT", 17000)

LOGGER_ID = _int_env("LOGGER_ID", required=True)
CLONE_LOGGER = LOGGER_ID
CLONE_GC = _int_env("CLONE_GC", 0)
OWNER_ID = _int_env("OWNER_ID", 0)

HEROKU_APP_NAME = getenv("HEROKU_APP_NAME")
HEROKU_API_KEY = getenv("HEROKU_API_KEY")


UPSTREAM_BRANCH = getenv("UPSTREAM_BRANCH", "main")
GIT_TOKEN = getenv("GIT_TOKEN", "")

SUPPORT_CHANNEL = getenv("SUPPORT_CHANNEL", "https://t.me/Meowcloner")
SUPPORT_CHAT = getenv("SUPPORT_CHAT", "https://t.me/MeowClone")


AUTO_LEAVING_ASSISTANT = getenv("AUTO_LEAVING_ASSISTANT", "False")
AUTO_LEAVE_ASSISTANT_TIME = _int_env("ASSISTANT_LEAVE_TIME", 9000)

SONG_DOWNLOAD_DURATION = _int_env("SONG_DOWNLOAD_DURATION", 9999999)
SONG_DOWNLOAD_DURATION_LIMIT = _int_env("SONG_DOWNLOAD_DURATION_LIMIT", 9999999)

SPOTIFY_CLIENT_ID = getenv("SPOTIFY_CLIENT_ID", "1c21247d714244ddbb09925dac565aed")
SPOTIFY_CLIENT_SECRET = getenv("SPOTIFY_CLIENT_SECRET", "709e1a2969664491b58200860623ef19")

PLAYLIST_FETCH_LIMIT = _int_env("PLAYLIST_FETCH_LIMIT", 25)
PLAYLIST_ID = -1001980154960

TG_AUDIO_FILESIZE_LIMIT = _int_env("TG_AUDIO_FILESIZE_LIMIT", 5242880000)
TG_VIDEO_FILESIZE_LIMIT = _int_env("TG_VIDEO_FILESIZE_LIMIT", 5242880000)

STRING1 = _env("STRING_SESSION", "")
STRING2 = _env("STRING_SESSION2")

BANNED_USERS = filters.user()
adminlist = {}
lyrical = {}
votemode = {}
autoclean = []
confirmer = {}

# --- Updated Image URLs ---
_IMG_LIST = [
    "https://files.catbox.moe/v00l7e.jpg",
    "https://files.catbox.moe/uow54p.jpg",
    "https://files.catbox.moe/z0t6l3.jpg",
    "https://files.catbox.moe/jdw0il.jpg",
    "https://files.catbox.moe/izfi0y.jpg",
    "https://files.catbox.moe/7wx3ha.jpg",
    "https://files.catbox.moe/2u0srm.jpg",
    "https://files.catbox.moe/tqwy0q.jpg",
    "https://files.catbox.moe/vbgrx1.jpg"
]
START_IMG_URL = getenv("START_IMG_URL", _IMG_LIST)
HELP_IMG_URL = getenv("HELP_IMG_URL", "https://files.catbox.moe/v00l7e.jpg")
PING_IMG_URL = getenv("PING_IMG_URL", _IMG_LIST)

PLAYLIST_IMG_URL = getenv("PLAYLIST_IMG_URL", "https://files.catbox.moe/z0t6l3.jpg")
STATS_IMG_URL = getenv("STATS_IMG_URL", "https://files.catbox.moe/7wx3ha.jpg")
TELEGRAM_AUDIO_URL = getenv("TELEGRAM_AUDIO_URL", "https://files.catbox.moe/7wx3ha.jpg")
TELEGRAM_VIDEO_URL = getenv("TELEGRAM_VIDEO_URL", "https://files.catbox.moe/7wx3ha.jpg")
STREAM_IMG_URL = getenv("STREAM_IMG_URL", "https://files.catbox.moe/vbgrx1.jpg")
SOUNCLOUD_IMG_URL = getenv("SOUNCLOUD_IMG_URL", "https://files.catbox.moe/vbgrx1.jpg")
YOUTUBE_IMG_URL = getenv("YOUTUBE_IMG_URL", "https://files.catbox.moe/vbgrx1.jpg")
SPOTIFY_ARTIST_IMG_URL = getenv("SPOTIFY_ARTIST_IMG_URL", "https://files.catbox.moe/vbgrx1.jpg")
SPOTIFY_ALBUM_IMG_URL = getenv("SPOTIFY_ALBUM_IMG_URL", "https://files.catbox.moe/vbgrx1.jpg")
SPOTIFY_PLAYLIST_IMG_URL = getenv("SPOTIFY_PLAYLIST_IMG_URL", "https://files.catbox.moe/vbgrx1.jpg")

def time_to_seconds(time):
    return sum(int(x) * 60**i for i, x in enumerate(reversed(str(time).split(":"))))

DURATION_LIMIT = int(time_to_seconds(f"{DURATION_LIMIT_MIN}:00"))

if SUPPORT_CHANNEL and not re.match("(?:http|https)://", SUPPORT_CHANNEL):
    raise SystemExit("[ERROR] - SUPPORT_CHANNEL url must start with https://")

if SUPPORT_CHAT and not re.match("(?:http|https)://", SUPPORT_CHAT):
    raise SystemExit("[ERROR] - SUPPORT_CHAT url must start with https://")

CMBOT = [
    "💞", "🩷", "🩷", "🩷", "🩷", "🩵", "🩵", "🩶", "🩵", "🩶",
    "🩶", "🩷", "🩵", "🩶", "🩷", "🩶", "🩵", "🩷", "🩷", "🩵",
    "🩶", "🩶", "🩵", "🩶", "🩶", "🩷", "🩵", "🩶"
]

EFFECT_ID = [
    5104841245755180586,
    5107584321108051014,
    5104841245755180586,
    5107584321108051014,
    5104841245755180586,
    5107584321108051014,
    5104841245755180586,
    5107584321108051014,
]
