#
# Copyright (C) 2026 by Kanha-Team@Github, < https://github.com/Kanha-Team>.
# This file is part of < https://github.com/Kanha-Team/KanhaClone > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/Kanha-Team/KanhaClone/blob/main/LICENSE >
#
# All rights reserved.
#

from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from KanhaClone import app
from KanhaClone.core.call import Kanha
from KanhaClone.utils.database import music_off
from config import BANNED_USERS

from KanhaClone.cplugin.utils.decorators.admins import AdminRightsCheck

@Client.on_message(filters.command(["pause", "cpause"]) & filters.group & ~BANNED_USERS)
@AdminRightsCheck # <-- Ab ye Clone Owner/Sudo ko allow karega
async def pause_admin(cli, message: Message, _, chat_id):
    
    # Music ko Database me OFF mark karo (Taaki Resume command ko pata chale)
    await music_off(chat_id)
    
    # Asli stream ko pause karo
    await Kanha.pause_stream(chat_id)

    buttons = [
        [
            InlineKeyboardButton(
                text="ʀᴇsᴜᴍᴇ", callback_data=f"ADMIN Resume|{chat_id}"
            ),
            InlineKeyboardButton(
                text="ʀᴇᴘʟᴀʏ", callback_data=f"ADMIN Replay|{chat_id}"
            ),
        ],
    ]

    await message.reply_text(
        _["admin_2"].format(message.from_user.mention),
        reply_markup=InlineKeyboardMarkup(buttons),
    )
