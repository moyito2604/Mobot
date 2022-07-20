#This is an asynchronous threaded timer used to run Mobot
#It generates one instance of a timer per server that it is used in
#It is then used to periodically check if the next song in queue is ready to play

import asyncio
from contextlib import suppress

#Modified for use with Mobot

class RepeatedTimer:
    def __init__(self, time, func, *args, **kwargs):
        self.func = func
        self.time = time
        self.args = args
        self.kwargs = kwargs
        self.is_started = False
        self._task = None

#Function is called to start and run the timer
    async def _run(self):
        while self.is_started:
            await asyncio.sleep(self.time)
            await self.func(*self.args, **self.kwargs)
    
    async def pause(self):
        #ends the current task without cancelling it
        if self.is_started:
            self.is_started = False

    async def start(self):
        if not self.is_started:
            self.is_started = True
            # Start task to call func periodically:
            self._task = asyncio.ensure_future(self._run())

    async def stop(self):
        if self.is_started:
            self.is_started = False
            # Stop task and await it stopped:
            self._task.cancel()
            with suppress(asyncio.CancelledError):
                await self._task

#Synchronous timer class
#from threading import Timer

#class RepeatedTimer(object):
    #def __init__(self, interval, function, *args, **kwargs):
        #self._timer     = None
        #self.interval   = interval
        #self.function   = function
        #self.args       = args
        #self.kwargs     = kwargs
        #self.is_running = False
        #self.start()

    #def _run(self):
        #self.is_running = False
        #self.start()
        #self.function(*self.args, **self.kwargs)

    #def start(self):
        #if not self.is_running:
            #self._timer = Timer(self.interval, self._run)
            #self._timer.start()
            #self.is_running = True

    #def stop(self):
        #self._timer.cancel()
        #self.is_running = False
