import datetime
import threading
import time

import numpy
from numpy import append


class FPSCalculator:
    def __init__(self, history_len = 100):
        self._history = numpy.array([0])
        self._history_len = history_len
        self._last_time = datetime.datetime.now()

    def __call__(self):
        new_time = datetime.datetime.now()
        try:
            self._history = append(self._history, 1 / ( new_time - self._last_time ).total_seconds() )
        except ZeroDivisionError:
            return

        if self._history.size > self._history_len:
            self._history.pop(0)

        self._last_time = new_time

    def avg(self):
        if self._history.size <= 2:
            return 0
        return numpy.average(self._history)

    def max(self):
        if self._history.size <= 2:
            return 0
        return numpy.max(self._history)

    def min(self):
        if self._history.size <= 2:
            return 0
        return numpy.min(self._history)

    def __str__(self):
        if self._history.size <= 2:
            return "< 1"
        return str(int(self._history[-1]))


class ThreadingFPSCalculator(FPSCalculator):
    def __init__(self, history_len = 1000):
        super().__init__(history_len)

        self.__calc_thread = threading.Thread(target=self._calc_fps, daemon=True, name="FPSCalculator")
        self.__calc_thread.start()
        self._avg = 0
        self._max = 0
        self._min = 0

    def avg(self):
        return self._avg

    def max(self):
        return self._max

    def min(self):
        return self._min

    def _calc_fps(self):
        while 1:
            try:
                self._avg = super().avg()
                self._max = super().max()
                self._min = super().min()
                if self._history.size > 2:
                    self._history = numpy.array(self._history[-1])
            except Exception:
                pass
            time.sleep(2)
            

