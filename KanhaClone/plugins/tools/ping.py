#
# Copyright (C) 2026 by Kanha-Team@Github, < https://github.com/Kanha-Team>.
# This file is part of < https://github.com/Kanha-Team/KanhaClone > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/Kanha-Team/KanhaClone/blob/main/LICENSE >
#
# All rights reserved.
#

import random
from datetime import datetime

from pyrogram import filters
from pyrogram.types import Message
from config import *
from KanhaClone import app
from KanhaClone.core.call import Kanha
from KanhaClone.utils import bot_sys_stats
from KanhaClone.utils.decorators.language import language
from KanhaClone.utils.inline import supp_markup
from config import BANNED_USERS, PING_IMG_URL

FALLBACK_IMG = "https://telegra.ph/file/2e3d368e77c449c287430.jpg"

def _pick_img(img):
    """Return a single valid URL string from str or list."""
    if not img:
        return FALLBACK_IMG
    if isinstance(img, list):
        chosen = random.choice(img)
        return chosen if isinstance(chosen, str) and chosen.startswith("http") else FALLBACK_IMG
    return img if isinstance(img, str) else FALLBACK_IMG


@app.on_message(filters.command("ping", prefixes=["/", "!", "%", ",", "", ".", "@", "#"]) & ~BANNED_USERS)
@language
async def ping_com(client, message: Message, _):
    start = datetime.now()
    try:
        response = await message.reply_photo(
            photo=_pick_img(PING_IMG_URL),
            caption=_["ping_1"].format(app.mention),
        )
        pytgping = await Kanha.ping()
        UP, CPU, RAM, DISK = await bot_sys_stats()
        resp = (datetime.now() - start).microseconds / 1000
        await response.edit_caption(
            caption=_["ping_2"].format(resp, app.mention, UP, RAM, CPU, DISK, pytgping),
            reply_markup=supp_markup(_),
        )
    except Exception:
        # Fallback: text only agar photo fail ho
        try:
            pytgping = await Kanha.ping()
            UP, CPU, RAM, DISK = await bot_sys_stats()
            resp = (datetime.now() - start).microseconds / 1000
            await message.reply_text(
                _["ping_2"].format(resp, app.mention, UP, RAM, CPU, DISK, pytgping),
                reply_markup=supp_markup(_),
            )
        except Exception:
            pass
