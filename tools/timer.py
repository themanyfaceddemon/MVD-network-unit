import logging
import threading
import time
from typing import Callable, Dict

logger = logging.getLogger(__name__)


class Timer:
    def __init__(
        self,
        function: Callable[[], None],
        interval: float,
        repeat: bool = True,
        name: str | None = None,
    ) -> None:
        self.function: Callable[[], None] = function
        self.interval: float = interval
        self.repeat: bool = repeat
        self.name: str = name or f"Timer-{id(self)}"
        self.last_run: float = time.time()
        self._stop_event = threading.Event()

    def should_run(self) -> bool:
        return time.time() - self.last_run >= self.interval

    def run(self) -> None:
        if self._stop_event.is_set():
            return

        try:
            self.function()

        except Exception as e:
            logger.error(f"Timer '{self.name}' raised an error: {e}")

        self.last_run = time.time()

    def stop(self) -> None:
        self._stop_event.set()


class TimerManager:
    _timers: Dict[str, Timer] = {}
    _timer_thread: threading.Thread | None = None
    _stop_event = threading.Event()

    @classmethod
    def init(cls):
        if cls._timer_thread is not None:
            return

        def timer_thread():
            while not cls._stop_event.is_set():
                timers_to_remove = []
                for name, timer in list(cls._timers.items()):
                    if timer.should_run():
                        timer.run()
                        if not timer.repeat:
                            timers_to_remove.append(name)

                for name in timers_to_remove:
                    cls._timers.pop(name, None)

            time.sleep(0.1)

        cls._timer_thread = threading.Thread(target=timer_thread, daemon=True)
        cls._timer_thread.start()

    @classmethod
    def deconstruct(cls):
        if cls._timer_thread is not None:
            cls._stop_event.set()
            cls._timer_thread.join()
            cls._timer_thread = None

        cls._timers.clear()
        cls._stop_event.clear()

    @classmethod
    def add_timer(
        cls,
        name: str | None,
        function,
        interval: float,
        repeat: bool = True,
    ):
        if name in cls._timers:
            logger.warning(f"A timer '{name}' already exists!")
            return

        timer = Timer(function, interval, repeat, name)
        cls._timers[timer.name] = timer

    @classmethod
    def remove_timer(cls, name: str):
        if name in cls._timers:
            cls._timers[name].stop()
            del cls._timers[name]

    @classmethod
    def stop_all_timers(cls):
        for timer in cls._timers.values():
            timer.stop()

        cls._timers.clear()
