#!/usr/bin/env python3

from rcon import get_rcon, send_message, asyncio_run

async def restart(delay_in_seconds: str = ''):
    async with get_rcon() as rcon:
        await send_message(rcon, f'restart {delay_in_seconds or 0}')

if __name__ == "__main__":
    from argparse import ArgumentParser
    
    parser = ArgumentParser()
    parser.add_argument("delay_in_seconds", nargs="?", type=int, default=0)
    args = parser.parse_args()

    asyncio_run(restart(args.delay_in_seconds))
