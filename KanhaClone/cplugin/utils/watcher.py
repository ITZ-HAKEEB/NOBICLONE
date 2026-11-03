#
# Copyright (C) 2026 by Kanha-Team@Github, < https://github.com/Kanha-Team>.
# This file is part of < https://github.com/Kanha-Team/KanhaClone > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/Kanha-Team/KanhaClone/blob/main/LICENSE >
#
# All rights reserved.
#

from pyrogram import filters, Client
from pyrogram.types import Message

from KanhaClone import app
from KanhaClone.core.call import Kanha
from KanhaClone.misc import db

welcome = 20
close = 30

@Client.on_message(filters.video_chat_started, group=welcome)
@Client.on_message(filters.video_chat_ended, group=close)
async def video_chat_events(_, message: Message):
    # Stream ko force stop karega
    await Kanha.stop_stream_force(message.chat.id)
    
    try:
        db[message.chat.id] = []
    except:
        pass
