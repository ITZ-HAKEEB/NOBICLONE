#
# Copyright (C) 2026 by Kanha-Team@Github, < https://github.com/Kanha-Team>.
# This file is part of < https://github.com/Kanha-Team/KanhaClone > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/Kanha-Team/KanhaClone/blob/main/LICENSE >
#
# All rights reserved.
#

import math
from pyrogram.types import InlineKeyboardButton
from KanhaClone.utils.formatters import time_to_seconds
import config


import random

def btn(text, style=None, icon=None, **kw):
    try:
        from pyrogram.enums import ButtonStyle
        styles = [
            ButtonStyle.DANGER,
            ButtonStyle.PRIMARY,
            ButtonStyle.SUCCESS,
        ]
        return InlineKeyboardButton(text=text, style=random.choice(styles), **kw)
    except (ImportError, TypeError, AttributeError):
        return InlineKeyboardButton(text=text, **kw)


def track_markup(_, videoid, user_id, channel, fplay):
    buttons = [
        [
            btn(
                text=_["P_B_1"],
                callback_data=f"MusicStream {videoid}|{user_id}|a|{channel}|{fplay}",
            ),
            btn(
                text=_["P_B_2"],
                callback_data=f"MusicStream {videoid}|{user_id}|v|{channel}|{fplay}",
            ),
        ],
        [
            btn(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {videoid}|{user_id}",
            )
        ],
    ]
    return buttons

def stream_markup_timer(_, chat_id, played, dur):
    played_sec = time_to_seconds(played)
    duration_sec = time_to_seconds(dur)
    percentage = (played_sec / duration_sec) * 100
    umm = math.floor(percentage)
    if 0 < umm <= 10: bar = "◉—————————"
    elif 10 < umm < 20: bar = "—◉————————"
    elif 20 <= umm < 30: bar = "——◉———————"
    elif 30 <= umm < 40: bar = "———◉——————"
    elif 40 <= umm < 50: bar = "————◉—————"
    elif 50 <= umm < 60: bar = "—————◉————"
    elif 60 <= umm < 70: bar = "——————◉———"
    elif 70 <= umm < 80: bar = "———————◉——"
    elif 80 <= umm < 95: bar = "————————◉—"
    else: bar = "—————————◉"
    buttons = [
        [btn(text=f"{played} {bar} {dur}", callback_data="GetTimer")],
        [
            btn(text="▷", callback_data=f"ADMIN Resume|{chat_id}"),
            btn(text="II", callback_data=f"ADMIN Pause|{chat_id}"),
            btn(text="↻", callback_data=f"ADMIN Replay|{chat_id}"),
            btn(text="‣‣I", callback_data=f"ADMIN Skip|{chat_id}"),
            btn(text="▢", callback_data=f"ADMIN Stop|{chat_id}"),
        ],
        [btn(text=_["CLOSE_BUTTON"], callback_data="close")]
    ]
    return buttons

def stream_markup(_, chat_id):
    buttons = [
        [
            btn(text="▷", callback_data=f"ADMIN Resume|{chat_id}"),
            btn(text="II", callback_data=f"ADMIN Pause|{chat_id}"),
            btn(text="↻", callback_data=f"ADMIN Replay|{chat_id}"),
            btn(text="‣‣I", callback_data=f"ADMIN Skip|{chat_id}"),
            btn(text="▢", callback_data=f"ADMIN Stop|{chat_id}"),
        ],
        [btn(text=_["CLOSE_BUTTON"], callback_data="close")]
    ]
    return buttons

def playlist_markup(_, videoid, user_id, ptype, channel, fplay):
    buttons = [
        [
            btn(text=_["P_B_1"], callback_data=f"KanhaPlaylists {videoid}|{user_id}|{ptype}|a|{channel}|{fplay}"),
            btn(text=_["P_B_2"], callback_data=f"KanhaPlaylists {videoid}|{user_id}|{ptype}|v|{channel}|{fplay}"),
        ],
        [btn(text=_["CLOSE_BUTTON"], callback_data=f"forceclose {videoid}|{user_id}")],
    ]
    return buttons

def livestream_markup(_, videoid, user_id, mode, channel, fplay):
    buttons = [
        [btn(text=_["P_B_3"], callback_data=f"LiveStream {videoid}|{user_id}|{mode}|{channel}|{fplay}")],
        [btn(text=_["CLOSE_BUTTON"], callback_data=f"forceclose {videoid}|{user_id}")],
    ]
    return buttons

def slider_markup(_, videoid, user_id, query, query_type, channel, fplay):
    query = f"{query[:20]}"
    buttons = [
        [
            btn(text=_["P_B_1"], callback_data=f"MusicStream {videoid}|{user_id}|a|{channel}|{fplay}"),
            btn(text=_["P_B_2"], callback_data=f"MusicStream {videoid}|{user_id}|v|{channel}|{fplay}"),
        ],
        [
            btn(text="◁", callback_data=f"slider B|{query_type}|{query}|{user_id}|{channel}|{fplay}"),
            btn(text=_["CLOSE_BUTTON"], callback_data=f"forceclose {query}|{user_id}"),
            btn(text="▷", callback_data=f"slider F|{query_type}|{query}|{user_id}|{channel}|{fplay}"),
        ],
    ]
    return buttons

def telegram_markup(_, chat_id):
    buttons = [
        [
            btn(text="Next", callback_data=f"PanelMarkup None|{chat_id}"),
            btn(text=_["CLOSEMENU_BUTTON"], callback_data="close"),
        ],
    ]
    return buttons

def queue_markup(_, videoid, chat_id, bot_username):
    buttons = [
        [btn(text=_["S_B_3"], url=f"https://t.me/{bot_username}?startgroup=true")],
        [
            btn(text="II ᴘᴀᴜsᴇ", callback_data=f"ADMIN Pause|{chat_id}"),
            btn(text="▢ sᴛᴏᴘ", callback_data=f"ADMIN Stop|{chat_id}"),
            btn(text="sᴋɪᴘ ‣‣I", callback_data=f"ADMIN Skip|{chat_id}"),
        ],
        [
            btn(text="▷ ʀᴇsᴜᴍᴇ", callback_data=f"ADMIN Resume|{chat_id}"),
            btn(text="ʀᴇᴘʟᴀʏ ↺", callback_data=f"ADMIN Replay|{chat_id}"),
        ],
        [btn(text="ᴍᴏʀᴇ", callback_data=f"PanelMarkup None|{chat_id}")],
    ]
    return buttons

def stream_markup2(_, chat_id, bot_username):
    buttons = [
        [btn(text=_["S_B_3"], url=f"https://t.me/{bot_username}?startgroup=true")],
        [
            btn(text="▷", callback_data=f"ADMIN Resume|{chat_id}"),
            btn(text="II", callback_data=f"ADMIN Pause|{chat_id}"),
            btn(text="↻", callback_data=f"ADMIN Replay|{chat_id}"),
            btn(text="‣‣I", callback_data=f"ADMIN Skip|{chat_id}"),
            btn(text="▢", callback_data=f"ADMIN Stop|{chat_id}"),
        ],
        [btn(text=_["CLOSEMENU_BUTTON"], callback_data="close")],
    ]
    return buttons

def stream_markup_timer2(_, chat_id, played, dur):
    played_sec = time_to_seconds(played)
    duration_sec = time_to_seconds(dur)
    percentage = (played_sec / duration_sec) * 100
    umm = math.floor(percentage)
    if 0 < umm <= 40: bar = "◉——————————"
    elif 10 < umm < 20: bar = "—◉—————————"
    elif 20 < umm < 30: bar = "——◉————————"
    elif 30 <= umm < 40: bar = "———◉———————"
    elif 40 <= umm < 50: bar = "————◉——————"
    elif 50 <= umm < 60: bar = "——————◉————"
    elif 50 <= umm < 70: bar = "———————◉———"
    else: bar = "——————————◉"
    buttons = [
        [btn(text=f"{played} {bar} {dur}", callback_data="GetTimer")],
        [
            btn(text="▷", callback_data=f"ADMIN Resume|{chat_id}"),
            btn(text="II", callback_data=f"ADMIN Pause|{chat_id}"),
            btn(text="↻", callback_data=f"ADMIN Replay|{chat_id}"),
            btn(text="‣‣I", callback_data=f"ADMIN Skip|{chat_id}"),
            btn(text="▢", callback_data=f"ADMIN Stop|{chat_id}"),
        ],
        [btn(text=_["CLOSEMENU_BUTTON"], callback_data="close")],
    ]
    return buttons

def panel_markup_1(_, videoid, chat_id, bot_username):
    buttons = [
        [btn(text=_["S_B_3"], url=f"https://t.me/{bot_username}?startgroup=true")],
        [
            btn(text="sᴜғғʟᴇ", callback_data=f"ADMIN Shuffle|{chat_id}"),
            btn(text="ʟᴏᴏᴘ ↺", callback_data=f"ADMIN Loop|{chat_id}"),
        ],
        [
            btn(text="◁ 10 sᴇᴄ", callback_data=f"ADMIN 1|{chat_id}"),
            btn(text="10 sᴇᴄ ▷", callback_data=f"ADMIN 2|{chat_id}"),
        ],
        [
            btn(text="ʜᴏᴍᴇ", callback_data=f"Pages Back|2|{videoid}|{chat_id}"),
            btn(text="ɴᴇxᴛ", callback_data=f"Pages Forw|2|{videoid}|{chat_id}"),
        ],
    ]
    return buttons

def panel_markup_2(_, videoid, chat_id, bot_username):
    buttons = [
        [btn(text=_["S_B_3"], url=f"https://t.me/{bot_username}?startgroup=true")],
        [
            btn(text="🕒 0.5x", callback_data=f"SpeedUP {chat_id}|0.5"),
            btn(text="🕓 0.75x", callback_data=f"SpeedUP {chat_id}|0.75"),
            btn(text="🕤 1.0x", callback_data=f"SpeedUP {chat_id}|1.0"),
        ],
        [
            btn(text="🕤 1.5x", callback_data=f"SpeedUP {chat_id}|1.5"),
            btn(text="🕛 2.0x", callback_data=f"SpeedUP {chat_id}|2.0"),
        ],
        [btn(text="ʙᴀᴄᴋ", callback_data=f"Pages Back|1|{videoid}|{chat_id}")],
    ]
    return buttons

def panel_markup_3(_, videoid, chat_id):
    buttons = [
        [
            btn(text="🕒 0.5x", callback_data=f"SpeedUP {chat_id}|0.5"),
            btn(text="🕓 0.75x", callback_data=f"SpeedUP {chat_id}|0.75"),
            btn(text="🕤 1.0x", callback_data=f"SpeedUP {chat_id}|1.0"),
        ],
        [
            btn(text="🕤 1.5x", callback_data=f"SpeedUP {chat_id}|1.5"),
            btn(text="🕛 2.0x", callback_data=f"SpeedUP {chat_id}|2.0"),
        ],
        [btn(text="ʙᴀᴄᴋ", callback_data=f"Pages Back|2|{videoid}|{chat_id}")],
    ]
    return buttons

def panel_markup_4(_, vidid, chat_id, played, dur):
    played_sec = time_to_seconds(played)
    duration_sec = time_to_seconds(dur)
    percentage = (played_sec / duration_sec) * 100
    umm = math.floor(percentage)
    if 0 < umm <= 40: bar = "◉——————————"
    elif 10 < umm < 20: bar = "—◉—————————"
    elif 20 < umm < 30: bar = "——◉————————"
    elif 30 <= umm < 40: bar = "———◉———————"
    elif 40 <= umm < 50: bar = "————◉——————"
    elif 50 <= umm < 60: bar = "——————◉————"
    elif 50 <= umm < 70: bar = "———————◉———"
    else: bar = "——————————◉"
    buttons = [
        [btn(text=f"{played} {bar} {dur}", callback_data="GetTimer")],
        [
            btn(text="II ᴘᴀᴜsᴇ", callback_data=f"ADMIN Pause|{chat_id}"),
            btn(text="▢ sᴛᴏᴘ ▢", callback_data=f"ADMIN Stop|{chat_id}"),
            btn(text="sᴋɪᴘ ‣‣I", callback_data=f"ADMIN Skip|{chat_id}"),
        ],
        [
            btn(text="▷ ʀᴇsᴜᴍᴇ", callback_data=f"ADMIN Resume|{chat_id}"),
            btn(text="ʀᴇᴘʟᴀʏ ↺", callback_data=f"ADMIN Replay|{chat_id}"),
        ],
        [btn(text="ʜᴏᴍᴇ", callback_data=f"MainMarkup {vidid}|{chat_id}")],
    ]
    return buttons

def panel_markup_5(_, videoid, chat_id, bot_username):
    buttons = [
        [btn(text=_["S_B_3"], url=f"https:t.me/{bot_username}?startgroup=true")],
        [
            btn(text="ᴘᴀᴜsᴇ", callback_data=f"ADMIN Pause|{chat_id}"),
            btn(text="sᴛᴏᴘ", callback_data=f"ADMIN Stop|{chat_id}"),
            btn(text="sᴋɪᴘ", callback_data=f"ADMIN Skip|{chat_id}"),
        ],
        [
            btn(text="ʀᴇsᴜᴍᴇ", callback_data=f"ADMIN Resume|{chat_id}"),
            btn(text="ʀᴇᴘʟᴀʏ", callback_data=f"ADMIN Replay|{chat_id}"),
        ],
        [
            btn(text="ʜᴏᴍᴇ", callback_data=f"MainMarkup {videoid}|{chat_id}"),
            btn(text="ɴᴇxᴛ", callback_data=f"Pages Forw|1|{videoid}|{chat_id}"),
        ],
    ]
    return buttons

def panel_markup_clone(_, vidid, chat_id):
    buttons = [
        [
            btn(text="▷", callback_data=f"ADMIN Resume|{chat_id}"),
            btn(text="II", callback_data=f"ADMIN Pause|{chat_id}"),
            btn(text="‣‣I", callback_data=f"ADMIN Skip|{chat_id}"),
            btn(text="▢", callback_data=f"ADMIN Stop|{chat_id}"),
        ],
        [btn(text=_["CLOSE_BUTTON"], callback_data="close")]
    ]
    return buttons

