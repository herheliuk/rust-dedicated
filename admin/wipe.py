#!/usr/bin/env python3

import shutil

from restart import restart, asyncio_run
from pathlib import Path

SERVER_SEED_FILE = Path("/home/user/server/server.seed")
BACKUPS_FOLDER = Path("/home/user/server_data_backups")

def delete_backups_folder():
    for item in BACKUPS_FOLDER.iterdir():
        if item.is_symlink() or item.is_file():
            item.unlink()
        elif item.is_dir():
            shutil.rmtree(item)

async def wipe(delay_in_seconds: str = ''):
    SERVER_SEED_FILE.unlink(missing_ok=True)
    delete_backups_folder()
    await restart(delay_in_seconds)

if __name__ == "__main__":
    from argparse import ArgumentParser
    
    parser = ArgumentParser()
    parser.add_argument("delay_in_seconds", nargs="?", type=int, default=0)
    args = parser.parse_args()

    asyncio_run(wipe(args.delay_in_seconds))
