#
# Copyright (C) 2026 by Kanha-Team@Github, < https://github.com/Kanha-Team>.
# This file is part of < https://github.com/Kanha-Team/KanhaClone > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/Kanha-Team/KanhaClone/blob/main/LICENSE >
#
# All rights reserved.
#


import random
from pyrogram import filters, Client
from pyrogram.types import InlineKeyboardMarkup, Message

import config
from KanhaClone import YouTube, app
from KanhaClone.core.call import Kanha
from KanhaClone.misc import db
from KanhaClone.utils.database import get_loop
from KanhaClone.cplugin.utils.decorators.admins import AdminRightsCheck
from KanhaClone.utils.inline import close_markup, stream_markup, stream_markup2
from KanhaClone.utils.stream.autoclear import auto_clean
from KanhaClone.utils.thumbnails import get_thumb
from config import BANNED_USERS
from KanhaClone.utils.database.clonedb import get_owner_id_from_db, get_cloned_support_chat, get_cloned_support_channel


@Client.on_message(
    filters.command(
        ["skip", "cskip", "next", "cnext"], prefixes=["/", "!", "%", ",", ".", "@", "#"]
    )
    & filters.group
    & ~BANNED_USERS
)
@AdminRightsCheck
async def skip(cli, message: Message, _, chat_id):
    a = await cli.get_me()

    C_BOT_SUPPORT_CHAT = await get_cloned_support_chat(a.id)
    C_SUPPORT_CHAT = f"https://t.me/{C_BOT_SUPPORT_CHAT}"

    if not len(message.command) < 2:
        loop = await get_loop(chat_id)
        if loop != 0:
            return await message.reply_text(_["admin_8"])
        state = message.text.split(None, 1)[1].strip()
        if state.isnumeric():
            state = int(state)
            check = db.get(chat_id)
            if check:
                count = len(check)
                if count > 2:
                    count = int(count - 1)
                    if 1 <= state <= count:
                        last_popped = None
                        for x in range(state):
                            popped = None
                            try:
                                popped = check.pop(0)
                                last_popped = popped
                            except:
                                return await message.reply_text(_["admin_12"])
                            if popped:
                                await auto_clean(popped)
                            if not check:
                                try:
                                    await message.reply_text(
                                        text=_["admin_6"].format(
                                            message.from_user.mention,
                                            message.chat.title,
                                        ),
                                        reply_markup=close_markup(_),
                                    )
                                    await Kanha.stop_stream(chat_id)
                                except:
                                    pass
                                return
                    else:
                        return await message.reply_text(_["admin_11"].format(count))
                else:
                    return await message.reply_text(_["admin_10"])
            else:
                return await message.reply_text(_["queue_2"])
        else:
            return await message.reply_text(_["admin_9"])
    else:
        check = db.get(chat_id)
        popped = None
        try:
            popped = check.pop(0)
            if popped:
                await auto_clean(popped)
            if not check:
                await message.reply_text(
                    text=_["admin_6"].format(
                        message.from_user.mention, message.chat.title
                    ),
                    reply_markup=close_markup(_),
                )
                try:
                    return await Kanha.stop_stream(chat_id)
                except:
                    return
        except:
            try:
                await message.reply_text(
                    text=_["admin_6"].format(
                        message.from_user.mention, message.chat.title
                    ),
                    reply_markup=close_markup(_),
                )
                return await Kanha.stop_stream(chat_id)
            except:
                return

    if not check:
        return

    queued = check[0]["file"]
    title = (check[0]["title"]).title()
    user = check[0]["by"]
    streamtype = check[0]["streamtype"]
    videoid = check[0]["vidid"]
    status = True if str(streamtype) == "video" else None
    if db.get(chat_id) and db[chat_id]:
        db[chat_id][0]["played"] = 0
    exis = (check[0]).get("old_dur")
    if exis:
        if db.get(chat_id) and db[chat_id]:
            db[chat_id][0]["dur"] = exis
            db[chat_id][0]["seconds"] = check[0]["old_second"]
            db[chat_id][0]["speed_path"] = None
            db[chat_id][0]["speed"] = 1.0

    if "live_" in queued:
        n, link = await YouTube.video(videoid, True)
        if n == 0:
            return await message.reply_text(_["admin_7"].format(title))
        try:
            image = await YouTube.thumbnail(videoid, True)
        except:
            image = None
        try:
            await Kanha.skip_stream(chat_id, link, video=status, image=image)
        except:
            return await message.reply_text(_["call_6"])
        button = stream_markup2(_, chat_id)
        img = await get_thumb(videoid)
        run = await message.reply_photo(
            photo=img,
            caption=_["stream_1"].format(
                f"https://www.youtube.com/watch?v={videoid}",
                title[:23],
                check[0]["dur"],
                user,
            ),
            reply_markup=InlineKeyboardMarkup(button),
        )
        if db.get(chat_id) and db[chat_id]:
            db[chat_id][0]["mystic"] = run
            db[chat_id][0]["markup"] = "tg"
    elif "vid_" in queued:
        mystic = await message.reply_text(_["call_7"], disable_web_page_preview=True)
        try:
            file_path, direct = await YouTube.download(
                videoid,
                mystic,
                videoid=True,
                video=status,
            )
        except:
            return await mystic.edit_text(_["call_6"])
        try:
            image = await YouTube.thumbnail(videoid, True)
        except:
            image = None
        try:
            await Kanha.skip_stream(chat_id, file_path, video=status, image=image)
        except:
            return await mystic.edit_text(_["call_6"])
        button = stream_markup(_, chat_id)
        img = await get_thumb(videoid)
        run = await message.reply_photo(
            photo=img,
            caption=_["stream_1"].format(
                f"https://www.youtube.com/watch?v={videoid}",
                title[:23],
                check[0]["dur"],
                user,
            ),
            reply_markup=InlineKeyboardMarkup(button),
        )
        if db.get(chat_id) and db[chat_id]:
            db[chat_id][0]["mystic"] = run
            db[chat_id][0]["markup"] = "stream"
        await mystic.delete()
    elif "index_" in queued:
        try:
            await Kanha.skip_stream(chat_id, videoid, video=status)
        except:
            return await message.reply_text(_["call_6"])
        button = stream_markup2(_, chat_id)

        if isinstance(config.STREAM_IMG_URL, list):
            img_url = random.choice(config.STREAM_IMG_URL)
        else:
            img_url = config.STREAM_IMG_URL

        run = await message.reply_photo(
            photo=img_url,
            caption=_["stream_2"].format(user),
            reply_markup=InlineKeyboardMarkup(button),
        )
        if db.get(chat_id) and db[chat_id]:
            db[chat_id][0]["mystic"] = run
            db[chat_id][0]["markup"] = "tg"
    else:
        if videoid == "telegram":
            image = None
        elif videoid == "soundcloud":
            image = None
        else:
            try:
                image = await YouTube.thumbnail(videoid, True)
            except:
                image = None
        try:
            await Kanha.skip_stream(chat_id, queued, video=status, image=image)
        except:
            return await message.reply_text(_["call_6"])

        if videoid == "telegram":
            button = stream_markup2(_, chat_id)

            if str(streamtype) == "audio":
                if isinstance(config.TELEGRAM_AUDIO_URL, list):
                    img_url = random.choice(config.TELEGRAM_AUDIO_URL)
                else:
                    img_url = config.TELEGRAM_AUDIO_URL
            else:
                if isinstance(config.TELEGRAM_VIDEO_URL, list):
                    img_url = random.choice(config.TELEGRAM_VIDEO_URL)
                else:
                    img_url = config.TELEGRAM_VIDEO_URL

            run = await message.reply_photo(
                photo=img_url,
                caption=_["stream_1"].format(
                    C_SUPPORT_CHAT, title[:23], check[0]["dur"], user
                ),
                reply_markup=InlineKeyboardMarkup(button),
            )
            if db.get(chat_id) and db[chat_id]:
                db[chat_id][0]["mystic"] = run
                db[chat_id][0]["markup"] = "tg"
        elif videoid == "soundcloud":
            button = stream_markup2(_, chat_id)

            if str(streamtype) == "audio":
                if isinstance(config.SOUNCLOUD_IMG_URL, list):
                    img_url = random.choice(config.SOUNCLOUD_IMG_URL)
                else:
                    img_url = config.SOUNCLOUD_IMG_URL
            else:
                if isinstance(config.TELEGRAM_VIDEO_URL, list):
                    img_url = random.choice(config.TELEGRAM_VIDEO_URL)
                else:
                    img_url = config.TELEGRAM_VIDEO_URL

            run = await message.reply_photo(
                photo=img_url,
                caption=_["stream_1"].format(
                    C_SUPPORT_CHAT, title[:23], check[0]["dur"], user
                ),
                reply_markup=InlineKeyboardMarkup(button),
            )
            if db.get(chat_id) and db[chat_id]:
                db[chat_id][0]["mystic"] = run
                db[chat_id][0]["markup"] = "tg"
        else:
            button = stream_markup(_, chat_id)
            img = await get_thumb(videoid)
            run = await message.reply_photo(
                photo=img,
                caption=_["stream_1"].format(
                    f"https://www.youtube.com/watch?v={videoid}",
                    title[:23],
                    check[0]["dur"],
                    user,
                ),
                reply_markup=InlineKeyboardMarkup(button),
            )
            if db.get(chat_id) and db[chat_id]:
                db[chat_id][0]["mystic"] = run
                db[chat_id][0]["markup"] = "stream"
