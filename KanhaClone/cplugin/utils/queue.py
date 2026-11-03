#
# Copyright (C) 2026 by Kanha-Team@Github, < https://github.com/Kanha-Team>.
# This file is part of < https://github.com/Kanha-Team/KanhaClone > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/Kanha-Team/KanhaClone/blob/main/LICENSE >
#
# All rights reserved.
#

from KanhaClone.misc import db


async def put(
    chat_id,
    title,
    duration,
    videoid,
    file_path,
    ruser,
    user_id,
    streamtype="audio",  # Default audio rakha hai, video ke liye change hoga
):
    put_f = {
        "title": title,
        "dur": duration,       # skip.py mein ["dur"] use hota hai
        "file": file_path,     # skip.py mein ["file"] use hota hai
        "vidid": videoid,      # skip.py mein ["vidid"] use hota hai
        "by": ruser,           # skip.py mein ["by"] use hota hai
        "user_id": user_id,
        "streamtype": streamtype, # Important for video/audio check
        "played": 0,           # Seek bar ke liye zaroori hai
        "seconds": 0,          # Duration calculation ke liye
    }
    
    get = db.get(chat_id)
    if get:
        db[chat_id].append(put_f)
    else:
        db[chat_id] = []
        db[chat_id].append(put_f)
