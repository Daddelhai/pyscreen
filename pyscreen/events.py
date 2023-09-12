import asyncio
import json

import aiohttp
import pygame

from pyscreen.eventHandler import EventHandler

from pyscreen.logging import getLogger
logger = getLogger()

def load_events(eventHandler: EventHandler, url):
    async def get(path):
        TIMEOUT = aiohttp.ClientTimeout(total=2,sock_connect=1,sock_read=1)
        try:
            async with aiohttp.ClientSession(timeout=TIMEOUT) as session:
                async with session.get(f"{url}{path}", timeout=1) as response:
                    return asyncio.ensure_future(json.loads(await response.text()))
        except asyncio.exceptions.TimeoutError as e:
            logger.warn("Error while getting data from server: Connection timed out")
        except Exception:
            logger.warn("Error while getting data from server")
            pass

    async def setSimRate(e):
        if e.key == pygame.K_0:
            sr = 0
        elif e.key == pygame.K_1:
            sr = 1
        elif e.key == pygame.K_2:
            sr = 2
        elif e.key == pygame.K_3:
            sr = 4
        elif e.key == pygame.K_4:
            sr = 8
        elif e.key == pygame.K_5:
            sr = 12
        elif e.key == pygame.K_6:
            sr = 16
        elif e.key == pygame.K_7:
            sr = 20
        elif e.key == pygame.K_8:
            sr = 26
        elif e.key == pygame.K_9:
            sr = 32
        else:
            return

        await get(f"/setsimrate/{sr}")

    eventHandler.addEventListener("keyDown", setSimRate)

    def dragdrop_test(event):
        logger.debug(event.file)

    eventHandler.addEventListener("fileDrop", dragdrop_test)