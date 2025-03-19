import dearpygui.dearpygui as dpg
from structures import get_display_name
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
            dpg.add_checkbox(
                label="Живые",
                tag="ch_box_search_alive",
                default_value=AppConfig.get("ch_box_search_alive", True),
                callback=_handle_checkbox_change,
            )
            dpg.add_checkbox(
                label="Мёртвые",
                tag="ch_box_search_dead",
                default_value=AppConfig.get("ch_box_search_dead", True),
                callback=_handle_checkbox_change,
            )
            dpg.add_checkbox(
                label="Пропали без вести",
                tag="ch_box_search_missing",
                default_value=AppConfig.get("ch_box_search_missing", True),
                callback=_handle_checkbox_change,
            )
            dpg.add_checkbox(
                label="На рассмотрении",
                tag="ch_box_search_on_review",
                default_value=AppConfig.get("ch_box_search_on_review", False),
                callback=_handle_checkbox_change,
            )

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
    TimerManager.add_timer("delete_search_dict", _delete_on_hide, 5)

    _update_search_dict()
    dpg.set_value("main_tab_bar", "search_tab")


def _delete_on_hide():
    if dpg.is_item_shown("search_tab") is False:
        TimerManager.remove_timer("update_search_dict")
        TimerManager.remove_timer("delete_search_dict")
        dpg.delete_item("search_tab")


def _handle_checkbox_change(sender, app_data):
    AppConfig.set(sender, app_data)
    _update_all_search_info()


def _update_search_dict():
    answer = ServerRequests.get_all_users()
    if not answer:
        return

    global search_dict_full
    search_dict_full = {user["user_uuid"]: user for user in answer}

    _update_all_search_info()


def _update_all_search_info():
    dpg.delete_item("all_search_info", children_only=True)
    global search_dict_full

    selected_statuses = []
    if dpg.get_value("ch_box_search_alive"):
        selected_statuses.append("alive")
    if dpg.get_value("ch_box_search_dead"):
        selected_statuses.append("dead")
    if dpg.get_value("ch_box_search_missing"):
        selected_statuses.append("missing")
    if dpg.get_value("ch_box_search_on_review"):
        selected_statuses.append("on_review")

    if not selected_statuses:
        dpg.add_text(
            "Выберите хотя бы один статус для отображения", parent="all_search_info"
        )
        return

    search_query = dpg.get_value("search_input_text").strip().lower()
    items = []

    if search_query:
        search_terms = search_query.split()
        for user_id, user in search_dict_full.items():
            if user.get("status") not in selected_statuses:
                continue

            search_target = ""
            search_target += f"{str(user_id).lower()} "

            if user.get("name_rus"):
                search_target += user["name_rus"].lower() + " "
            if user.get("name_eng"):
                search_target += user["name_eng"].lower() + " "
            if user.get("name_cs"):
                search_target += user["name_cs"].lower() + " "

            if all(term in search_target for term in search_terms):
                items.append((get_display_name(user), user_id))
    else:
        items = [
            (get_display_name(user), user_id)
            for user_id, user in search_dict_full.items()
            if user.get("status") in selected_statuses
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
