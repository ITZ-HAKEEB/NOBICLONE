#
# Copyright (C) 2026 by Kanha-Team@Github, < https://github.com/Kanha-Team>.
# This file is part of < https://github.com/Kanha-Team/KanhaClone > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/Kanha-Team/KanhaClone/blob/main/LICENSE >
#
# All rights reserved.
#

import asyncio
import os
import random
from datetime import datetime, timedelta
from typing import Union

from pyrogram import Client
from pyrogram.types import InlineKeyboardMarkup
from ntgcalls import ConnectionNotFound, TelegramServerError
from pytgcalls import PyTgCalls, exceptions, types

import config
from KanhaClone import LOGGER, YouTube, app
from KanhaClone.misc import db
from KanhaClone.utils.decorators.admins import FORCE_JOIN_LINKS
from KanhaClone.utils.database import (
    add_active_chat,
    add_active_video_chat,
    get_lang,
    get_loop,
    group_assistant,
    is_autoend,
    music_on,
    remove_active_chat,
    remove_active_video_chat,
    set_loop,
)
from KanhaClone.utils.exceptions import AssistantErr
from KanhaClone.utils.formatters import check_duration, seconds_to_min, speed_converter
from KanhaClone.utils.inline.play import stream_markup, telegram_markup
from KanhaClone.utils.stream.autoclear import auto_clean
from KanhaClone.utils.thumbnails import get_thumb
from strings import get_string


autoend = {}
counter = {}


def get_random_img(img_list):
    if isinstance(img_list, (list, tuple)):
        return random.choice(img_list) if img_list else "https://telegra.ph/file/2e3d368e77c449c287430.jpg"
    return img_list or "https://telegra.ph/file/2e3d368e77c449c287430.jpg"


async def delete_old_message(chat_id: int):
    try:
        old = db.get(chat_id, [{}])[0].get("mystic")
        if old:
            await old.delete()
    except Exception:
        pass


async def _clear_(chat_id: int):
    db[chat_id] = []
    try:
        await remove_active_video_chat(chat_id)
    finally:
        await remove_active_chat(chat_id)


class Call(PyTgCalls):
    """KanhaClone voice-chat manager with multiple configured and custom assistants."""

    def __init__(self):
        # Do not inherit from PyTgCalls for the manager itself; individual clients do the work.
        self.assistants = {}
        self.userbots = {}
        self.custom_assistants = {}
        self.active_clients = {}

        for index in range(1, 6):
            session = getattr(config, f"STRING{index}", None)
            if not session:
                continue
            userbot = Client(
                name=f"KanhaAss{index}",
                api_id=config.API_ID,
                api_hash=config.API_HASH,
                session_string=str(session),
            )
            assistant = PyTgCalls(userbot, cache_duration=100)
            self.userbots[index] = userbot
            self.assistants[index] = assistant

        # Keep compatibility with existing code that expects self.one.
        self.userbot1 = self.userbots.get(1)
        self.one = self.assistants.get(1)
        self.two = self.assistants.get(2)
        self.three = self.assistants.get(3)
        self.four = self.assistants.get(4)
        self.five = self.assistants.get(5)

    async def _configured_assistants(self):
        return list(self.assistants.values())

    async def get_active_clients(self, chat_id: int):
        value = self.active_clients.get(chat_id, [])
        if not isinstance(value, list):
            value = [value]
        clients = [client for client in value if client]
        if clients:
            return list(dict.fromkeys(clients))
        try:
            assistant = await group_assistant(self, chat_id)
            if assistant:
                return [assistant]
        except Exception:
            pass
        return (await self._configured_assistants())[:1]

    def _remember_client(self, chat_id: int, assistant):
        clients = self.active_clients.setdefault(chat_id, [])
        if not isinstance(clients, list):
            clients = [clients]
            self.active_clients[chat_id] = clients
        if assistant not in clients:
            clients.append(assistant)

    def _safe_set(self, chat_id, key, value):
        try:
            if db.get(chat_id) and db[chat_id]:
                db[chat_id][0][key] = value
        except (IndexError, KeyError, TypeError):
            pass

    def _make_stream(self, link, video=False, ffmpeg=None):
        """Build a py-tgcalls 3.0.0 MediaStream."""
        if not link:
            raise AssistantErr("Invalid or empty media source.")
        return types.MediaStream(
            media_path=link,
            audio_parameters=types.AudioQuality.HIGH,
            video_parameters=types.VideoQuality.HD_720p,
            audio_flags=types.MediaStream.Flags.REQUIRED,
            video_flags=(
                types.MediaStream.Flags.AUTO_DETECT
                if video
                else types.MediaStream.Flags.IGNORE
            ),
            ffmpeg_parameters=ffmpeg,
        )

    async def _change_on_clients(self, chat_id: int, stream, clients=None):
        clients = clients or await self.get_active_clients(chat_id)
        successes = 0
        last_error = None
        for assistant in clients:
            try:
                await assistant.play(chat_id=chat_id, stream=stream, config=types.GroupCallConfig(auto_start=False))
                successes += 1
            except Exception as exc:
                last_error = exc
        if not successes and last_error:
            raise last_error

    async def pause_stream(self, chat_id: int, assistant_type=None):
        await delete_old_message(chat_id)
        for assistant in await self.get_active_clients(chat_id):
            try:
                await assistant.pause(chat_id)
            except Exception:
                pass

    async def resume_stream(self, chat_id: int, assistant_type=None):
        await delete_old_message(chat_id)
        for assistant in await self.get_active_clients(chat_id):
            try:
                await assistant.resume(chat_id)
            except Exception:
                pass

    async def stop_stream(self, chat_id: int, assistant_type=None):
        await delete_old_message(chat_id)
        clients = await self.get_active_clients(chat_id)
        try:
            await _clear_(chat_id)
        except Exception:
            pass
        for assistant in clients:
            try:
                await assistant.leave_call(chat_id, close=False)
            except Exception:
                pass
        self.active_clients.pop(chat_id, None)

    async def stop_stream_force(self, chat_id: int):
        clients = await self.get_active_clients(chat_id)
        for assistant in clients:
            try:
                await assistant.leave_call(chat_id, close=False)
            except Exception:
                pass
        # Also attempt all configured assistants in case active-client tracking was lost.
        for assistant in await self._configured_assistants():
            try:
                await assistant.leave_call(chat_id, close=False)
            except Exception:
                pass
        self.active_clients.pop(chat_id, None)
        try:
            await _clear_(chat_id)
        except Exception:
            pass

    async def force_stop_stream(self, chat_id: int):
        await self.stop_stream_force(chat_id)

    async def speedup_stream(self, chat_id: int, file_path, speed, playing):
        clients = await self.get_active_clients(chat_id)
        if not clients:
            raise AssistantErr("No assistant is available.")
        if str(speed) != "1.0":
            base = os.path.basename(file_path)
            chatdir = os.path.join(os.getcwd(), "playback", str(speed))
            os.makedirs(chatdir, exist_ok=True)
            out = os.path.join(chatdir, base)
            if not os.path.isfile(out):
                video_factor = {"0.5": 2.0, "0.75": 1.35, "1.5": 0.68, "2.0": 0.5}.get(str(speed), 1.0)
                proc = await asyncio.create_subprocess_exec(
                    "ffmpeg", "-y", "-i", file_path,
                    "-filter:v", f"setpts={video_factor}*PTS",
                    "-filter:a", f"atempo={speed}", out,
                    stdout=asyncio.subprocess.DEVNULL,
                    stderr=asyncio.subprocess.PIPE,
                )
                _stdout, stderr = await proc.communicate()
                if proc.returncode != 0 or not os.path.isfile(out):
                    raise AssistantErr("FFmpeg could not prepare the requested playback speed.")
        else:
            out = file_path

        dur = await asyncio.get_running_loop().run_in_executor(None, check_duration, out)
        dur = int(dur)
        played, con_seconds = speed_converter(playing[0]["played"], speed)
        duration = seconds_to_min(dur)
        ffmpeg = f"-ss {played} -to {duration}"
        stream = self._make_stream(out, playing[0]["streamtype"] == "video", ffmpeg)
        if not db.get(chat_id) or str(db[chat_id][0].get("file")) != str(file_path):
            raise AssistantErr("Umm")
        await self._change_on_clients(chat_id, stream, clients)
        if not db.get(chat_id):
            return
        if not db[chat_id][0].get("old_dur"):
            db[chat_id][0]["old_dur"] = db[chat_id][0].get("dur")
            db[chat_id][0]["old_second"] = db[chat_id][0].get("seconds")
        db[chat_id][0].update({
            "played": con_seconds,
            "dur": duration,
            "seconds": dur,
            "speed_path": out,
            "speed": speed,
        })

    async def skip_stream(self, chat_id: int, link: str, video: Union[bool, str] = None,
                          image: Union[bool, str] = None, assistant_type=None):
        stream = self._make_stream(link, bool(video))
        await self._change_on_clients(chat_id, stream)

    async def seek_stream(self, chat_id, file_path, to_seek, duration, mode):
        stream = self._make_stream(file_path, mode == "video", f"-ss {to_seek} -to {duration}")
        await self._change_on_clients(chat_id, stream)

    async def stream_call(self, link):
        assistant = await group_assistant(self, config.LOGGER_ID)
        try:
            await assistant.play(
                chat_id=config.LOGGER_ID,
                stream=self._make_stream(link, video=True),
                config=types.GroupCallConfig(auto_start=False),
            )
            await asyncio.sleep(0.2)
        finally:
            try:
                await assistant.leave_call(config.LOGGER_ID, close=False)
            except Exception:
                pass

    async def _get_custom_assistant(self, userbot):
        me = await userbot.get_me()
        user_id = me.id
        assistant = self.custom_assistants.get(user_id)
        if assistant:
            return assistant
        assistant = PyTgCalls(userbot, cache_duration=100)
        await assistant.start()

        @assistant.on_update()
        async def _custom_update_handler(_, update: types.Update):
            if isinstance(update, types.StreamEnded):
                if update.stream_type == types.StreamEnded.Type.AUDIO:
                    await self.change_stream(assistant, update.chat_id)
            elif isinstance(update, types.ChatUpdate):
                if update.status in (
                    types.ChatUpdate.Status.KICKED,
                    types.ChatUpdate.Status.LEFT_GROUP,
                    types.ChatUpdate.Status.CLOSED_VOICE_CHAT,
                ):
                    await self.stop_stream(update.chat_id)

        self.custom_assistants[user_id] = assistant
        return assistant

    async def join_call(self, chat_id: int, original_chat_id: int, link,
                        video: Union[bool, str] = None, image: Union[bool, str] = None,
                        userbot=None):
        language = await get_lang(chat_id)
        _ = get_string(language)
        if not link:
            raise AssistantErr(_["play_14"])

        if userbot:
            for invite in FORCE_JOIN_LINKS:
                try:
                    await userbot.join_chat(invite)
                    await asyncio.sleep(0.5)
                except Exception:
                    pass
            assistant = await self._get_custom_assistant(userbot)
        else:
            assistant = await group_assistant(self, chat_id)
            if not assistant:
                configured = await self._configured_assistants()
                if not configured:
                    raise AssistantErr("No assistant session configured.")
                assistant = configured[0]

        self._remember_client(chat_id, assistant)
        stream = self._make_stream(link, bool(video))
        try:
            await assistant.play(
                chat_id=chat_id,
                stream=stream,
                config=types.GroupCallConfig(auto_start=False),
            )
        except exceptions.NoActiveGroupCall:
            raise AssistantErr(_["call_8"])
        except exceptions.NoAudioSourceFound:
            raise AssistantErr(_["call_10"])
        except (ConnectionNotFound, TelegramServerError, TimeoutError, asyncio.TimeoutError):
            raise AssistantErr(_["call_10"])
        except Exception:
            raise AssistantErr(_["call_10"])
        await add_active_chat(chat_id)
        await music_on(chat_id)
        if video:
            await add_active_video_chat(chat_id)
        if await is_autoend():
            counter[chat_id] = {}
            try:
                users = len(await assistant.get_participants(chat_id))
                if users == 1:
                    autoend[chat_id] = datetime.now() + timedelta(minutes=1)
            except Exception:
                pass

    async def change_stream(self, client, chat_id: int):
        check = db.get(chat_id)
        if not check:
            try:
                await _clear_(chat_id)
            except Exception:
                pass
            self.active_clients.pop(chat_id, None)
            try:
                await client.leave_call(chat_id, close=False)
            except Exception:
                pass
            return

        popped = None
        loop = await get_loop(chat_id)
        try:
            if loop == 0:
                popped = check.pop(0)
            else:
                await set_loop(chat_id, loop - 1)
            if popped:
                await auto_clean(popped)
            if not check:
                await _clear_(chat_id)
                self.active_clients.pop(chat_id, None)
                try:
                    await app.send_message(chat_id, "💮 ᴛʜє ǫᴜєᴜє ʜᴧs ғɪηɪsʜєᴅ.\n\n💐 ᴜsє /play ᴛσ ᴧᴅᴅ ᴍσꝛє sσηɢs..!")
                except Exception:
                    pass
                return await client.leave_call(chat_id, close=False)
        except Exception:
            try:
                await _clear_(chat_id)
            except Exception:
                pass
            self.active_clients.pop(chat_id, None)
            try:
                return await client.leave_call(chat_id, close=False)
            except Exception:
                return

        queued = check[0].get("file")
        language = await get_lang(chat_id)
        _ = get_string(language)
        title = str(check[0].get("title", "Unknown track")).title()
        user = check[0].get("by", "Unknown")
        original_chat_id = check[0].get("chat_id", chat_id)
        streamtype = check[0].get("streamtype", "audio")
        videoid = check[0].get("vidid", "")
        self._safe_set(chat_id, "played", 0)

        if check[0].get("old_dur"):
            self._safe_set(chat_id, "dur", check[0]["old_dur"])
            self._safe_set(chat_id, "seconds", check[0].get("old_second"))
            self._safe_set(chat_id, "speed_path", None)
            self._safe_set(chat_id, "speed", 1.0)

        video = str(streamtype) == "video"
        chat_client = check[0].get("client") or app

        if "live_" in str(queued):
            result, link = await YouTube.video(videoid, True)
            if result == 0:
                return await chat_client.send_message(original_chat_id, _["call_6"])
            stream = self._make_stream(link, video)
            try:
                await self._change_on_clients(chat_id, stream)
            except Exception:
                return await chat_client.send_message(original_chat_id, _["call_6"])
            img = get_random_img(config.STREAM_IMG_URL)
            buttons = telegram_markup(_, chat_id)
            message = await chat_client.send_photo(
                chat_id=original_chat_id, photo=img,
                caption=_["stream_1"].format(f"https://www.youtube.com/watch?v={videoid}", title[:23], check[0].get("dur", "--:--"), user),
                reply_markup=InlineKeyboardMarkup(buttons), has_spoiler=True,
            )
            self._safe_set(chat_id, "mystic", message)
            self._safe_set(chat_id, "markup", "tg")

        elif "vid_" in str(queued):
            mystic = await chat_client.send_message(original_chat_id, _["call_7"])
            try:
                file_path, _direct = await YouTube.download(videoid, mystic, videoid=True, video=video)
            except Exception:
                try:
                    file_path, _direct = await YouTube.download(videoid, mystic, videoid=True, video=video)
                except Exception:
                    return await mystic.edit_text(_["call_6"], disable_web_page_preview=True)
            try:
                await self._change_on_clients(chat_id, self._make_stream(file_path, video))
            except Exception:
                return await chat_client.send_message(original_chat_id, _["call_6"])
            img = await get_thumb(videoid) or get_random_img(config.PLAYLIST_IMG_URL)
            buttons = stream_markup(_, chat_id)
            await mystic.delete()
            message = await chat_client.send_photo(
                chat_id=original_chat_id, photo=img,
                caption=_["stream_1"].format(f"https://www.youtube.com/watch?v={videoid}", title[:23], check[0].get("dur", "--:--"), user),
                reply_markup=InlineKeyboardMarkup(buttons), has_spoiler=True,
            )
            self._safe_set(chat_id, "mystic", message)
            self._safe_set(chat_id, "markup", "stream")

        elif "index_" in str(queued):
            try:
                await self._change_on_clients(chat_id, self._make_stream(videoid, video))
            except Exception:
                return await chat_client.send_message(original_chat_id, _["call_6"])
            message = await chat_client.send_photo(
                chat_id=original_chat_id, photo=get_random_img(config.STREAM_IMG_URL),
                caption=_["stream_2"].format(user),
                reply_markup=InlineKeyboardMarkup(telegram_markup(_, chat_id)), has_spoiler=True,
            )
            self._safe_set(chat_id, "mystic", message)
            self._safe_set(chat_id, "markup", "tg")

        else:
            try:
                await self._change_on_clients(chat_id, self._make_stream(queued, video))
            except Exception:
                return await chat_client.send_message(original_chat_id, _["call_6"])

            if videoid == "telegram":
                image = get_random_img(config.TELEGRAM_VIDEO_URL if video else config.TELEGRAM_AUDIO_URL)
                buttons = telegram_markup(_, chat_id)
                markup_type = "tg"
                caption = _["stream_1"].format(config.SUPPORT_CHAT, title[:23], check[0].get("dur", "--:--"), user)
            elif videoid == "soundcloud":
                image = get_random_img(config.SOUNCLOUD_IMG_URL)
                buttons = telegram_markup(_, chat_id)
                markup_type = "tg"
                caption = _["stream_1"].format(config.SUPPORT_CHAT, title[:23], check[0].get("dur", "--:--"), user)
            else:
                image = await get_thumb(videoid) or get_random_img(config.PLAYLIST_IMG_URL)
                buttons = stream_markup(_, chat_id)
                markup_type = "stream"
                caption = _["stream_1"].format(f"https://www.youtube.com/watch?v={videoid}", title[:23], check[0].get("dur", "--:--"), user)
            message = await chat_client.send_photo(
                chat_id=original_chat_id, photo=image, caption=caption,
                reply_markup=InlineKeyboardMarkup(buttons), has_spoiler=True,
            )
            self._safe_set(chat_id, "mystic", message)
            self._safe_set(chat_id, "markup", markup_type)

    async def ping(self):
        pings = []
        for assistant in await self._configured_assistants():
            try:
                value = assistant.ping
                if asyncio.iscoroutine(value):
                    value = await value
                pings.append(float(value))
            except Exception:
                pass
        return str(round(sum(pings) / len(pings), 3)) if pings else "0"    
    async def start(self):
        LOGGER(__name__).info("Starting PyTgCalls assistants...\n")
        for assistant in await self._configured_assistants():
            try:
                await assistant.start()
            except Exception as exc:
                LOGGER(__name__).warning(
                    "Could not start an assistant: %s", exc
                )

    async def decorators(self):
        for assistant in await self._configured_assistants():
            on_update = getattr(assistant, "on_update", None)

            if on_update is None:
                LOGGER(__name__).warning(
                    "PyTgCalls does not provide on_update(); "
                    "check the installed version and event API."
                )
                continue

            @on_update()
            async def _update_handler(_, update, _client=assistant):
                try:
                    if isinstance(update, types.StreamEnded):
                        if update.stream_type == types.StreamEnded.Type.AUDIO:
                            await self.change_stream(
                                _client, update.chat_id
                            )

                    elif isinstance(update, types.ChatUpdate):
                        if update.status in (
                            types.ChatUpdate.Status.KICKED,
                            types.ChatUpdate.Status.LEFT_GROUP,
                            types.ChatUpdate.Status.CLOSED_VOICE_CHAT,
                        ):
                            await self.stop_stream(update.chat_id)

                except Exception as exc:
                    LOGGER(__name__).warning(
                        "Assistant update handler error: %s", exc
                    )


Kanha = Call()
