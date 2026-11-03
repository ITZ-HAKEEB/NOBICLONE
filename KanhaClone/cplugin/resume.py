#
# Copyright (C) 2026 by Kanha-Team@Github, < https://github.com/Kanha-Team>.
# This file is part of < https://github.com/Kanha-Team/KanhaClone > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/Kanha-Team/KanhaClone/blob/main/LICENSE >
#
# All rights reserved.
#

from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup

from KanhaClone import app
from KanhaClone.core.call import Kanha
from KanhaClone.utils.inline import close_markup
from config import BANNED_USERS
# Hum Database functions import kar rahe hain taaki state save rahe
from KanhaClone.utils.database import is_music_playing, music_on

from KanhaClone.cplugin.utils.decorators.admins import AdminRightsCheck

@Client.on_message(
    filters.command(["resume", "cresume"]) & filters.group & ~BANNED_USERS
)
@AdminRightsCheck # <-- Ab ye Clone Owner/Sudo ko allow karega
async def resume_com(cli, message: Message, _, chat_id):
    # Check karega ki kya music already chal raha hai?
    if await is_music_playing(chat_id):
        return await message.reply_text(_["admin_3"])
    
    # Music ko ON mark karega (Global Memory mein)
    await music_on(chat_id)
    
    # Stream ko Resume karega
    await Kanha.resume_stream(chat_id)
    
    buttons_resume = [
        [
            InlineKeyboardButton(text="sᴋɪᴘ", callback_data=f"ADMIN Skip|{chat_id}"),
            InlineKeyboardButton(text="sᴛᴏᴘ", callback_data=f"ADMIN Stop|{chat_id}"),
        ],
        [
            InlineKeyboardButton(
                text="ᴘᴀᴜsᴇ",
                callback_data=f"ADMIN Pause|{chat_id}",
            ),
        ],
    ]
    await message.reply_text(
        _["admin_4"].format(message.from_user.mention),
        reply_markup=InlineKeyboardMarkup(buttons_resume),
    )
