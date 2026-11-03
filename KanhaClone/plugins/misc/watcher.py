#
# Copyright (C) 2026 by Kanha-Team@Github, < https://github.com/Kanha-Team>.
# This file is part of < https://github.com/Kanha-Team/KanhaClone > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/Kanha-Team/KanhaClone/blob/main/LICENSE >
#
# All rights reserved.
#

from pyrogram import filters
from pyrogram.types import Message

from KanhaClone import app
from KanhaClone.core.call import Kanha

welcome = 20
close = 30


@app.on_message(filters.video_chat_started, group=welcome)
@app.on_message(filters.video_chat_ended, group=close)
async def welcome(_, message: Message):
    await Kanha.stop_stream_force(message.chat.id)
