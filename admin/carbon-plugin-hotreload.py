#!/usr/bin/env python3

from pathlib import Path
from os import getenv as os_getenv
from collections import defaultdict
from rcon import get_rcon, send_message, asyncio_run
from inotify_simple import INotify, flags
import time

async def main():
    if not (PLUGINS_FOLDER := Path(os_getenv("PLUGINS_FOLDER")).resolve()):
        raise Exception("PLUGINS_FOLDER env var is not set")

    inotify = INotify()
    inotify.add_watch(PLUGINS_FOLDER, flags.MODIFY)

    last_handled = defaultdict(lambda: 0)
    debounce_time = 0.5  # seconds

    async with get_rcon() as rcon:
        while True:
            for event in inotify.read():
                now = time.time()
                if now - last_handled[event.name] < debounce_time:
                    continue
                last_handled[event.name] = now

                command = f'c.load {event.name.replace(".cs", "")}'
                await send_message(rcon, command)
                if __debug__:
                    print(f"Reloaded {event.name}")

if __name__ == "__main__":
    asyncio_run(main())
