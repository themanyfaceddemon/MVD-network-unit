import dearpygui.dearpygui as dpg
from systems import AppConfig, ServerRequests
from tools import TimerManager

from .user_window import create_user_window

search_dict_full = {}


def create_search_tab():
    if dpg.does_item_exist("search_tab"):
        dpg.show_item("search_tab")
        dpg.set_value("main_tab_bar", "search_tab")
        return

    with dpg.tab(
        label="Поиск",
        parent="main_tab_bar",
        tag="search_tab",
        closable=True,
        order_mode=dpg.mvTabOrder_Reorderable,
    ):
        with dpg.group(horizontal=True):
            dpg.add_input_text(
                hint="Поиск по всем записям",
                tag="search_input_text",
                callback=_update_all_search_info,
            )
            dpg.add_button(label="Синхронизация", callback=_update_search_dict)

        with dpg.child_window(
            autosize_x=True,
            autosize_y=True,
            tag="all_search_info",
        ):
            pass

    TimerManager.add_timer(
        "update_search_dict",
        _update_search_dict,
        AppConfig.server_data_update_time,
    )
    _update_search_dict()
    dpg.set_value("main_tab_bar", "search_tab")


def _update_search_dict():
    answer = ServerRequests.get_all_users()
    if not answer:
        return

    global search_dict_full
    search_dict_full = {user["id"]: user for user in answer}

    _update_all_search_info()


def _update_all_search_info(sender=None, app_data=None):
    dpg.delete_item("all_search_info", children_only=True)
    global search_dict_full

    def get_display_name(user):
        parts = []
        name_rus = user.get("nameRus") or None
        name_eng = user.get("nameEng") or None
        cs_name = user.get("cs") or None

        if name_rus:
            parts.append(name_rus)
        if name_eng:
            parts.append(name_eng)
        if cs_name:
            parts.append(f"'{cs_name}'")
        return " | ".join(parts) or "Без имени"

    search_query = dpg.get_value("search_input_text").strip().lower()
    items = []

    if search_query:
        search_terms = search_query.split()
        for user_id, user in search_dict_full.items():
            search_target = ""
            search_target += f"{str(user_id).lower()} "

            if user.get("nameRus"):
                search_target += user["nameRus"].lower() + " "
            if user.get("nameEng"):
                search_target += user["nameEng"].lower() + " "
            if user.get("cs"):
                search_target += user["cs"].lower() + " "

            if all(term in search_target for term in search_terms):
                items.append((get_display_name(user), user_id))
    else:
        items = [
            (get_display_name(user), user_id)
            for user_id, user in search_dict_full.items()
        ]

    if not items:
        dpg.add_text("По вашему запросу ничего не найдено", parent="all_search_info")
        return

    with dpg.table(
        parent="all_search_info",
        header_row=False,
        policy=dpg.mvTable_SizingStretchSame,
        resizable=False,
        borders_innerV=True,
        borders_outerV=True,
        borders_outerH=True,
        borders_innerH=True,
        tag="all_search_info_table",
    ):
        dpg.add_table_column()
        dpg.add_table_column()
        dpg.add_table_column()

        for i in range(0, len(items), 3):
            with dpg.table_row():
                for item in items[i : i + 3]:
                    dpg.add_selectable(
                        label=item[0],
                        user_data=item[1],
                        callback=_sel_callback,
                    )


def _sel_callback(sender, app_data, user_data) -> None:
    dpg.set_value(sender, False)
    create_user_window(user_data)
