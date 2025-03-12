import dearpygui.dearpygui as dpg
from systems import ServerRequests
from tools import create_popup_window


def create_doll_link():
    if not ServerRequests.has_access("doll_register"):
        dpg.add_text(
            "Доступ к созданию регистраций куклы отклонён",
            parent="dynamic_fields",
            wrap=0,
        )
        return

    dpg.add_input_text(
        parent="dynamic_fields",
        hint="UUID куклы",
        tag="input_doll_UUID",
        width=0,
    )

    dpg.add_input_text(
        parent="dynamic_fields",
        hint="UUID командира",
        tag="input_comand_UUID",
        width=0,
    )

    dpg.add_button(
        label="Отправить",
        callback=_submit,
        parent="dynamic_fields",
    )


def _submit(sender, app_data, user_data) -> None:
    doll_UUID: str | None = dpg.get_value("input_doll_UUID") or None
    comand_UUID: str | None = dpg.get_value("input_comand_UUID") or None

    if not doll_UUID:
        create_popup_window(
            "Ошибка создания записи",
            "Одно из следующих полей обязательно должно быть заполнено: UUID куклы",
        )
        return

    if not comand_UUID:
        create_popup_window(
            "Ошибка создания записи",
            "Одно из следующих полей обязательно должно быть заполнено: UUID командира",
        )
        return

    status_code = ServerRequests.add_doll_reg(comand_UUID, doll_UUID)
    if status_code == 200:
        create_popup_window("Успешно", "Запись успешно создана")
        return

    {
        400: [
            "Ошибка создания регистрации",
            "Один из двух UUID не существует в базе данных. Проверьте написание",
        ]
    }.get(
        status_code,
        [
            "Неизвестная ошибка сервера",
            f"Сервер словил необработанную ошибку #{status_code}",
        ],
    )
