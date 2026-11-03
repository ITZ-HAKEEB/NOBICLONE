#
# Copyright (C) 2026 by Kanha-Team@Github, < https://github.com/Kanha-Team>.
# This file is part of < https://github.com/Kanha-Team/KanhaClone > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/Kanha-Team/KanhaClone/blob/main/LICENSE >
#
# All rights reserved.
#

from typing import Union
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
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


def help_pannel(_, START: Union[bool, int] = None):
    first = [
        [
            btn(text=_["H_B_1"], callback_data="help_callback hb1"),
            btn(text=_["H_B_2"], callback_data="help_callback hb2"),
            btn(text=_["H_B_3"], callback_data="help_callback hb3"),
        ],
        [
            btn(text=_["H_B_4"], callback_data="help_callback hb4"),
            btn(text=_["H_B_5"], callback_data="help_callback hb5"),
            btn(text=_["H_B_6"], callback_data="help_callback hb6"),
        ],
        [
            btn(text=_["H_B_7"], callback_data="help_callback hb7"),
            btn(text=_["H_B_8"], callback_data="help_callback hb8"),
            btn(text=_["H_B_9"], callback_data="help_callback hb9"),
        ],
        [
            btn(text="ᴄʟᴏɴᴇ ғᴇᴀᴛυʀᴇs", callback_data="help_callback clone_main"),
        ],
        [
            btn(text=_["BACK_BUTTON"], callback_data="settingsback_helper"),
        ],
    ]
    return InlineKeyboardMarkup(first)


def first_page(_, is_owner: bool = False):
    first = []

    if is_owner:
        first.append([
            btn(text="ᴄʟσηᴇ ғᴇᴀᴛυʀᴇs", callback_data="help_callback chelp"),
        ])

    first += [
        [
            btn(text=_["H_B_1"], callback_data="help_callback hb1"),
            btn(text=_["H_B_2"], callback_data="help_callback hb2"),
            btn(text=_["H_B_3"], callback_data="help_callback hb3"),
        ],
        [
            btn(text=_["H_B_4"], callback_data="help_callback hb4"),
            btn(text=_["H_B_5"], callback_data="help_callback hb5"),
            btn(text=_["H_B_6"], callback_data="help_callback hb6"),
        ],
        [
            btn(text=_["H_B_7"], callback_data="help_callback hb7"),
            btn(text=_["H_B_8"], callback_data="help_callback hb8"),
            btn(text=_["H_B_9"], callback_data="help_callback hb9"),
        ],
        [
            btn(text=_["BACK_BUTTON"], callback_data="settingsback_home"),
        ],
    ]

    return InlineKeyboardMarkup(first)


def clone_help_panel(_):
    buttons = [
        [
            btn(text="ᴍᴀɴᴀɢᴇ", callback_data="help_callback clone_manage"),
        ],
        [
            btn(text="sᴛᴀʀᴛ", callback_data="help_callback clone_start"),
            btn(text="ᴘɪɴɢ", callback_data="help_callback clone_ping"),
        ],
        [
            btn(text="ᴘʟᴀʏ ᴍᴏᴅᴇ", callback_data="help_callback clone_play"),
            btn(text="ʟσɢɢᴇʀ", callback_data="help_callback clone_logger"),
        ],
        [
            btn(text="ʙυᴛᴛσηs & ʀᴇɴᴀᴍᴇ", callback_data="help_callback clone_buttons"),
        ],
        [
            btn(text=_["BACK_BUTTON"], callback_data="settings_back_helper"),
        ],
    ]
    return InlineKeyboardMarkup(buttons)


def clone_back_markup(_):
    return InlineKeyboardMarkup(
        [
            [
                btn(
                    text=_["BACK_BUTTON"],
                    callback_data="help_callback chelp",
                )
            ]
        ]
    )


def help_back_markup(_):
    return InlineKeyboardMarkup(
        [
            [
                btn(
                    text=_["BACK_BUTTON"],
                    callback_data="settings_back_helper",
                )
            ]
        ]
    )


def private_help_panel(_):
    return InlineKeyboardMarkup(
        [
            [
                btn(
                    text=_["S_B_4"],
                    url=f"https://t.me/{app.username}?start=help",
                )
            ]
        ]
    )
