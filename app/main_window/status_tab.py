import dearpygui.dearpygui as dpg
from systems import AppConfig, ServerRequests
from tools import TimerManager


def create_status_tab():
    if dpg.does_item_exist("status_tab"):
        dpg.show_item("status_tab")
        dpg.set_value("main_tab_bar", "status_tab")
        return

    with dpg.tab(
        label="Просмотр статуса записей",
        parent="main_tab_bar",
        tag="status_tab",
        closable=True,
        order_mode=dpg.mvTabOrder_Reorderable,
    ):
        dpg.add_input_text(
            hint="Введите имя сотрудника",
            show=ServerRequests.has_access("see_user_queue"),
            tag="status_input_name",
            callback=_update_status_dict,
        )
        dpg.add_group(tag="status_tab_data")

    TimerManager.add_timer(
        "update_status_dict",
        _update_status_dict,
        AppConfig.server_data_update_time,
    )
    _update_status_dict()
    dpg.set_value("main_tab_bar", "status_tab")


def _update_status_dict():
    dpg.delete_item("status_tab_data", children_only=True)
    name = dpg.get_value("status_input_name") or None
    data = ServerRequests.get_user_queue(name)

    with dpg.group(parent="status_tab_data"):
        data = data.get("data", [])
        if not data:
            dpg.add_text("Данные не были обнаружены")
            return

        for item in data:
            item_data = item.get("data")
            if not item_data:
                continue

            parts = []
            name_rus = item_data.get("nameRus")
            name_eng = item_data.get("nameEng")
            name_cs = item_data.get("cs")

            if name_rus:
                parts.append(name_rus)
            if name_eng:
                parts.append(name_eng)
            if name_cs:
                parts.append(f"'{name_cs}'")

            approved_by = item.get("approved_by") or "Ещё не обработано"
            status = {
                "pending": "На рассмотрении",
                "approved": "Принято",
                "rejected": "Отклонено",
            }.get(item.get("status"), "Неизвестный статус")
            reason = item.get("reason") or "Не указано"

            with dpg.collapsing_header(label=(" | ".join(parts) or "Без имени")):
                dpg.add_text(f"Кто занимался рассмотрением: {approved_by}")
                dpg.add_text(f"Статус запроса: {status}")
                if status == "Отклонено":
                    dpg.add_text(f"Причина отклонения: {reason}")
