#!/usr/bin/env python3

from websockets import connect as websockets_connect

from json import loads as json_loads, dumps as json_dumps
from asyncio import (
    gather as asyncio_gather,
    run as asyncio_run,
    to_thread as asyncio_to_thread
)
from readline import read_history_file, write_history_file
from os import getenv

HISTORY_FILE = ".rcon_history"
try:
    read_history_file(HISTORY_FILE)
except FileNotFoundError:
    pass


def get_rcon():
    return websockets_connect(
        f"ws://{getenv("SERVER_CONTAINER_NAME")}:28016/ZxAKvf4zh7U3P1Pxxv70qjsRhHA3TK",
        ping_timeout=None
    )

async def send_message(rcon, message):
    return await rcon.send(json_dumps({
        "Identifier": -1,
        "Message": message,
        "Name": "WebRcon"
    }))

async def read_message(rcon):
    raw = await rcon.recv()
    return json_loads(raw).get("Message")


async def main():
    async with get_rcon() as rcon:
        async def send_input(rcon):
            while True:
                message = await asyncio_to_thread(input, '> ')
                await send_message(rcon, message)
        
        async def listen(rcon):
            while True:
                message = await read_message(rcon)
                print(f'\r{message}\n> ', end="", flush=True)
        
        await asyncio_gather(
            send_input(rcon),
            listen(rcon)
        )

if __name__ == "__main__":
    try:
        asyncio_run(main())
    finally:
        write_history_file(HISTORY_FILE)
