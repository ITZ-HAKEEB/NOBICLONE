#
# Copyright (C) 2026 by Kanha-Team@Github, < https://github.com/Kanha-Team>.
# This file is part of < https://github.com/Kanha-Team/KanhaClone > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/Kanha-Team/KanhaClone/blob/main/LICENSE >
#
# All rights reserved.
#

from typing import Union

from pyrogram.types import InlineKeyboardButton


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



def setting_markup(_):
    buttons = [
        [
            btn(text=_["ST_B_1"], callback_data="AU"),
            btn(text=_["ST_B_3"], callback_data="LG"),
        ],
        [
            btn(text=_["ST_B_2"], callback_data="PM"),
        ],
        [
            btn(text=_["ST_B_4"], callback_data="VM"),
        ],
        [
            btn(text=_["CLOSE_BUTTON"], callback_data="close"),
        ],
    ]
    return buttons


def vote_mode_markup(_, current, mode: Union[bool, str] = None):
    buttons = [
        [
            btn(text="Vᴏᴛɪɴɢ ᴍᴏᴅᴇ ➜", callback_data="VOTEANSWER"),
            btn(
                text=_["ST_B_5"] if mode == True else _["ST_B_6"],
                callback_data="VOMODECHANGE",
            ),
        ],
        [
            btn(text="-2", callback_data="FERRARIUDTI M"),
            btn(
                text=f"ᴄᴜʀʀᴇɴᴛ : {current}",
                callback_data="ANSWERVOMODE",
            ),
            btn(text="+2", callback_data="FERRARIUDTI A"),
        ],
        [
            btn(
                text=_["BACK_BUTTON"],
                callback_data="settings_helper",
            ),
            btn(text=_["CLOSE_BUTTON"], callback_data="close"),
        ],
    ]
    return buttons


def auth_users_markup(_, status: Union[bool, str] = None):
    buttons = [
        [
            btn(text=_["ST_B_7"], callback_data="AUTHANSWER"),
            btn(
                text=_["ST_B_8"] if status == True else _["ST_B_9"],
                callback_data="AUTH",
            ),
        ],
        [
            btn(text=_["ST_B_1"], callback_data="AUTHLIST"),
        ],
        [
            btn(
                text=_["BACK_BUTTON"],
                callback_data="settings_helper",
            ),
            btn(text=_["CLOSE_BUTTON"], callback_data="close"),
        ],
    ]
    return buttons


def playmode_users_markup(
    _,
    Direct: Union[bool, str] = None,
    Group: Union[bool, str] = None,
    Playtype: Union[bool, str] = None,
):
    buttons = [
        [
            btn(text=_["ST_B_10"], callback_data="SEARCHANSWER"),
            btn(
                text=_["ST_B_11"] if Direct == True else _["ST_B_12"],
                callback_data="MODECHANGE",
            ),
        ],
        [
            btn(text=_["ST_B_13"], callback_data="AUTHANSWER"),
            btn(
                text=_["ST_B_8"] if Group == True else _["ST_B_9"],
                callback_data="CHANNELMODECHANGE",
            ),
        ],
        [
            btn(text=_["ST_B_14"], callback_data="PLAYTYPEANSWER"),
            btn(
                text=_["ST_B_8"] if Playtype == True else _["ST_B_9"],
                callback_data="PLAYTYPECHANGE",
            ),
        ],
        [
            btn(
                text=_["BACK_BUTTON"],
                callback_data="settings_helper",
            ),
            btn(text=_["CLOSE_BUTTON"], callback_data="close"),
        ],
    ]
    return buttons
