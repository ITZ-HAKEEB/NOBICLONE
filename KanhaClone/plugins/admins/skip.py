#
# Copyright (C) 2026 by Kanha-Team@Github, < https://github.com/Kanha-Team>.
# This file is part of < https://github.com/Kanha-Team/KanhaClone > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/Kanha-Team/KanhaClone/blob/main/LICENSE >
#
# All rights reserved.
#

import random
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, Message

import config
from KanhaClone import YouTube, app
from KanhaClone.core.call import Kanha
from KanhaClone.misc import db
from KanhaClone.utils.database import get_loop
from KanhaClone.utils.decorators import AdminRightsCheck
from KanhaClone.utils.inline import close_markup, stream_markup, stream_markup2
from KanhaClone.utils.stream.autoclear import auto_clean
from KanhaClone.utils.thumbnails import get_thumb
from config import BANNED_USERS


def get_random_img(img_list):
    if img_list:
        if isinstance(img_list, list):
            return random.choice(img_list)
        return img_list
    return "https://telegra.ph/file/2e3d368e77c449c287430.jpg"  # Fallback


def _safe_db_set(chat_id, key, value):
    if db.get(chat_id) and db[chat_id]:
        db[chat_id][0][key] = value


async def _reply_photo_safe(target, photo, caption, reply_markup, has_spoiler=True):
    try:
        return await target.reply_photo(
            photo=photo,
            caption=caption,
            reply_markup=reply_markup,
            has_spoiler=has_spoiler,
        )
    except Exception:
        try:
            return await target.reply_text(caption, reply_markup=reply_markup)
        except Exception:
            return None


@app.on_message(
    filters.command(["skip", "cskip", "next", "cnext"]) & filters.group & ~BANNED_USERS
)
@AdminRightsCheck
async def skip(cli, message: Message, _, chat_id):
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
                                    return
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

    if not db.get(chat_id) or not db[chat_id]:
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
        if not img:
            img = get_random_img(config.PLAYLIST_IMG_URL)
        run = await _reply_photo_safe(
            message,
            img,
            _["stream_1"].format(
                f"https://www.youtube.com/watch?v={videoid}",
                title[:23],
                check[0]["dur"],
                user,
            ),
            InlineKeyboardMarkup(button),
        )
        _safe_db_set(chat_id, "mystic", run)
        _safe_db_set(chat_id, "markup", "tg")

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
        if not img:
            img = get_random_img(config.PLAYLIST_IMG_URL)
        run = await _reply_photo_safe(
            message,
            img,
            _["stream_1"].format(
                f"https://www.youtube.com/watch?v={videoid}",
                title[:23],
                check[0]["dur"],
                user,
            ),
            InlineKeyboardMarkup(button),
        )
        _safe_db_set(chat_id, "mystic", run)
        _safe_db_set(chat_id, "markup", "stream")
        await mystic.delete()

    elif "index_" in queued:
        try:
            await Kanha.skip_stream(chat_id, videoid, video=status)
        except:
            return await message.reply_text(_["call_6"])
        button = stream_markup2(_, chat_id)
        run = await _reply_photo_safe(
            message,
            get_random_img(config.STREAM_IMG_URL),
            _["stream_2"].format(user),
            InlineKeyboardMarkup(button),
        )
        _safe_db_set(chat_id, "mystic", run)
        _safe_db_set(chat_id, "markup", "tg")

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
            tg_img = get_random_img(config.TELEGRAM_AUDIO_URL) if str(streamtype) == "audio" else get_random_img(config.TELEGRAM_VIDEO_URL)
            run = await _reply_photo_safe(
                message,
                tg_img,
                _["stream_1"].format(config.SUPPORT_CHAT, title[:23], check[0]["dur"], user),
                InlineKeyboardMarkup(button),
            )
            _safe_db_set(chat_id, "mystic", run)
            _safe_db_set(chat_id, "markup", "tg")

        elif videoid == "soundcloud":
            button = stream_markup2(_, chat_id)
            sc_img = get_random_img(config.SOUNCLOUD_IMG_URL) if str(streamtype) == "audio" else get_random_img(config.TELEGRAM_VIDEO_URL)
            run = await _reply_photo_safe(
                message,
                sc_img,
                _["stream_1"].format(config.SUPPORT_CHAT, title[:23], check[0]["dur"], user),
                InlineKeyboardMarkup(button),
            )
            _safe_db_set(chat_id, "mystic", run)
            _safe_db_set(chat_id, "markup", "tg")

        else:
            button = stream_markup(_, chat_id)
            img = await get_thumb(videoid)
            if not img:
                img = get_random_img(config.PLAYLIST_IMG_URL)
            run = await _reply_photo_safe(
                message,
                img,
                _["stream_1"].format(
                    f"https://www.youtube.com/watch?v={videoid}",
                    title[:23],
                    check[0]["dur"],
                    user,
                ),
                InlineKeyboardMarkup(button),
            )
            _safe_db_set(chat_id, "mystic", run)
            _safe_db_set(chat_id, "markup", "stream")
