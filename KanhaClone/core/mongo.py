#
# Copyright (C) 2026 by Kanha-Team@Github, < https://github.com/Kanha-Team>.
# This file is part of < https://github.com/Kanha-Team/KanhaClone > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/Kanha-Team/KanhaClone/blob/main/LICENSE >
#
# All rights reserved.
#

from motor.motor_asyncio import AsyncIOMotorClient as _mongo_client_
from pymongo import MongoClient

import config

from ..logging import LOGGER

# A missing URI used to fall back to a hard-coded empty string, which made every
# database call fail later with an unrelated-looking timeout. Fail fast instead.
if not config.MONGO_DB_URI:
    raise SystemExit(
        "[ERROR] - MONGO_DB_URI is missing. Set it in your .env file "
        "(MongoDB Atlas free tier works). The variable used to be called "
        "MONGO_URI in some guides; both names are accepted now."
    )

_mongo_async_ = _mongo_client_(
    config.MONGO_DB_URI,
    serverSelectionTimeoutMS=15000,
    tz_aware=True,
)
_mongo_sync_ = MongoClient(config.MONGO_DB_URI, serverSelectionTimeoutMS=15000)

mongodb = _mongo_async_.Kanha
pymongodb = _mongo_sync_.Kanha
