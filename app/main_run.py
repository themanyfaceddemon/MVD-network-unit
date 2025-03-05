import logging
import threading

import dearpygui.dearpygui as dpg
from tools import TimerManager


class App:
    @classmethod
    def run(cls) -> None:
        try:
            dpg.start_dearpygui()

        except Exception as e:
            logging.error(f"Error during running GUI: {e}")

        finally:
            logging.debug("Destroying app...")

            TimerManager.stop_all_timers()
            TimerManager.deconstruct()

            for thread in threading.enumerate():
                if thread is not threading.main_thread():
                    if not thread.daemon:
                        logging.debug(f"Waiting for thread {thread.name} to finish...")
                        thread.join()

            dpg.destroy_context()
