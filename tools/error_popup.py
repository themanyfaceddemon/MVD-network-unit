import dearpygui.dearpygui as dpg

from .viewport_resize import ViewportResizeManager


def create_error_popup(title: str, info: str):
    if not dpg.does_item_exist("error_warning_window"):
        with dpg.window(
            modal=True,
            no_collapse=True,
            no_move=True,
            no_resize=True,
            no_close=True,
            label=title,
            tag="error_warning_window",
            pos=[0, 0],
        ):
            dpg.add_text(info, wrap=0)
            dpg.add_button(label="OK", callback=_del_item)

        ViewportResizeManager.add_callback("error_warning_window", _res)
        dpg.focus_item("error_warning_window")


def _res(app_data):
    dpg.set_item_width("error_warning_window", app_data[2] * 0.5)
    dpg.set_item_height("error_warning_window", app_data[3] * 0.5)
    dpg.set_item_pos(
        "error_warning_window",
        [
            (app_data[2] - app_data[2] * 0.5) * 0.5,
            (app_data[3] - app_data[3] * 0.5) * 0.5,
        ],
    )


def _del_item():
    if dpg.does_item_exist("error_warning_window"):
        dpg.delete_item("error_warning_window")
        ViewportResizeManager.remove_callback("error_warning_window")
