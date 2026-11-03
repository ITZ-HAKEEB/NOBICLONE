#
# Copyright (C) 2026 by Kanha-Team@Github, < https://github.com/Kanha-Team>.
# This file is part of < https://github.com/Kanha-Team/KanhaClone > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/Kanha-Team/KanhaClone/blob/main/LICENSE >
#
# All rights reserved.
#

from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

buttons = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(text="▷", callback_data="resume_cb"),
            InlineKeyboardButton(text="II", callback_data="pause_cb"),
            InlineKeyboardButton(text="‣‣I", callback_data="skip_cb"),
            InlineKeyboardButton(text="▢", callback_data="end_cb"),
        ]
    ]
)

close_key = InlineKeyboardMarkup(
    [[InlineKeyboardButton(text="✯ ᴄʟᴏsᴇ ✯", callback_data="close")]]
)



def stream_markup(chat_id):
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(text="▷", callback_data=f"ADMIN Resume|{chat_id}"),
                InlineKeyboardButton(text="II", callback_data=f"ADMIN Pause|{chat_id}"),
                InlineKeyboardButton(text="‣‣I", callback_data=f"ADMIN Skip|{chat_id}"),
                InlineKeyboardButton(text="▢", callback_data=f"ADMIN Stop|{chat_id}"),
            ],
            [
                InlineKeyboardButton(text="✯ ᴄʟᴏsᴇ ✯", callback_data="close")
            ]
        ]
    )
