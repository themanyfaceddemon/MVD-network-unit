import re
import tempfile
from pathlib import Path

import dearpygui.dearpygui as dpg
from PIL import ImageGrab
from systems import AppConfig, ServerRequests
from tools import create_popup_window

img_data_path = None


def create_mercenarie():
    dpg.add_combo(
        [
            "Кукла",
            "Получеловек",
            "Человек",
        ],
        label="Раса",
        default_value="Человек",
        parent="dynamic_fields",
        callback=_on_race_cel,
    )
    dpg.add_separator(parent="dynamic_fields")

    dpg.add_group(tag="add_db_fields", parent="dynamic_fields")
    _on_race_cel(None, "Человек", None)


def _on_race_cel(sender, app_data, user_data):
    if not dpg.does_item_exist("add_db_fields"):
        return

    dpg.delete_item("add_db_fields", children_only=True)

    func_dict = {
        "Кукла": _add_db_doll,
        "doll": _add_db_doll,
        "Получеловек": _add_db_halfhuman,
        "halfhuman": _add_db_halfhuman,
        "Человек": _add_db_human,
        "human": _add_db_human,
    }
    func = func_dict.get(app_data, None)
    if func:
        func()


def _add_db_doll():
    _add_name_info("Имя")
    dpg.add_separator(parent="add_db_fields")
    _add_sex_field()
    dpg.add_separator(parent="add_db_fields")
    dpg.add_combo(
        ["M", "A", "T"],
        label="Тип",
        default_value="T",
        parent="add_db_fields",
        tag="input_type",
    )
    with dpg.group(horizontal=True, parent="add_db_fields"):
        dpg.add_input_text(
            hint="Модель",
            tag="input_model",
        )
        dpg.add_button(label="...")
        with dpg.popup(dpg.last_item(), mousebutton=dpg.mvMouseButton_Left) as con:
            for model in [
                "ALR-52P",
                "CRAR Relic Explorer",
                "LG II Landscaper",
                "ME78",
                "Pastrychef SP",
                "RPVII",
                "S-WG",
            ]:
                dpg.add_button(
                    label=model,
                    callback=_set_and_hide,
                    user_data=("input_model", model, con),
                )

    dpg.add_separator(parent="add_db_fields")
    _add_add_info()
    dpg.add_separator(parent="add_db_fields")
    _add_img()
    dpg.add_button(
        label="Отправить",
        user_data="doll",
        callback=_submit,
        parent="add_db_fields",
    )


def _add_db_halfhuman():
    _add_name_info()
    dpg.add_separator(parent="add_db_fields")
    _add_sex_field()
    dpg.add_separator(parent="add_db_fields")
    dpg.add_input_text(
        hint="Тип",
        parent="add_db_fields",
        tag="input_type",
    )
    dpg.add_separator(parent="add_db_fields")
    _add_add_info()
    dpg.add_separator(parent="add_db_fields")
    _add_img()
    dpg.add_button(
        label="Отправить",
        user_data="halfhuman",
        callback=_submit,
        parent="add_db_fields",
    )


def _add_db_human():
    _add_name_info()
    dpg.add_separator(parent="add_db_fields")
    _add_sex_field()
    dpg.add_separator(parent="add_db_fields")
    _add_add_info()
    dpg.add_separator(parent="add_db_fields")
    _add_img()
    dpg.add_button(
        label="Отправить",
        user_data="human",
        callback=_submit,
        parent="add_db_fields",
    )


def _add_name_info(label="ФИО"):
    dpg.add_input_text(
        hint=f"{label} (RUS)", tag="input_name_rus", parent="add_db_fields"
    )
    dpg.add_input_text(
        hint=f"{label} (ENG)", tag="input_name_eng", parent="add_db_fields"
    )
    dpg.add_input_text(hint="Позывной", tag="input_cs", parent="add_db_fields")


def _add_sex_field():
    dpg.add_combo(
        ["Мужской", "Женский"],
        label="Пол",
        default_value="Мужской",
        parent="add_db_fields",
        tag="input_sex",
    )


def _add_add_info():
    with dpg.group(horizontal=True, parent="add_db_fields"):
        dpg.add_input_text(
            hint="Место рождения",
            tag="input_pob",
        )
        dpg.add_button(label="...")
        with dpg.popup(dpg.last_item(), mousebutton=dpg.mvMouseButton_Left) as con:
            for contry in ["НСССР", "Германия", "Англия", "США", "Китай", "Япония"]:
                dpg.add_button(
                    label=contry,
                    callback=_set_and_hide,
                    user_data=("input_pob", contry, con),
                )

    with dpg.group(horizontal=True, parent="add_db_fields"):
        dpg.add_input_text(
            hint="Специализация",
            tag="input_spec",
        )
        dpg.add_button(label="...")
        with dpg.popup(dpg.last_item(), mousebutton=dpg.mvMouseButton_Left) as con:
            for spec in [
                "Военный",
                "Бывший военный",
                "Член ЧВК",
                "Гражданский",
                "Инженер",
            ]:
                dpg.add_button(
                    label=spec,
                    callback=_set_and_hide,
                    user_data=("input_spec", spec, con),
                )

    with dpg.group(horizontal=True, parent="add_db_fields"):
        dpg.add_input_text(
            hint="Цель прибытия в сектор",
            tag="input_goal",
        )
        dpg.add_button(label="...")
        with dpg.popup(dpg.last_item(), mousebutton=dpg.mvMouseButton_Left) as con:
            for goal in ["Заработок", "Работа", "ПМЖ"]:
                dpg.add_button(
                    label=goal,
                    callback=_set_and_hide,
                    user_data=("input_goal", goal, con),
                )


def _set_and_hide(sender, app_data, user_data):
    dpg.set_value(user_data[0], user_data[1])
    dpg.hide_item(user_data[2])


def _add_img():
    global img_data_path
    img_data_path = None

    dpg.add_button(
        label="Загрузить фото из буфера обмена",
        callback=_load_img_to_create,
        parent="add_db_fields",
    )
    with dpg.group(horizontal=True, parent="add_db_fields"):
        dpg.add_text("Статус:")
        dpg.add_text("Не загружено", tag="img_status", color=AppConfig.red_color)


def _load_img_to_create():
    image = ImageGrab.grabclipboard()

    if isinstance(image, list):
        dpg.configure_item("img_status", color=AppConfig.red_color)
        dpg.set_value("img_status", "Информация в буффере не является изображением")
        return

    if image is None:
        dpg.configure_item("img_status", color=AppConfig.red_color)
        dpg.set_value("img_status", "Изображение не обнаружено")
        return

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        image.save(tmp, format="PNG")
        global img_data_path
        img_data_path = Path(tmp.name)

    dpg.configure_item("img_status", color=AppConfig.green_color)
    dpg.set_value("img_status", "Успешно загружено")


def _has_cyrillic(text: str) -> bool:
    return bool(re.search(r"[а-яё]", text.lower()))


def _has_latin(text: str) -> bool:
    return bool(re.search(r"[a-z]", text.lower()))


def _submit(sender, app_data, user_data) -> None:
    global img_data_path

    if img_data_path is None:
        create_popup_window(
            "Ошибка создания записи",
            "Не обнаружена фотография прикреплённая к записи",
        )
        return

    name_rus: str | None = dpg.get_value("input_name_rus") or None
    name_eng: str | None = dpg.get_value("input_name_eng") or None
    name_cs: str | None = dpg.get_value("input_cs") or None

    name_f = "имя" if user_data == "doll" else "ФИО"
    if not any([name_rus, name_eng, name_cs]):
        create_popup_window(
            "Ошибка создания записи",
            f"Одно из следующих полей обязательно должно быть заполнено: {name_f.capitalize()} на русском или английском; позывной",
        )
        return

    if name_eng and _has_cyrillic(name_eng):
        create_popup_window(
            "Ошибка создания записи",
            f"Английское {name_f} не может содержать кирилические символы",
        )
        return

    if name_rus and _has_latin(name_rus):
        create_popup_window(
            "Ошибка создания записи",
            f"Русское {name_f} не может содержать латинские символы",
        )
        return

    sex: str | None = dpg.get_value("input_sex")
    match sex:
        case "Мужской":
            sex = "male"

        case "Женский":
            sex = "female"

        case _:
            create_popup_window(
                "Ошибка создания записи",
                "Ошибка определения пола",
            )
            return

    pob: str | None = dpg.get_value("input_pob") or None
    spec: str | None = dpg.get_value("input_spec") or None
    goal: str | None = dpg.get_value("input_goal") or None
    model: str | None = dpg.get_value("input_model") or None
    user_type: str | None = dpg.get_value("input_type") or None

    anser = 0
    match user_data:
        case "human":
            anser = ServerRequests.create_human(
                nameRus=name_rus,
                nameEng=name_eng,
                cs=name_cs,
                sex=sex,
                pob=pob,
                specialization=spec,
                goal=goal,
                file_path=img_data_path,
            )
        case "halfhuman":
            if not user_type:
                create_popup_window(
                    "Ошибка создания записи",
                    "Тип получеловека не был определён",
                )
                return

            anser = ServerRequests.create_halfhuman(
                nameRus=name_rus,
                nameEng=name_eng,
                type=user_type,
                cs=name_cs,
                sex=sex,
                pob=pob,
                specialization=spec,
                goal=goal,
                file_path=img_data_path,
            )
        case "doll":
            if not AppConfig.is_doll_model_value(user_type):
                create_popup_window(
                    "Ошибка создания записи",
                    "Ошибка определения типа куклы",
                )
                return

            if not model:
                create_popup_window(
                    "Ошибка создания записи",
                    "Модель куклы не была указана",
                )
                return

            anser = ServerRequests.create_doll(
                nameRus=name_rus,
                nameEng=name_eng,
                cs=name_cs,
                type=user_type,
                model=model,
                sex=sex,
                pob=pob,
                specialization=spec,
                goal=goal,
                file_path=img_data_path,
            )
        case _:
            create_popup_window(
                "Ошибка", "У разраба рак мозга. Как вы сюда вообще попали?"
            )

    ls_anser = {
        201: ["Успешно", "Запись успешно создана"],
        202: ["Успешно", "Запись отправлена на рассмотрение"],
        400: [
            "Ошибка создания записи",
            "Сервер не скушал данные, опять Вуди вылил алкоголь на плату",
        ],
        500: [
            "Ошибка создания записи",
            "Сервер скончался на месте обработки. Доложите руководителю системы об этом",
        ],
        900: [
            "Ошибка создания записи",
            "Сервер отказал в регистрации данного пользователя",
        ],
    }.get(
        anser,
        ["Ошибка создания записи", f"Неизвестная ошибка от сервера #{anser}"],
    )

    create_popup_window(ls_anser[0], ls_anser[1])
    _on_race_cel(None, user_data, None)
