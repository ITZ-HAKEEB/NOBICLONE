#
# Copyright (C) 2026 by Kanha-Team@Github, < https://github.com/Kanha-Team>.
# This file is part of < https://github.com/Kanha-Team/KanhaClone > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/Kanha-Team/KanhaClone/blob/main/LICENSE >
#
# All rights reserved.
#

import time
import random
import asyncio
import logging
from pyrogram import filters, Client
from pyrogram.enums import ChatType, ParseMode
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, InputMediaPhoto, InputMediaVideo
from py_yt import VideosSearch

import config
from KanhaClone import app
from KanhaClone.misc import _boot_, SUDOERS
from KanhaClone.plugins.sudo.sudoers import sudoers_list
from KanhaClone.utils.formatters import get_readable_time

from config import BANNED_USERS, OWNER_ID, START_IMG_URL

# Module Imports
from KanhaClone.utils.decorators.language import LanguageStart, languageCB
from KanhaClone.utils.database.clonedb import get_owner_id_from_db, get_cloned_support_chat, get_cloned_support_channel, is_premium
from KanhaClone.utils.database import add_served_user, add_served_user_clone, add_served_chat_clone
from KanhaClone.utils.database import clonebotdb

# Extra Import for Transfer Logic
from KanhaClone.core.mongo import mongodb


import random
from KanhaClone.utils.database.clonedb import is_premium

def btn(text, style=None, icon=None, **kw):
    try:
        from pyrogram.enums import ButtonStyle
        styles = [
            ButtonStyle.DANGER,
            ButtonStyle.PRIMARY,
            ButtonStyle.SUCCESS,
        ]
        return InlineKeyboardButton(text=text, style=random.choice(styles), **kw)
    except (ImportError, TypeError, AttributeError):
        return InlineKeyboardButton(text=text, **kw)

cloneownerdb = mongodb.cloneownerdb

# Initialize logging
LOG = logging.getLogger(__name__)

# Fallback Effect IDs
DEFAULT_EFFECT_IDS = [
    5104841245755180586,
    5107584321108051014,
    5104841245755180586,
    5107584321108051014,
    5104841245755180586,
    5107584321108051014,
    5104841245755180586,
    5107584321108051014,
]

# =====================================================================
# INTERNAL BUTTON HELPERS
# =====================================================================

def make_start_panel(bot_username, owner_url, 
                     txt_add, txt_support, txt_channel, txt_owner, txt_help, 
                     support_chat, support_channel,
                     custom_btn=None, btn_pos="TOP"):
    
    buttons = []

    # 1. Add Me (full width)
    if txt_add != "HIDDEN":
        buttons.append([btn(text=txt_add, url=f"https://t.me/{bot_username}?startgroup=true")])

    # 2. Developer + YT-Api (side by side)
    row_dev = []
    if txt_owner != "HIDDEN":
        row_dev.append(btn(text=txt_owner, url=owner_url))
    row_dev.append(btn(text="💌 ʏᴛ-ᴀᴘɪ", callback_data="bot_info_data"))
    buttons.append(row_dev)

    # 3. Update + Support (side by side)
    row_support = []
    if txt_channel != "HIDDEN":
        row_support.append(btn(text=txt_channel, url=support_channel))
    if txt_support != "HIDDEN":
        row_support.append(btn(text=txt_support, url=support_chat))
    if row_support:
        buttons.append(row_support)

    # 4. Help Command (full width)
    if txt_help != "HIDDEN":
        buttons.append([btn(text=txt_help, callback_data="settings_back_helper")])

    # --- Custom Button Logic ---
    if custom_btn and custom_btn.get("text"):
        c_btn = btn(text=custom_btn["text"], url=custom_btn["url"])
        if btn_pos in ["UP", "TOP"]:
            buttons.insert(0, [c_btn])
        elif btn_pos in ["DOWN", "BOTTOM"]:
            buttons.append([c_btn])
        elif btn_pos in ["MID", "MIDDLE"]:
            if len(buttons) >= 1:
                buttons.insert(1, [c_btn])
            else:
                buttons.append([c_btn])
        else:
            buttons.insert(0, [c_btn])

    return InlineKeyboardMarkup(buttons)


def make_gp_panel(bot_username, txt_add, txt_support, support_chat):
    buttons = [
        [
            btn(text=txt_add, url=f"https://t.me/{bot_username}?startgroup=true"),
            btn(text=txt_support, url=support_chat),
        ]
    ]
    return InlineKeyboardMarkup(buttons)

# =====================================================================
# Database Helpers
# =====================================================================

async def get_start_image(bot_id):
    d = await clonebotdb.find_one({"bot_id": bot_id}) or {}
    return d.get("start_image")

async def get_start_caption(bot_id):
    d = await clonebotdb.find_one({"bot_id": bot_id}) or {}
    return d.get("start_caption")

async def get_start_button(bot_id):
    d = await clonebotdb.find_one({"bot_id": bot_id}) or {}
    return d.get("start_button")

async def get_start_btn_pos(bot_id):
    d = await clonebotdb.find_one({"bot_id": bot_id}) or {}
    return d.get("start_btn_pos", "TOP")

async def get_start_video(bot_id):
    d = await clonebotdb.find_one({"bot_id": bot_id}) or {}
    return d.get("start_video")

async def get_start_sticker(bot_id):
    d = await clonebotdb.find_one({"bot_id": bot_id}) or {}
    return d.get("start_sticker")

async def get_start_animation(bot_id):
    d = await clonebotdb.find_one({"bot_id": bot_id}) or {}
    return d.get("start_animation")

async def get_start_reaction(bot_id):
    d = await clonebotdb.find_one({"bot_id": bot_id}) or {}
    return d.get("start_reaction")

async def get_start_effect(bot_id):
    d = await clonebotdb.find_one({"bot_id": bot_id}) or {}
    return d.get("start_effect")

async def get_custom_btn_text(bot_id, key, default_text):
    d = await clonebotdb.find_one({"bot_id": bot_id}) or {}
    val = d.get(f"btn_{key}", default_text)
    return val

async def add_start_content(bot_id, key, value):
    d = await clonebotdb.find_one({"bot_id": bot_id}) or {}
    current = d.get(key)
    
    if current:
        if isinstance(current, dict):
            current = f"{current['text']} - {current['url']}" 
        
        # Avoid duplicates
        if value in current:
            return False 
        final_value = f"{current}|||{value}"
    else:
        final_value = value
        
    await clonebotdb.update_one({"bot_id": bot_id}, {"$set": {key: final_value}}, upsert=True)
    return True

# --- General Helpers ---

def get_random_start_image():
    if START_IMG_URL:
        if isinstance(START_IMG_URL, list):
            return random.choice(START_IMG_URL)
        if isinstance(START_IMG_URL, str) and "|||" in START_IMG_URL:
            return random.choice(START_IMG_URL.split("|||"))
        return START_IMG_URL
    return "https://telegra.ph/file/2e3d368e77c449c287430.jpg"

def format_link(val):
    if not val:
        return "https://t.me/Telegram" 
    if "https://" in val or "http://" in val:
        return val
    return f"https://t.me/{val}"

def get_mention_html(user_id, name):
    return f'<a href="tg://user?id={user_id}">{name}</a>'

async def check_owner(client, message):
    user_id = message.from_user.id
    if user_id in SUDOERS:
        return True
    
    bot_id = client.me.id
    owner_id = await get_owner_id_from_db(bot_id)
    if user_id == owner_id:
        return True
    return False

# =====================================================================
# START COMMAND (PRIVATE)
# =====================================================================

@Client.on_message(filters.command("start") & filters.private & ~BANNED_USERS)
@LanguageStart
async def start_pm(client, message: Message, _):
    a = await client.get_me()
    bot_id = a.id
    await add_served_user_clone(message.from_user.id, bot_id)

    # 1. Loading Animation
    raw_sticker, raw_animation = await asyncio.gather(
        get_start_sticker(bot_id),
        get_start_animation(bot_id)
    )
    
    custom_sticker = random.choice(raw_sticker.split("|||")) if raw_sticker else None
    custom_animation = random.choice(raw_animation.split("|||")) if raw_animation else None
    
    loading = None

    if custom_sticker:
        try:
            loading = await message.reply_sticker(custom_sticker)
            await asyncio.sleep(2)
        except:
            pass
    elif custom_animation:
        try:
            loading = await message.reply_animation(custom_animation)
            await asyncio.sleep(2)
        except:
             pass
    else:
        anim_frames = ["<b>ʟᴏᴀᴅɪɴɢ</b>", "<b>ʟᴏᴀᴅɪɴɢ.</b>", "<b>ʟᴏᴀᴅɪɴɢ..</b>", "<b>ʟᴏᴀᴅɪɴɢ...</b>"]
        try:
            loading = await message.reply_text(anim_frames[0])
            for frame in anim_frames[1:]:
                await asyncio.sleep(0.3)
                try:
                    await loading.edit_text(frame, parse_mode=ParseMode.HTML)
                except:
                    pass
        except:
            pass

    (
        C_BOT_OWNER_ID,
        raw_support,
        raw_channel,
        txt_add,
        txt_support,
        txt_channel,
        txt_owner,
        txt_help,
        raw_custom_btn,
        btn_pos,
        raw_video,
        raw_img,
        raw_caption,
        raw_reaction,
        raw_effect
    ) = await asyncio.gather(
        get_owner_id_from_db(bot_id),
        get_cloned_support_chat(bot_id),
        get_cloned_support_channel(bot_id),
        get_custom_btn_text(bot_id, "add", _["S_B_3"]),
        get_custom_btn_text(bot_id, "support", _["S_B_9"]),
        get_custom_btn_text(bot_id, "channel", _["S_B_6"]),
        get_custom_btn_text(bot_id, "owner", _["C_B_2"]),
        get_custom_btn_text(bot_id, "help", _["S_B_4"]),
        get_start_button(bot_id),
        get_start_btn_pos(bot_id),
        get_start_video(bot_id),
        get_start_image(bot_id),
        get_start_caption(bot_id),
        get_start_reaction(bot_id),
        get_start_effect(bot_id),
    )

    C_SUPPORT_CHAT = format_link(raw_support)
    C_SUPPORT_CHANNEL = format_link(raw_channel)
    OWNER_URL = f"tg://openmessage?user_id={C_BOT_OWNER_ID}"

    await add_served_user(message.from_user.id)
    await message.react("🍓", big=True)
    if len(message.text.split()) > 1:
        name = message.text.split(None, 1)[1]

    try:
        if loading: await loading.delete()
    except:
        pass

    # Inline Arguments Logic
    if len(message.text.split()) > 1:
        arg = message.text.split(None, 1)[1]
        
        if arg.startswith("help"):
            keyboard = InlineKeyboardMarkup([[btn(_["S_B_9"], url=C_SUPPORT_CHAT)]])
            return await message.reply_photo(
                photo=get_random_start_image(),
                caption=_["help_1"].format(C_SUPPORT_CHAT),
                reply_markup=keyboard,
                has_spoiler=True
            )
        if arg.startswith("sud"):
            return await sudoers_list(client=client, message=message, _=_)
        if arg.startswith("inf"):
            m = await message.reply_text("🔎")
            q = arg.replace("info_", "", 1)
            try:
                results = await VideosSearch(f"https://www.youtube.com/watch?v={q}", limit=1).next()
                result = results["result"][0]
                thumbnail = result["thumbnails"][0]["url"].split("?")[0]
                caption = _["start_6"].format(result["title"], result["duration"], result["viewCount"]["short"], result["publishedTime"], result["channel"]["link"], result["channel"]["name"], a.mention)
                key = InlineKeyboardMarkup([[btn(_["S_B_8"], url=result["link"]), btn(_["S_B_9"], url=C_SUPPORT_CHAT)]])
                await m.delete()
                return await message.reply_photo(photo=thumbnail, caption=caption, reply_markup=key, has_spoiler=True)
            except Exception as e:
                LOG.error(e)
                return await m.edit_text("❌ Error fetching info.")

    # Custom Button Data Logic
    custom_button_data = None
    if raw_custom_btn:
        if isinstance(raw_custom_btn, dict):
            custom_button_data = raw_custom_btn
        elif isinstance(raw_custom_btn, str):
            chosen_str = random.choice(raw_custom_btn.split("|||"))
            if "-" in chosen_str:
                txt, url = chosen_str.split("-", 1)
                custom_button_data = {"text": txt.strip(), "url": url.strip()}
    
    markup = make_start_panel(a.username, OWNER_URL,
                              txt_add, txt_support, txt_channel, txt_owner, txt_help,
                              C_SUPPORT_CHAT, C_SUPPORT_CHANNEL,
                              custom_button_data, btn_pos)

    # Media & Caption Logic
    start_video = random.choice(raw_video.split("|||")) if raw_video else None
    start_img = random.choice(raw_img.split("|||")) if raw_img else None
    custom_caption = random.choice(raw_caption.split("|||")) if raw_caption else None
    
    user_mention = get_mention_html(message.from_user.id, message.from_user.first_name)
    bot_mention = get_mention_html(a.id, a.first_name)
    
    if custom_caption:
        try:
            caption = custom_caption.format(
                name=user_mention,
                firstname=message.from_user.first_name,
                botname=bot_mention,
                username=a.username
            )
        except:
            caption = custom_caption
    else:
        caption = (
            f"<blockquote><b>ʜᴇʏ ʙᴀʙʏ</b> {user_mention}, 💫</blockquote>\n"
            f"<blockquote expandable><b>"
            f"๏ ᴛʜɪs ɪs {bot_mention} !\n"
            f"➻ ᴀ ғᴀsᴛ & ᴘᴏᴡᴇʀғᴜʟ ᴛᴇʟᴇɢʀᴀᴍ ᴍᴜsɪᴄ ᴘʟᴀʏᴇʀ 🎧\n"
            f"๏ sᴛʀᴇᴀᴍ ʜɪɢʜ ǫᴜᴀʟɪᴛʏ ᴍᴜsɪᴄ ɪɴ ʏᴏᴜʀ ᴠᴄ ᴡɪᴛʜ ᴇᴀsᴇ.\n"
            f"๏ ɴᴇᴡ ᴠᴇʀsɪᴏɴ ᴡɪᴛʜ sᴜᴘᴇʀ ғᴀsᴛ ʏᴏᴜᴛᴜʙᴇ ᴀᴘɪ ⚡\n"
            f"๏ sᴜᴘᴘᴏʀᴛs ᴘʟᴀʏʟɪsᴛ, ʟɪᴠᴇ sᴛʀᴇᴀᴍ & ᴍᴏʀᴇ.\n\n"
            f"•── ⋅ ⋅ ⋅ ────── ⋅ ⋅ ────── ⋅ ⋅ ⋅ ──•\n\n"
            f"๏ ᴜsᴇ ᴛʜᴇ ʙᴜᴛᴛᴏɴs ʙᴇʟᴏᴡ ᴛᴏ ᴇxᴘʟᴏʀᴇ ғᴇᴀᴛᴜʀᴇs.\n"
            f"๏ ᴄʟɪᴄᴋ ᴏɴ ʜᴇʟᴘ ᴛᴏ ɢᴇᴛ ᴀʟʟ ᴄᴏᴍᴍᴀɴᴅs & ɢᴜɪᴅᴇ.\n\n"
            f"✦ ᴇɴᴊᴏʏ ᴍᴜsɪᴄ ᴡɪᴛʜ ᴘᴏᴡᴇʀ & sᴛʏʟᴇ ✦"
            f"</b></blockquote>"
        )

    # 2. Effect Logic
    if raw_effect:
        effect = random.choice(raw_effect.split("|||"))
    else:
        # Check if config has effect IDs, else use fallback
        try:
            EFFECT_ID = config.EFFECT_ID
        except:
            EFFECT_ID = DEFAULT_EFFECT_IDS
        effect = random.choice(EFFECT_ID)
    
    try:
        effect = int(effect)
    except:
        effect = None

    if start_video:
        try:
            return await message.reply_video(start_video, caption=caption, reply_markup=markup, effect_id=effect, has_spoiler=True, parse_mode=ParseMode.HTML)
        except:
            pass
    
    photo = start_img if start_img else get_random_start_image()
    await message.reply_photo(photo, caption=caption, reply_markup=markup, effect_id=effect, has_spoiler=True, parse_mode=ParseMode.HTML)


# =====================================================================
# START COMMAND (GROUP)
# =====================================================================

@Client.on_message(filters.command("start") & filters.group & ~BANNED_USERS)
@LanguageStart
async def start_gp(client, message: Message, _):
    a = await client.get_me()
    bot_id = a.id
    uptime = get_readable_time(int(time.time() - _boot_))
    
    raw_support, txt_add, txt_support, raw_video, raw_img = await asyncio.gather(
        get_cloned_support_chat(a.id),
        get_custom_btn_text(a.id, "add", _["S_B_1"]),
        get_custom_btn_text(a.id, "support", _["S_B_2"]),
        get_start_video(bot_id),
        get_start_image(bot_id)
    )

    C_SUPPORT_CHAT = format_link(raw_support)
    markup = make_gp_panel(a.username, txt_add, txt_support, C_SUPPORT_CHAT)
    caption = _["start_1"].format(a.mention, uptime)
    
    start_video = random.choice(raw_video.split("|||")) if raw_video else None
    start_img = random.choice(raw_img.split("|||")) if raw_img else None
    
    if start_video:
        try:
            return await message.reply_video(start_video, caption=caption, reply_markup=markup, has_spoiler=True)
        except:
            pass
    
    photo = start_img if start_img else get_random_start_image()
    try:
        await message.reply_photo(photo, caption=caption, reply_markup=markup, has_spoiler=True)
    except Exception:
        try:
            await message.reply_text(caption, reply_markup=markup, disable_web_page_preview=True)
        except Exception:
            pass
    await add_served_chat_clone(message.chat.id, a.id)


# =====================================================================
# CALLBACKS
# =====================================================================

@Client.on_callback_query(filters.regex("settingsback_home") & ~BANNED_USERS)
@languageCB
async def home_back_handler(client, CallbackQuery, _):
    a = await client.get_me()
    bot_id = a.id

    (
        C_BOT_OWNER_ID,
        raw_support,
        raw_channel,
        txt_add,
        txt_support,
        txt_channel,
        txt_owner,
        txt_help,
        raw_custom_btn,
        btn_pos,
        raw_video,
        raw_img,
        raw_caption,
        raw_effect
    ) = await asyncio.gather(
        get_owner_id_from_db(bot_id),
        get_cloned_support_chat(bot_id),
        get_cloned_support_channel(bot_id),
        get_custom_btn_text(bot_id, "add", _["S_B_3"]),
        get_custom_btn_text(bot_id, "support", _["S_B_9"]),
        get_custom_btn_text(bot_id, "channel", _["S_B_6"]),
        get_custom_btn_text(bot_id, "owner", _["C_B_2"]),
        get_custom_btn_text(bot_id, "help", _["S_B_4"]),
        get_start_button(bot_id),
        get_start_btn_pos(bot_id),
        get_start_video(bot_id),
        get_start_image(bot_id),
        get_start_caption(bot_id),
        get_start_effect(bot_id),
    )

    C_SUPPORT_CHAT = format_link(raw_support)
    C_SUPPORT_CHANNEL = format_link(raw_channel)
    OWNER_URL = f"tg://openmessage?user_id={C_BOT_OWNER_ID}"

    custom_button_data = None
    if raw_custom_btn:
        if isinstance(raw_custom_btn, dict):
            custom_button_data = raw_custom_btn
        elif isinstance(raw_custom_btn, str):
            chosen_str = random.choice(raw_custom_btn.split("|||"))
            if "-" in chosen_str:
                txt, url = chosen_str.split("-", 1)
                custom_button_data = {"text": txt.strip(), "url": url.strip()}
    
    markup = make_start_panel(a.username, OWNER_URL,
                              txt_add, txt_support, txt_channel, txt_owner, txt_help,
                              C_SUPPORT_CHAT, C_SUPPORT_CHANNEL,
                              custom_button_data, btn_pos)

    start_video = random.choice(raw_video.split("|||")) if raw_video else None
    start_img = random.choice(raw_img.split("|||")) if raw_img else None
    custom_caption = random.choice(raw_caption.split("|||")) if raw_caption else None
    
    user_mention = get_mention_html(CallbackQuery.from_user.id, CallbackQuery.from_user.first_name)
    bot_mention = get_mention_html(a.id, a.first_name)
    
    if custom_caption:
        try:
            caption = custom_caption.format(name=user_mention, firstname=CallbackQuery.from_user.first_name, botname=bot_mention, username=a.username)
        except:
            caption = custom_caption
    else:
        caption = (
            f"<blockquote><b>ʜᴇʏ ʙᴀʙʏ</b> {user_mention}, 💫</blockquote>\n"
            f"<blockquote expandable><b>"
            f"๏ ᴛʜɪs ɪs {bot_mention} !\n"
            f"➻ ᴀ ғᴀsᴛ & ᴘᴏᴡᴇʀғᴜʟ ᴛᴇʟᴇɢʀᴀᴍ ᴍᴜsɪᴄ ᴘʟᴀʏᴇʀ 🎧\n"
            f"๏ sᴛʀᴇᴀᴍ ʜɪɢʜ ǫᴜᴀʟɪᴛʏ ᴍᴜsɪᴄ ɪɴ ʏᴏᴜʀ ᴠᴄ ᴡɪᴛʜ ᴇᴀsᴇ.\n"
            f"๏ ɴᴇᴡ ᴠᴇʀsɪᴏɴ ᴡɪᴛʜ sᴜᴘᴇʀ ғᴀsᴛ ʏᴏᴜᴛᴜʙᴇ ᴀᴘɪ ⚡\n"
            f"๏ sᴜᴘᴘᴏʀᴛs ᴘʟᴀʏʟɪsᴛ, ʟɪᴠᴇ sᴛʀᴇᴀᴍ & ᴍᴏʀᴇ.\n\n"
            f"•── ⋅ ⋅ ⋅ ────── ⋅ ⋅ ────── ⋅ ⋅ ⋅ ──•\n\n"
            f"๏ ᴜsᴇ ᴛʜᴇ ʙᴜᴛᴛᴏɴs ʙᴇʟᴏᴡ ᴛᴏ ᴇxᴘʟᴏʀᴇ ғᴇᴀᴛᴜʀᴇs.\n"
            f"๏ ᴄʟɪᴄᴋ ᴏɴ ʜᴇʟᴘ ᴛᴏ ɢᴇᴛ ᴀʟʟ ᴄᴏᴍᴍᴀɴᴅs & ɢᴜɪᴅᴇ.\n\n"
            f"✦ ᴇɴᴊᴏʏ ᴍᴜsɪᴄ ᴡɪᴛʜ ᴘᴏᴡᴇʀ & sᴛʏʟᴇ ✦"
            f"</b></blockquote>"
        )

    if raw_effect:
        effect = random.choice(raw_effect.split("|||"))
    else:
        try:
            EFFECT_ID = config.EFFECT_ID
        except:
            EFFECT_ID = DEFAULT_EFFECT_IDS
        effect = random.choice(EFFECT_ID)
    
    try:
        effect = int(effect)
    except:
        effect = None

    try:
        if start_video:
            await CallbackQuery.edit_message_media(media=InputMediaVideo(media=start_video, caption=caption), reply_markup=markup)
        else:
            photo = start_img if start_img else get_random_start_image()
            await CallbackQuery.edit_message_media(media=InputMediaPhoto(media=photo, caption=caption), reply_markup=markup)
    except Exception as e:
        try:
            await CallbackQuery.message.delete()
        except:
            pass
        if start_video:
            await CallbackQuery.message.reply_video(start_video, caption=caption, reply_markup=markup, effect_id=effect, has_spoiler=True, parse_mode=ParseMode.HTML)
        else:
            photo = start_img if start_img else get_random_start_image()
            await CallbackQuery.message.reply_photo(photo, caption=caption, reply_markup=markup, effect_id=effect, has_spoiler=True, parse_mode=ParseMode.HTML)


# =====================================================================
# SETTINGS & MANAGEMENT (Secure)
# =====================================================================

@Client.on_message(filters.command(["transfer", "transferowner"]) & ~BANNED_USERS)
async def transfer_owner(client, message):
    if not await check_owner(client, message):
         return await message.reply_text("❌ **Only Bot Owner can use this.**")

    bot_id = (await client.get_me()).id
    user = message.from_user

    new_owner = None
    if message.reply_to_message:
        new_owner = message.reply_to_message.from_user
    elif len(message.command) > 1:
        try:
            new_owner = await client.get_users(message.command[1])
        except:
            return await message.reply_text("❌ User not found!")
    else:
        return await message.reply_text("❌ Reply to a user or type `/transfer @username`.")

    if new_owner.is_bot:
        return await message.reply_text("❌ Bot cannot be owner.")
    if new_owner.id == user.id:
        return await message.reply_text("❌ You are already the owner.")

    await clonebotdb.update_one({"bot_id": bot_id}, {"$set": {"user_id": new_owner.id}})
    await cloneownerdb.update_one({"bot_id": bot_id}, {"$set": {"user_id": new_owner.id}}, upsert=True)

    await message.reply_text(f"✅ **Ownership Transferred!**\n👑 New Owner: {new_owner.mention}")


@Client.on_message(filters.command("viewstartsettings") & ~BANNED_USERS)
async def view_start_settings(client, message):
    if not await check_owner(client, message): return
    bot_id = (await client.get_me()).id
    pos = await get_start_btn_pos(bot_id)
    await message.reply_text(f"⚙️ **Settings Viewed**\nButton Position: `{pos}`")


@Client.on_message(filters.command("resetstartsetting") & ~BANNED_USERS)
async def reset_start_settings(client, message):
    if not await check_owner(client, message): return
    bot_id = (await client.get_me()).id
    await clonebotdb.update_one({"bot_id": bot_id}, {"$unset": {
        "start_image": "", "start_video": "", "start_sticker": "", 
        "start_animation": "", "start_caption": "", "start_button": "", 
        "start_btn_pos": "", "start_reaction": "", "start_effect": ""
    }})
    await message.reply_text("🔄 All Start Settings Reset!")


@Client.on_message(filters.command(["setstartreaction", "addstartreaction"]) & ~BANNED_USERS)
async def set_start_reaction_cmd(client, message):
    if not await check_owner(client, message): return
    if not await is_premium((await client.get_me()).id):
        return await message.reply_text("💎 ᴛʜɪs ғᴇᴀᴛᴜʀᴇ ɪs ғᴏʀ ᴘʀᴇᴍɪᴜᴍ ʙᴏᴛs ᴏɴʟʏ.")
    bot_id = (await client.get_me()).id
    if len(message.command) < 2:
        return await message.reply_text("❌ **Usage:** `/setstartreaction 🔥`")
    
    emoji = message.command[1]
    await add_start_content(bot_id, "start_reaction", emoji)
    await message.reply_text(f"✅ Added: {emoji}")


@Client.on_message(filters.command(["delstartreaction", "resetstartreaction"]) & ~BANNED_USERS)
async def del_start_reaction_cmd(client, message):
    if not await check_owner(client, message): return
    if not await is_premium((await client.get_me()).id):
        return await message.reply_text("💎 ᴛʜɪs ғᴇᴀᴛᴜʀᴇ ɪs ғᴏʀ ᴘʀᴇᴍɪᴜᴍ ʙᴏᴛs ᴏɴʟʏ.")
    bot_id = (await client.get_me()).id
    await clonebotdb.update_one({"bot_id": bot_id}, {"$unset": {"start_reaction": ""}})
    await message.reply_text("✅ Start Reaction Reset!")


@Client.on_message(filters.command(["setstarteffect", "addstarteffect"]) & ~BANNED_USERS)
async def set_start_effect_cmd(client, message):
    if not await check_owner(client, message): return
    if not await is_premium((await client.get_me()).id):
        return await message.reply_text("💎 ᴛʜɪs ғᴇᴀᴛᴜʀᴇ ɪs ғᴏʀ ᴘʀᴇᴍɪᴜᴍ ʙᴏᴛs ᴏɴʟʏ.")
    bot_id = (await client.get_me()).id
    if len(message.command) < 2:
        return await message.reply_text("❌ **Usage:** `/setstarteffect 🔥`\nSupported: 🔥, 👍, 👎, ❤️, 🎉, 💩")
    
    EFFECT_MAP = {
        "🔥": "5104841245755180586",
        "👍": "5107584321108051014",
        "👎": "5104858069142078462",
        "❤️": "5044134455711629726",
        "🎉": "5046509860389126442",
        "💩": "5046589136895476101"
    }
    
    arg = message.command[1]
    effect_id = EFFECT_MAP.get(arg, arg) 
    await add_start_content(bot_id, "start_effect", effect_id)
    await message.reply_text(f"✅ Start Effect Added!")


@Client.on_message(filters.command(["delstarteffect", "resetstarteffect"]) & ~BANNED_USERS)
async def del_start_effect_cmd(client, message):
    if not await check_owner(client, message): return
    if not await is_premium((await client.get_me()).id):
        return await message.reply_text("💎 ᴛʜɪs ғᴇᴀᴛᴜʀᴇ ɪs ғᴏʀ ᴘʀᴇᴍɪᴜᴍ ʙᴏᴛs ᴏɴʟʏ.")
    bot_id = (await client.get_me()).id
    await clonebotdb.update_one({"bot_id": bot_id}, {"$unset": {"start_effect": ""}})
    await message.reply_text("✅ Start Effect Reset!")


@Client.on_message(filters.command(["setstartimg", "addstartimg"]) & ~BANNED_USERS)
async def set_start_image_cmd(client, message):
    if not await check_owner(client, message): return
    if not await is_premium((await client.get_me()).id):
        return await message.reply_text("💎 ᴛʜɪs ғᴇᴀᴛᴜʀᴇ ɪs ғᴏʀ ᴘʀᴇᴍɪᴜᴍ ʙᴏᴛs ᴏɴʟʏ.")
    bot_id = (await client.get_me()).id
    if message.reply_to_message and message.reply_to_message.photo:
        await add_start_content(bot_id, "start_image", message.reply_to_message.photo.file_id)
        await message.reply_text("✅ Image Added!")
    else:
        await message.reply_text("Reply to a photo.")

@Client.on_message(filters.command(["delstartimg", "resetstartimg"]) & ~BANNED_USERS)
async def del_start_image_cmd(client, message):
    if not await check_owner(client, message): return
    if not await is_premium((await client.get_me()).id):
        return await message.reply_text("💎 ᴛʜɪs ғᴇᴀᴛᴜʀᴇ ɪs ғᴏʀ ᴘʀᴇᴍɪᴜᴍ ʙᴏᴛs ᴏɴʟʏ.")
    bot_id = (await client.get_me()).id
    await clonebotdb.update_one({"bot_id": bot_id}, {"$unset": {"start_image": ""}})
    await message.reply_text("✅ Images Reset!")


@Client.on_message(filters.command(["setstartvideo", "addstartvideo"]) & ~BANNED_USERS)
async def set_start_video_cmd(client, message):
    if not await check_owner(client, message): return
    if not await is_premium((await client.get_me()).id):
        return await message.reply_text("💎 ᴛʜɪs ғᴇᴀᴛᴜʀᴇ ɪs ғᴏʀ ᴘʀᴇᴍɪᴜᴍ ʙᴏᴛs ᴏɴʟʏ.")
    bot_id = (await client.get_me()).id
    if message.reply_to_message and message.reply_to_message.video:
        await add_start_content(bot_id, "start_video", message.reply_to_message.video.file_id)
        await message.reply_text("✅ Video Added!")
    else:
        await message.reply_text("Reply to a video.")

@Client.on_message(filters.command(["delstartvideo", "resetstartvideo"]) & ~BANNED_USERS)
async def del_start_video_cmd(client, message):
    if not await check_owner(client, message): return
    if not await is_premium((await client.get_me()).id):
        return await message.reply_text("💎 ᴛʜɪs ғᴇᴀᴛᴜʀᴇ ɪs ғᴏʀ ᴘʀᴇᴍɪᴜᴍ ʙᴏᴛs ᴏɴʟʏ.")
    bot_id = (await client.get_me()).id
    await clonebotdb.update_one({"bot_id": bot_id}, {"$unset": {"start_video": ""}})
    await message.reply_text("✅ Videos Reset!")


@Client.on_message(filters.command(["setstartsticker", "addstartsticker"]) & ~BANNED_USERS)
async def set_start_sticker_cmd(client, message):
    if not await check_owner(client, message): return
    if not await is_premium((await client.get_me()).id):
        return await message.reply_text("💎 ᴛʜɪs ғᴇᴀᴛᴜʀᴇ ɪs ғᴏʀ ᴘʀᴇᴍɪᴜᴍ ʙᴏᴛs ᴏɴʟʏ.")
    bot_id = (await client.get_me()).id
    if message.reply_to_message and message.reply_to_message.sticker:
        await add_start_content(bot_id, "start_sticker", message.reply_to_message.sticker.file_id)
        await message.reply_text("✅ Sticker Added!")
    else:
        await message.reply_text("Reply to a sticker.")

@Client.on_message(filters.command(["delstartsticker", "resetstartsticker"]) & ~BANNED_USERS)
async def del_start_sticker_cmd(client, message):
    if not await check_owner(client, message): return
    if not await is_premium((await client.get_me()).id):
        return await message.reply_text("💎 ᴛʜɪs ғᴇᴀᴛᴜʀᴇ ɪs ғᴏʀ ᴘʀᴇᴍɪᴜᴍ ʙᴏᴛs ᴏɴʟʏ.")
    bot_id = (await client.get_me()).id
    await clonebotdb.update_one({"bot_id": bot_id}, {"$unset": {"start_sticker": ""}})
    await message.reply_text("✅ Stickers Reset!")


@Client.on_message(filters.command(["setstartanimation", "addstartanimation"]) & ~BANNED_USERS)
async def set_start_animation_cmd(client, message):
    if not await check_owner(client, message): return
    if not await is_premium((await client.get_me()).id):
        return await message.reply_text("💎 ᴛʜɪs ғᴇᴀᴛᴜʀᴇ ɪs ғᴏʀ ᴘʀᴇᴍɪᴜᴍ ʙᴏᴛs ᴏɴʟʏ.")
    bot_id = (await client.get_me()).id
    if message.reply_to_message and message.reply_to_message.animation:
        await add_start_content(bot_id, "start_animation", message.reply_to_message.animation.file_id)
        await message.reply_text("✅ Animation Added!")
    else:
        await message.reply_text("Reply to a GIF.")

@Client.on_message(filters.command(["delstartanimation", "resetstartanimation"]) & ~BANNED_USERS)
async def del_start_animation_cmd(client, message):
    if not await check_owner(client, message): return
    if not await is_premium((await client.get_me()).id):
        return await message.reply_text("💎 ᴛʜɪs ғᴇᴀᴛᴜʀᴇ ɪs ғᴏʀ ᴘʀᴇᴍɪᴜᴍ ʙᴏᴛs ᴏɴʟʏ.")
    bot_id = (await client.get_me()).id
    await clonebotdb.update_one({"bot_id": bot_id}, {"$unset": {"start_animation": ""}})
    await message.reply_text("✅ Animations Reset!")


@Client.on_message(filters.command(["setstartcaption", "addstartcaption"]) & ~BANNED_USERS)
async def set_start_caption_cmd(client, message):
    if not await check_owner(client, message): return
    if not await is_premium((await client.get_me()).id):
        return await message.reply_text("💎 ᴛʜɪs ғᴇᴀᴛᴜʀᴇ ɪs ғᴏʀ ᴘʀᴇᴍɪᴜᴍ ʙᴏᴛs ᴏɴʟʏ.")
    bot_id = (await client.get_me()).id
    if message.reply_to_message:
        text = message.reply_to_message.text.html if message.reply_to_message.text else message.reply_to_message.caption.html
        await add_start_content(bot_id, "start_caption", text)
        await message.reply_text("✅ Caption Added!")
    else:
        await message.reply_text("Reply to a text.")

@Client.on_message(filters.command(["delstartcaption", "resetstartcaption"]) & ~BANNED_USERS)
async def del_start_caption_cmd(client, message):
    if not await check_owner(client, message): return
    if not await is_premium((await client.get_me()).id):
        return await message.reply_text("💎 ᴛʜɪs ғᴇᴀᴛᴜʀᴇ ɪs ғᴏʀ ᴘʀᴇᴍɪᴜᴍ ʙᴏᴛs ᴏɴʟʏ.")
    bot_id = (await client.get_me()).id
    await clonebotdb.update_one({"bot_id": bot_id}, {"$unset": {"start_caption": ""}})
    await message.reply_text("✅ Captions Reset!")


@Client.on_message(filters.command(["setstartbutton", "addstartbutton"]) & ~BANNED_USERS)
async def set_start_button_cmd(client, message):
    if not await check_owner(client, message): return
    if not await is_premium((await client.get_me()).id):
        return await message.reply_text("💎 ᴛʜɪs ғᴇᴀᴛᴜʀᴇ ɪs ғᴏʀ ᴘʀᴇᴍɪᴜᴍ ʙᴏᴛs ᴏɴʟʏ.")
    bot_id = (await client.get_me()).id
    data = message.text.split(None, 1)[1] if len(message.command) > 1 else None
    
    if not data or "-" not in data: 
        return await message.reply_text("Format: `/addstartbutton Text - URL`")
    
    txt, url = data.split("-", 1)
    btn_str = f"{txt.strip()} - {url.strip()}"
    
    await add_start_content(bot_id, "start_button", btn_str)
    await message.reply_text("✅ Button Added!")

@Client.on_message(filters.command(["delstartbutton", "resetstartbutton"]) & ~BANNED_USERS)
async def del_start_button_cmd(client, message):
    if not await check_owner(client, message): return
    if not await is_premium((await client.get_me()).id):
        return await message.reply_text("💎 ᴛʜɪs ғᴇᴀᴛᴜʀᴇ ɪs ғᴏʀ ᴘʀᴇᴍɪᴜᴍ ʙᴏᴛs ᴏɴʟʏ.")
    bot_id = (await client.get_me()).id
    await clonebotdb.update_one({"bot_id": bot_id}, {"$unset": {"start_button": ""}})
    await message.reply_text("✅ Buttons Reset!")


@Client.on_message(filters.command("setbtnpos") & ~BANNED_USERS)
async def set_btn_pos_cmd(client, message):
    if not await is_premium((await client.get_me()).id):
        return await message.reply_text("💎 ᴛʜɪs ғᴇᴀᴛᴜʀᴇ ɪs ғᴏʀ ᴘʀᴇᴍɪᴜᴍ ʙᴏᴛs ᴏɴʟʏ.")
    if not await check_owner(client, message): return
    bot_id = (await client.get_me()).id
    if len(message.command) < 2:
        return await message.reply_text("Usage: `/setbtnpos [UP/DOWN/MID]`")
    
    raw_pos = message.command[1].upper()
    valid_pos = ["UP", "TOP", "DOWN", "BOTTOM", "MID", "MIDDLE"]
    
    if raw_pos in valid_pos:
        if raw_pos == "TOP": raw_pos = "UP"
        if raw_pos == "BOTTOM": raw_pos = "DOWN"
        if raw_pos == "MIDDLE": raw_pos = "MID"
        
        await clonebotdb.update_one({"bot_id": bot_id}, {"$set": {"start_btn_pos": raw_pos}}, upsert=True)
        await message.reply_text(f"✅ Position Set: **{raw_pos}**")
    else:
        await message.reply_text("❌ Invalid! Use: UP, DOWN, MID")


@Client.on_callback_query(filters.regex("^bot_info_data$"))
async def show_bot_info(client, query):
    start = time.time()
    x = await client.send_message(query.message.chat.id, "ᴘɪɴɢ ᴘᴏɴɢ 💕..")
    delta_ping = time.time() - start
    await x.delete()
    txt = f"""💌 ᴘɪɴɢ ᴘᴏɴɢ ʙᴀʙʏ...

• ᴅᴀᴛᴀʙᴀsᴇ: ᴏɴʟɪɴᴇ
• ʏᴏᴜᴛᴜʙᴇ ᴀᴘɪ: ʀᴇsᴘᴏɴsɪᴠᴇ
• ʙᴏᴛ sᴇʀᴠᴇʀ: ʀᴜɴɴɪɴɢ sᴍᴏᴏᴛʜʟʏ
• ʀᴇsᴘᴏɴsᴇ ᴛɪᴍᴇ: ᴏᴘᴛɪᴍᴀʟ
• ᴀᴘɪ ᴘɪɴɢ: {delta_ping * 1000:.3f} ms   

• ᴇᴠᴇʀʏᴛʜɪɴɢ ʟᴏᴏᴋs ɢᴏᴏᴅ!
"""
    await query.answer(txt, show_alert=True)
