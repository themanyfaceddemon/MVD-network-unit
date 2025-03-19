import dearpygui.dearpygui as dpg

from .error_popup import create_popup_window
from .select_file_folder import FileManager
from .timer import TimerManager
from .viewport_resize import ViewportResizeManager





def set_and_hide(sender, app_data, user_data):
    """Для user_data:
    [0] = куда сетать,
    [1] = что сетать,
    [2] = что прятать,
    """
    dpg.set_value(user_data[0], user_data[1])
    dpg.hide_item(user_data[2])
