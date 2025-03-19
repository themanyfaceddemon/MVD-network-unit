import dearpygui.dearpygui as dpg
from tools import create_popup_window, set_and_hide


def create_information():
    dpg.add_text("Тип дополнительной информации", parent="dynamic_fields")
    with dpg.group(horizontal=True, parent="dynamic_fields"):
        dpg.add_combo(
            [
                "Дополнение",
                "Предписание",
            ],
        )
        dpg.add_button(label="?")
        with dpg.popup(dpg.last_item(), mousebutton=dpg.mvMouseButton_Left):
            dpg.add_text("Расшифровки данных")
            dpg.add_separator()
            for text in [
                "Дополнение: Допольнительная информация о лице",
                "Предписание: Информация о здоровье лица и предписания которые требутся к ней",
            ]:
                dpg.add_text(text, wrap=0)
                dpg.add_separator()


def _submit(sender, app_data, user_data) -> None:
    pass
