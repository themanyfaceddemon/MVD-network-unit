import json

import dearpygui.dearpygui as dpg
from systems import AppConfig, ServerRequests


def _send_request():
    url = dpg.get_value("api_url")
    params = dpg.get_value("api_params")
    method = dpg.get_value("api_method")

    try:
        params_dict = json.loads(params) if params else {}
    except json.JSONDecodeError:
        dpg.set_value("api_response_anser", "Ошибка: Неверный JSON")
        return

    if method == "GET":
        response = ServerRequests._session.get(
            ServerRequests._base_url + url,
            params=params_dict,
        )
    else:
        response = ServerRequests._session.post(
            ServerRequests._base_url + url,
            json=params_dict,
        )

    dpg.set_value("api_response_code", f"Код ответа: {response.status_code}")
    dpg.set_value("api_response_anser", f"Код ответа: {response.json()}")


def create_system_tab():
    if dpg.does_item_exist("system_tab"):
        dpg.show_item("system_tab")
        dpg.set_value("main_tab_bar", "system_tab")
        return

    with dpg.tab(
        label="System control",
        parent="main_tab_bar",
        tag="system_tab",
        closable=True,
        order_mode=dpg.mvTabOrder_Reorderable,
    ):
        dpg.add_text(
            "НЕ ИСПОЛЬЗУЙТЕ ЕСЛИ НЕ ЕБЁТЕ КАК, ПРОШУ, БЛЯТЬ, НЕ ЕБИТЕ СЕРВЕР",
            color=AppConfig.attention_color,
        )
        dpg.add_input_text(label="Путь к API", tag="api_url")
        dpg.add_input_text(label="Параметры (JSON)", tag="api_params", multiline=True)
        dpg.add_combo(
            ["GET", "POST"], label="Метод", tag="api_method", default_value="GET"
        )
        dpg.add_button(label="Отправить запрос", callback=_send_request)
        dpg.add_text("", tag="api_response_code")
        dpg.add_text("", tag="api_response_anser", wrap=0)

    dpg.set_value("main_tab_bar", "system_tab")
