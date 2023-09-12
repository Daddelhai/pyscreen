import asyncio
from threading import Lock, get_ident

class AsyncRLock:
    def __init__(self):
        self.__lock = Lock()
        self.__lockCount = 0
        self.__lockThread = None
        self.__asyncEventLock = Lock()
        self.__asyncEvent: dict[int,asyncio.Event] = {}

    def __aquire(self):
        self.__lock.acquire()
        self.__lockThread = get_ident()
        self.__lockCount = 1

    def __release(self):
        self.__lockCount = 0
        self.__lockThread = None
        self.__lock.release()

        # release one waiting event
        if len(self.__asyncEvent) == 0:
            return
        
        with self.__asyncEventLock:
            key = next(iter(self.__asyncEvent))
            self.__asyncEvent[key].set()
            del self.__asyncEvent[key]

    def acquire(self):
        if self.__lock.locked():
            if self.__lockThread == get_ident():
                self.__lockCount += 1
                return
            else:
                self.__aquire()
                return
        else:
            self.__aquire()
            return
        
    def release(self):
        if self.__lockThread == get_ident():
            self.__lockCount -= 1
            if self.__lockCount == 0:
                self.__release()
                return
            else:
                return
        else:
            raise RuntimeError("Attempt to release lock from wrong thread")
        
    def locked(self):
        return self.__lock.locked()
    
    def lockedForCurrentThread(self):
        if not self.locked():
            return False
        return self.__lockThread != get_ident()
    
    def __enter__(self):
        self.acquire()
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.release()
        return False
    
    async def wait(self):
        if not self.lockedForCurrentThread():
            return # No need to wait
        
        if get_ident() not in self.__asyncEvent:
            with self.__asyncEventLock:
                self.__asyncEvent[get_ident()] = asyncio.Event()
            
        return await self.__asyncEvent[get_ident()].wait()

    async def __aenter__(self):
        await self.wait()
        self.acquire()

    async def __aexit__(self, exc_type, exc_value, traceback):
        self.release()
        return False