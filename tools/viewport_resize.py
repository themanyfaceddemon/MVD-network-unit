import logging
from collections.abc import Callable
from typing import Dict

import dearpygui.dearpygui as dpg

logger = logging.getLogger(__name__)


class ViewportResizeManager:
    callback_dict: Dict[str, Callable] = {}
    _debounce_timer = None

    @classmethod
    def init(cls):
        dpg.set_viewport_resize_callback(cls._execute_callbacks)

    @classmethod
    def add_callback(cls, key: str, callback: Callable):
        cls.callback_dict[key] = callback
        cls.invoke()

    @classmethod
    def remove_callback(cls, key: str):
        if key in cls.callback_dict:
            del cls.callback_dict[key]

    @classmethod
    def invoke(cls):
        cls._execute_callbacks()

    @classmethod
    def _execute_callbacks(cls):
        app_data = (
            dpg.get_viewport_width(),
            dpg.get_viewport_height(),
            dpg.get_viewport_client_width(),
            dpg.get_viewport_client_height(),
        )

        for key, callback in cls.callback_dict.items():
            try:
                if callable(callback):
                    if callback.__code__.co_argcount == 0:
                        callback()
                    else:
                        callback(app_data)

            except Exception as e:
                logger.error(f"Error in callback '{key}': {e}")
