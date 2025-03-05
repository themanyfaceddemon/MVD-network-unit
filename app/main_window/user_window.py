from typing import Any

import dearpygui.dearpygui as dpg
import pyperclip
from systems import AppConfig, ServerRequests
from tools import ViewportResizeManager, create_error_popup


def create_user_window(user_id: str) -> None:
    _delete_window()

    user_data = ServerRequests.get_user_info(user_id)
    if not user_data:
        create_error_popup(
            "Ошибка получения данных",
            "Сервер не передал данные о выбранном клиенте",
        )
        return

    name_rus: str | None = user_data.get("nameRus")
    name_eng: str | None = user_data.get("nameEng")
    name_cs: str | None = user_data.get("cs")
    race: str | None = user_data.get("race")
    pob: str | None = user_data.get("pob")
    goal: str | None = user_data.get("goal")
    type: str | None = user_data.get("type")
    model: str | None = user_data.get("model")
    specialization: str | None = user_data.get("specialization")
    photo_file = user_data.get("photo_file")
    sex: str = "Мужской" if user_data.get("sex") == "male" else "Женский"

    photo_path = None
    if photo_file:
        photo_path = ServerRequests.get_image(photo_file)

    if photo_path:
        width, height, _, data = dpg.load_image(str(photo_path))
        with dpg.texture_registry():
            dpg.add_static_texture(width, height, data, tag="user_texture")

    with dpg.window(
        tag="user_window_see_1",
        no_move=True,
        no_resize=True,
        no_title_bar=True,
        pos=[0, 0],
    ):
        _add_uuid_section(user_id)
        _add_info_table(
            name_rus=name_rus,
            name_eng=name_eng,
            name_cs=name_cs,
            race=race,
        )
        _add_race_section(race)
        _add_optional_sections(type=type, model=model, race=race)
        dpg.add_separator()
        _add_sex_section(sex)
        dpg.add_separator()
        _add_additional_info(
            "Место производства:" if race == "doll" else "Место рождения:",
            pob,
            "pob",
        )
        _add_additional_info(
            "Цель в секторе:",
            goal,
            "goal",
        )
        _add_additional_info(
            "Специализация:",
            specialization,
            "specialization",
        )
        with dpg.group(horizontal=True, tag="see_close_btn"):
            dpg.add_button(label="Закрыть", callback=_delete_window)
            dpg.add_button(
                label="Удалить запись",
                callback=_delete_record,
                user_data=user_id,
                show=ServerRequests.has_access("delete_user_data"),
            )

    with dpg.window(
        tag="user_window_see_2",
        no_move=True,
        no_resize=True,
        no_title_bar=True,
        pos=[0, 0],
    ):
        dpg.add_text("Колёсико мыши - просматривать по вертикали", wrap=0)
        dpg.add_text("Shift + колёсико мыши - просмотра по горизонтали", wrap=0)

        with dpg.child_window(
            auto_resize_x=True,
            auto_resize_y=True,
            horizontal_scrollbar=True,
        ):
            if dpg.does_item_exist("user_texture"):
                dpg.add_image("user_texture")
            else:
                dpg.add_text("Изображение не обнаружено")

    ViewportResizeManager.add_callback("user_window_see", _resize_callback)


def _resize_callback(app_data):
    item_width = app_data[2] / 2
    dpg.set_item_pos("user_window_see_2", [item_width, 0])

    for tag in ["user_window_see_1", "user_window_see_2"]:
        dpg.set_item_width(tag, item_width)
        dpg.set_item_height(tag, app_data[3])

    dpg.set_item_pos("see_close_btn", [8, app_data[3] - 28])


def _copy(sender, app_data, user_data):
    pyperclip.copy(user_data[0])
    dpg.hide_item(user_data[1])


def _delete_window():
    ViewportResizeManager.remove_callback("user_window_see")
    for tag in ["user_window_see_1", "user_window_see_2", "user_texture"]:
        if dpg.does_item_exist(tag):
            dpg.delete_item(tag)


def _delete_record(sender, app_data, user_data):
    code = ServerRequests.delete_user_data(user_data)
    if code == 200:
        _delete_window()


def _add_uuid_section(user_id: str):
    with dpg.group(horizontal=True):
        dpg.add_text("UUID:")
        dpg.add_text(
            user_id,
            tag="cur_user_uuid",
            color=AppConfig.uuid_color,
            wrap=0,
        )
        with dpg.popup("cur_user_uuid") as tooltip_id:
            dpg.add_button(
                label="Скопировать",
                callback=_copy,
                user_data=[user_id, tooltip_id],
            )


def _add_info_table(
    name_rus: str | None,
    name_eng: str | None,
    name_cs: str | None,
    race,
):
    name_label_rus = "Имя (RUS):" if race == "doll" else "ФИО (RUS):"
    name_label_eng = "Имя (ENG):" if race == "doll" else "ФИО (ENG):"
    with dpg.table(
        header_row=True,
        policy=dpg.mvTable_SizingStretchSame,
        resizable=False,
        borders_innerV=True,
        borders_outerV=True,
        borders_outerH=True,
        borders_innerH=True,
    ):
        dpg.add_table_column(label=name_label_rus)
        dpg.add_table_column(label=name_label_eng)
        if not race == "doll":
            dpg.add_table_column(label="Позывной:")

        with dpg.table_row():
            name_rus = name_rus if name_rus else "Отсутствует"
            name_eng = name_eng if name_eng else "Отсутствует"
            dpg.add_text(
                name_rus,
                wrap=0,
            )
            _add_ch_container_text(dpg.last_item(), name_rus, "nameRus")

            dpg.add_text(
                name_eng,
                wrap=0,
            )
            _add_ch_container_text(dpg.last_item(), name_eng, "nameEng")

            if not race == "doll":
                dpg.add_text(
                    name_cs if name_cs else "Отсутствует",
                    wrap=0,
                )
                _add_ch_container_text(
                    dpg.last_item(),
                    name_cs if name_cs else "Отсутствует",
                    "cs",
                )


def _add_race_section(race: str | None):
    tr_race = {
        "doll": "Кукла",
        "human": "Человек",
        "halfhuman": "Полу-человек",
        None: "ОШИБКА ОПРЕДЕЛЕНИЯ РАСЫ",
    }
    with dpg.group(horizontal=True):
        dpg.add_text("Раса:")
        dpg.add_text(
            tr_race.get(race, "ОШИБКА ОПРЕДЕЛЕНИЯ РАСЫ"),
            wrap=0,
        )


def _add_optional_sections(type: str | None, model: str | None, race):
    if race != "human":
        label = "Тип куклы:" if race == "doll" else "Тип полулюда:"
        user_type_field = type if type else "Не указано"
        with dpg.group(horizontal=True) as gr:
            dpg.add_text(label)
            dpg.add_text(
                user_type_field,
                wrap=0,
            )
        if race == "doll":
            _add_ch_container_combo(gr, ["T", "A", "M"], user_type_field, "type")

        else:
            _add_ch_container_text(gr, user_type_field, "type")

    if race == "doll":
        model = model if model else "Не указано"
        with dpg.group(horizontal=True) as gr:
            dpg.add_text("Модель:")
            dpg.add_text(
                model,
                wrap=0,
            )
            _add_ch_container_text(gr, model, "model")


def _add_sex_section(sex: str):
    with dpg.group(horizontal=True) as gr:
        dpg.add_text("Пол:")
        color = AppConfig.female_color if sex == "Женский" else AppConfig.male_color
        dpg.add_text(sex, color=color, wrap=0)

    _add_ch_container_combo(gr, ["Женский", "Мужской"], sex, "sex")


def _add_additional_info(label: str, value: str | None, tag_to_ch: str):
    value = value if value else "Отсутствует"
    with dpg.group(horizontal=True) as gr:
        dpg.add_text(label)
        dpg.add_text(value, wrap=0)
    _add_ch_container_text(gr, value, tag_to_ch)


def _add_ch_container_text(
    parent,
    default_value: str,
    tag_to_ch: str,
):
    if not ServerRequests.has_access("change_user_data"):
        return

    with dpg.popup(parent):
        dpg.add_text("Изменение значения:")

        text_id = dpg.add_input_text(
            hint="Новое значение",
            default_value=default_value,
            on_enter=True,
            callback=lambda s, a, u: _ch_callback(a, tag_to_ch),
        )
        with dpg.group(horizontal=True):
            dpg.add_button(
                label="Подтвердить",
                callback=lambda: _ch_callback(dpg.get_value(text_id), tag_to_ch),
            )
            dpg.add_button(
                label="Очистить значение",
                callback=lambda: _ch_callback(None, tag_to_ch),
            )


def _add_ch_container_combo(
    parent,
    items: list[str],
    default_value: str,
    tag_to_ch: str,
):
    if not ServerRequests.has_access("change_user_data"):
        return

    with dpg.popup(parent):
        dpg.add_text("Изменение значения:")
        dpg.add_combo(
            items,
            default_value=default_value,
            callback=lambda s, a, u: _ch_callback(a, tag_to_ch),
        )


def _ch_callback(value: Any, tag_to_ch: str) -> None:
    user_uuid = dpg.get_value("cur_user_uuid")

    if tag_to_ch == "sex":
        value = "male" if value == "Мужской" else "female"

    ServerRequests.change_user_data(user_uuid, {tag_to_ch: value})
    create_user_window(user_uuid)
