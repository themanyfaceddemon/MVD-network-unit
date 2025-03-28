import dearpygui.dearpygui as dpg

from .doll_link import create_doll_link
from .information_create import create_information
from .license_create import create_license
from .mercenaries_create import create_mercenarie

CREATE_TAB_ITEMS = {
    "Добавление регистрации в базу данных": create_mercenarie,
    "Привязка куклы": create_doll_link,
    # "Ввод дополнительных данных": create_information,
    # "Создание лицензий": create_license,
}


def create_create_tab():
    if dpg.does_item_exist("create_tab"):
        dpg.show_item("create_tab")
        dpg.set_value("main_tab_bar", "create_tab")
        return

    with dpg.tab(
        label="Конструктор данных",
        parent="main_tab_bar",
        tag="create_tab",
        closable=True,
        order_mode=dpg.mvTabOrder_Reorderable,
    ):
        dpg.add_text("Выберите действие:", tag="entry_type_selector_text")
        dpg.add_combo(
            list(CREATE_TAB_ITEMS.keys()),
            default_value="Добавление регистрации в базу данных",
            callback=_on_selection_change,
            tag="entry_type_selector",
        )
        dpg.add_separator()
        dpg.add_group(tag="dynamic_fields")
        _on_selection_change(None, "Добавление регистрации в базу данных", None)

    dpg.set_value("main_tab_bar", "create_tab")


def _on_selection_change(sender, app_data, user_data):
    dpg.delete_item("dynamic_fields", children_only=True)

    func = CREATE_TAB_ITEMS.get(app_data, None)
    if func:
        func()
