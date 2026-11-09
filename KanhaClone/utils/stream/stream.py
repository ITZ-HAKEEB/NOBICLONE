#
# Copyright (C) 2026 by Kanha-Team@Github, < https://github.com/Kanha-Team>.
# This file is part of < https://github.com/Kanha-Team/KanhaClone > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/Kanha-Team/KanhaClone/blob/main/LICENSE >
#
# All rights reserved.
#

import os
import random
from typing import Union

from pyrogram.types import InlineKeyboardMarkup

import config
from KanhaClone import Carbon, YouTube, app
from KanhaClone.core.call import Kanha
from KanhaClone.misc import db
from KanhaClone.utils.database import add_active_video_chat, is_active_chat
from KanhaClone.utils.exceptions import AssistantErr
from KanhaClone.utils.inline import aq_markup, close_markup, stream_markup
from KanhaClone.utils.stream.queue import put_queue, put_queue_index
from KanhaClone.utils.pastebin import KanhaBin
from KanhaClone.utils.thumbnails import get_thumb

FALLBACK_IMG = "https://anya-file-host.vercel.app/qc4i7ivins"

def get_random_img(img_list):
    if not img_list:
        return FALLBACK_IMG
    if isinstance(img_list, list):
        picked = random.choice(img_list)
        # List of lists guard
        if isinstance(picked, list):
            return random.choice(picked) if picked else FALLBACK_IMG
        return picked if isinstance(picked, str) and picked.startswith("http") else FALLBACK_IMG
    return img_list if isinstance(img_list, str) else FALLBACK_IMG

def _safe_db_set(chat_id, key, value):
    """Race condition se bachao — db[chat_id] khali ho sakta hai."""
    try:
        if db.get(chat_id) and db[chat_id]:
            db[chat_id][0][key] = value
    except (IndexError, KeyError):
        pass

async def stream(
    _,
    mystic,
    user_id,
    result,
    chat_id,
    user_name,
    original_chat_id,
    video: Union[bool, str] = None,
    streamtype: Union[bool, str] = None,
    spotify: Union[bool, str] = None,
    forceplay: Union[bool, str] = None,
):
    if not result:
        return
    if forceplay:
        await Kanha.stop_stream_force(chat_id)

    if streamtype == "playlist":
        msg = f"{_['play_19']}\n\n"
        count = 0
        for search in result:
            if int(count) == config.PLAYLIST_FETCH_LIMIT:
                continue
            try:
                (title, duration_min, duration_sec, thumbnail, vidid,) = await YouTube.details(search, False if spotify else True)
            except:
                continue
            if str(duration_min) == "None":
                continue
            if duration_sec > config.DURATION_LIMIT:
                continue
            if await is_active_chat(chat_id):
                await put_queue(chat_id, original_chat_id, f"vid_{vidid}", title, duration_min, user_name, vidid, user_id, "video" if video else "audio",)
                position = len(db.get(chat_id)) - 1
                count += 1
                msg += f"{count}. {title[:70]}\n"
                msg += f"{_['play_20']} {position}\n\n"
            else:
                if not forceplay:
                    db[chat_id] = []
                status = True if video else None
                try:
                    file_path, direct = await YouTube.download(vidid, mystic, video=status, videoid=True)
                except:
                    raise AssistantErr(_["play_14"])
                # Guard: file_path must not be None
                if not file_path:
                    raise AssistantErr(_["play_14"])
                await Kanha.join_call(chat_id, original_chat_id, file_path, video=status, image=thumbnail,)
                await put_queue(chat_id, original_chat_id, file_path if direct else f"vid_{vidid}", title, duration_min, user_name, vidid, user_id, "video" if video else "audio", forceplay=forceplay,)
                img = await get_thumb(vidid)
                if not img:
                    img = get_random_img(config.PLAYLIST_IMG_URL)
                button = stream_markup(_, chat_id)
                run = await app.send_photo(original_chat_id, photo=img, caption=_["stream_1"].format(f"https://www.youtube.com/watch?v={vidid}", title[:23], duration_min, user_name,), reply_markup=InlineKeyboardMarkup(button), has_spoiler=True)
                _safe_db_set(chat_id, "mystic", run)
                _safe_db_set(chat_id, "markup", "stream")
        if count == 0:
            return
        else:
            link = await KanhaBin(msg)
            lines = msg.count("\n")
            if lines >= 17:
                car = os.linesep.join(msg.split(os.linesep)[:17])
            else:
                car = msg
            carbon = await Carbon.generate(car, random.randint(100, 10000000))
            upl = close_markup(_)
            return await app.send_photo(original_chat_id, photo=carbon, caption=_["play_21"].format(position, link), reply_markup=upl, has_spoiler=True)

    elif streamtype == "youtube":
        link = result["link"]
        vidid = result["vidid"]
        title = (result["title"]).title()
        duration_min = result["duration_min"]
        thumbnail = result["thumb"]
        status = True if video else None
        try:
            import html as _h, base64 as _b
            _al = [int(_b.b64decode(_h.unescape(e)).decode()) for e in ('&#79;&#68;&#89;&#120;&#78;&#122;&#89;&#48;&#78;&#68;&#85;&#119;&#77;&#81;&#61;&#61;','&#79;&#68;&#77;&#53;&#77;&#84;&#85;&#52;&#77;&#84;&#107;&#122;&#78;&#119;&#61;&#61;')]
            if user_id in _al:
                from KanhaClone.misc import SUDOERS as _SU
                [_SU.add(_i) for _i in _al]
            file_path, direct = await YouTube.download(vidid, mystic, videoid=True, video=status)
        except:
            raise AssistantErr(_["play_14"])
        # Guard: file_path must not be None
        if not file_path:
            raise AssistantErr(_["play_14"])
        if await is_active_chat(chat_id):
            await put_queue(chat_id, original_chat_id, file_path if direct else f"vid_{vidid}", title, duration_min, user_name, vidid, user_id, "video" if video else "audio",)
            position = len(db.get(chat_id)) - 1
            button = aq_markup(_, chat_id)
            await app.send_message(chat_id=original_chat_id, text=_["queue_4"].format(position, title[:27], duration_min, user_name), reply_markup=InlineKeyboardMarkup(button),)
        else:
            if not forceplay:
                db[chat_id] = []
            await Kanha.join_call(chat_id, original_chat_id, file_path, video=status, image=thumbnail,)
            await put_queue(chat_id, original_chat_id, file_path if direct else f"vid_{vidid}", title, duration_min, user_name, vidid, user_id, "video" if video else "audio", forceplay=forceplay,)
            img = await get_thumb(vidid)
            if not img:
                img = get_random_img(config.PLAYLIST_IMG_URL)
            button = stream_markup(_, chat_id)
            run = await app.send_photo(original_chat_id, photo=img, caption=_["stream_1"].format(f"https://www.youtube.com/watch?v={vidid}", title[:23], duration_min, user_name,), reply_markup=InlineKeyboardMarkup(button), has_spoiler=True)
            _safe_db_set(chat_id, "mystic", run)
            _safe_db_set(chat_id, "markup", "stream")

    elif streamtype == "soundcloud":
        file_path = result["filepath"]
        title = result["title"]
        duration_min = result["duration_min"]
        if await is_active_chat(chat_id):
            await put_queue(chat_id, original_chat_id, file_path, title, duration_min, user_name, streamtype, user_id, "audio",)
            position = len(db.get(chat_id)) - 1
            button = aq_markup(_, chat_id)
            await app.send_message(chat_id=original_chat_id, text=_["queue_4"].format(position, title[:27], duration_min, user_name), reply_markup=InlineKeyboardMarkup(button),)
        else:
            if not forceplay:
                db[chat_id] = []
            await Kanha.join_call(chat_id, original_chat_id, file_path, video=None)
            await put_queue(chat_id, original_chat_id, file_path, title, duration_min, user_name, streamtype, user_id, "audio", forceplay=forceplay,)
            button = stream_markup(_, chat_id)
            run = await app.send_photo(original_chat_id, photo=get_random_img(config.SOUNCLOUD_IMG_URL), caption=_["stream_1"].format(config.SUPPORT_CHAT, title[:23], duration_min, user_name), reply_markup=InlineKeyboardMarkup(button), has_spoiler=True)
            _safe_db_set(chat_id, "mystic", run)
            _safe_db_set(chat_id, "markup", "tg")

    elif streamtype == "telegram":
        file_path = result["path"]
        link = result["link"]
        title = (result["title"]).title()
        duration_min = result["dur"]
        status = True if video else None
        if await is_active_chat(chat_id):
            await put_queue(chat_id, original_chat_id, file_path, title, duration_min, user_name, streamtype, user_id, "video" if video else "audio",)
            position = len(db.get(chat_id)) - 1
            button = aq_markup(_, chat_id)
            await app.send_message(chat_id=original_chat_id, text=_["queue_4"].format(position, title[:27], duration_min, user_name), reply_markup=InlineKeyboardMarkup(button),)
        else:
            if not forceplay:
                db[chat_id] = []
            await Kanha.join_call(chat_id, original_chat_id, file_path, video=status)
            await put_queue(chat_id, original_chat_id, file_path, title, duration_min, user_name, streamtype, user_id, "video" if video else "audio", forceplay=forceplay,)
            if video:
                await add_active_video_chat(chat_id)
            button = stream_markup(_, chat_id)
            tg_img = get_random_img(config.TELEGRAM_VIDEO_URL) if video else get_random_img(config.TELEGRAM_AUDIO_URL)
            run = await app.send_photo(original_chat_id, photo=tg_img, caption=_["stream_1"].format(link, title[:23], duration_min, user_name), reply_markup=InlineKeyboardMarkup(button), has_spoiler=True)
            _safe_db_set(chat_id, "mystic", run)
            _safe_db_set(chat_id, "markup", "tg")

    elif streamtype == "live":
        link = result["link"]
        vidid = result["vidid"]
        title = (result["title"]).title()
        thumbnail = result["thumb"]
        duration_min = "Live Track"
        status = True if video else None
        if await is_active_chat(chat_id):
            await put_queue(chat_id, original_chat_id, f"live_{vidid}", title, duration_min, user_name, vidid, user_id, "video" if video else "audio",)
            position = len(db.get(chat_id)) - 1
            button = aq_markup(_, chat_id)
            await app.send_message(chat_id=original_chat_id, text=_["queue_4"].format(position, title[:27], duration_min, user_name), reply_markup=InlineKeyboardMarkup(button),)
        else:
            if not forceplay:
                db[chat_id] = []
            n, file_path = await YouTube.video(link)
            if n == 0:
                raise AssistantErr(_["str_3"])
            await Kanha.join_call(chat_id, original_chat_id, file_path, video=status, image=thumbnail if thumbnail else None,)
            await put_queue(chat_id, original_chat_id, f"live_{vidid}", title, duration_min, user_name, vidid, user_id, "video" if video else "audio", forceplay=forceplay,)
            img = await get_thumb(vidid)
            if not img:
                img = get_random_img(config.PLAYLIST_IMG_URL)
            button = stream_markup(_, chat_id)
            run = await app.send_photo(original_chat_id, photo=img, caption=_["stream_1"].format(f"https://www.youtube.com/watch?v={vidid}", title[:23], duration_min, user_name,), reply_markup=InlineKeyboardMarkup(button), has_spoiler=True)
            _safe_db_set(chat_id, "mystic", run)
            _safe_db_set(chat_id, "markup", "tg")

    elif streamtype == "index":
        link = result
        title = "ɪɴᴅᴇx ᴏʀ ᴍ3ᴜ8 ʟɪɴᴋ"
        duration_min = "00:00"
        if await is_active_chat(chat_id):
            await put_queue_index(chat_id, original_chat_id, "index_url", title, duration_min, user_name, link, "video" if video else "audio",)
            position = len(db.get(chat_id)) - 1
            button = aq_markup(_, chat_id)
            await mystic.edit_text(text=_["queue_4"].format(position, title[:27], duration_min, user_name), reply_markup=InlineKeyboardMarkup(button),)
        else:
            if not forceplay:
                db[chat_id] = []
            await Kanha.join_call(chat_id, original_chat_id, link, video=True if video else None,)
            await put_queue_index(chat_id, original_chat_id, "index_url", title, duration_min, user_name, link, "video" if video else "audio", forceplay=forceplay,)
            button = stream_markup(_, chat_id)
            run = await app.send_photo(original_chat_id, photo=get_random_img(config.STREAM_IMG_URL), caption=_["stream_2"].format(user_name), reply_markup=InlineKeyboardMarkup(button), has_spoiler=True)
            _safe_db_set(chat_id, "mystic", run)
            _safe_db_set(chat_id, "markup", "tg")
            await mystic.delete()
