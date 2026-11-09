#
# Copyright (C) 2026 by Kanha-Team@Github, < https://github.com/Kanha-Team>.
# This file is part of < https://github.com/Kanha-Team/KanhaClone > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/Kanha-Team/KanhaClone/blob/main/LICENSE >
#
# All rights reserved.
#

import random 
from pyrogram.types import InlineKeyboardButton
import config
from KanhaClone import app


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


def start_panel(_):
    buttons = [
        [
            btn(
                text=_["SO_B_1"], 
                url=f"https://t.me/{app.username}?startgroup=true"
            ),
            btn(text=_["S_B_2"], url=config.SUPPORT_CHAT),
        ],
    ]
    return buttons

def private_panel(_):
    buttons = [
        [
            btn(
                text=_["S_B_3"],
                url=f"https://t.me/{app.username}?startgroup=true",
            )
        ],
        [
            btn(
                text=_["S_B_10"],
                callback_data="Kanha_Anu"),
            btn(
                text="💌 ʏᴛ-ᴀᴘɪ",
                callback_data="api_status"),
        ],
        [
            btn(
                text="🖨 ᴄʟᴏɴᴇ",
                callback_data="nobi"
            ),
            btn(
                text="🛡️ ᴘʀɪᴠᴀᴄʏ",
                url="https://ibb.co/QFDnHvFJ",
            ),
        ],
        [
            btn(text=_["S_B_4"], callback_data="settings_back_helper")
        ],
    ]
    return buttons

def support_panel(_):
    buttons = [
        [
            btn(text=_["S_B_2"], url=config.SUPPORT_CHAT),
            btn(text=_["S_B_6"], url=config.SUPPORT_CHANNEL),
        ],
        [
            btn(text=_["BACK_BUTTON"], callback_data="settingsback_helper")
        ]
    ]
    return buttons

def about_panel(_):
    buttons = [
        [
            btn(text=_["S_B_5"], user_id=config.OWNER_ID),
            btn(text=_["S_B_11"], url=config.GITHUB),
        ],
        [
            btn(text=_["S_B_6"], url=config.SUPPORT_CHANNEL),
            btn(text=_["S_B_2"], url=config.SUPPORT_CHAT)
        ],
        [
            btn(text=_["BACK_BUTTON"], callback_data="settingsback_helper")
        ]
    ]
    return buttons


