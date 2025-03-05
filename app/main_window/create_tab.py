import re
import tempfile
from pathlib import Path

import dearpygui.dearpygui as dpg
from PIL import ImageGrab
from systems import AppConfig, ServerRequests
from tools import create_error_popup

img_data_path = None


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
            ["Добавление регистрации в базу данных"],
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
    global img_data_path
    img_data_path = None

    if app_data == "Добавление регистрации в базу данных":
        _update_add_db()


def _update_add_db():
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
    _add_name_info("Имя", False)
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
            dpg.add_button(
                label="ALR-52P",
                callback=_set_and_hide,
                user_data=("input_model", "ALR-52P", con),
            )
            dpg.add_button(
                label="CRAR Relic Explorer",
                callback=_set_and_hide,
                user_data=("input_model", "CRAR Relic Explorer", con),
            )
            dpg.add_button(
                label="LG II Landscaper",
                callback=_set_and_hide,
                user_data=("input_model", "LG II Landscaper", con),
            )
            dpg.add_button(
                label="ME78",
                callback=_set_and_hide,
                user_data=("input_model", "ME78", con),
            )
            dpg.add_button(
                label="Pastrychef SP",
                callback=_set_and_hide,
                user_data=("input_model", "Pastrychef SP", con),
            )
            dpg.add_button(
                label="RPVII",
                callback=_set_and_hide,
                user_data=("input_model", "RPVII", con),
            )
            dpg.add_button(
                label="S-WG",
                callback=_set_and_hide,
                user_data=("input_model", "S-WG", con),
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


def _add_name_info(label="ФИО", has_cs: bool = True):
    dpg.add_input_text(
        hint=f"{label} (RUS)", tag="input_name_rus", parent="add_db_fields"
    )
    dpg.add_input_text(
        hint=f"{label} (ENG)", tag="input_name_eng", parent="add_db_fields"
    )
    if has_cs:
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
            dpg.add_button(
                label="НСССР",
                callback=_set_and_hide,
                user_data=("input_pob", "НСССР", con),
            )
            dpg.add_button(
                label="Германия",
                callback=_set_and_hide,
                user_data=("input_pob", "Германия", con),
            )
            dpg.add_button(
                label="Англия",
                callback=_set_and_hide,
                user_data=("input_pob", "Англия", con),
            )
            dpg.add_button(
                label="США",
                callback=_set_and_hide,
                user_data=("input_pob", "США", con),
            )
            dpg.add_button(
                label="Китай",
                callback=_set_and_hide,
                user_data=("input_pob", "Китай", con),
            )
            dpg.add_button(
                label="Япония",
                callback=_set_and_hide,
                user_data=("input_pob", "Япония", con),
            )

    with dpg.group(horizontal=True, parent="add_db_fields"):
        dpg.add_input_text(
            hint="Специализация",
            tag="input_spec",
        )
        dpg.add_button(label="...")
        with dpg.popup(dpg.last_item(), mousebutton=dpg.mvMouseButton_Left) as con:
            dpg.add_button(
                label="Военный",
                callback=_set_and_hide,
                user_data=("input_spec", "Военный", con),
            )
            dpg.add_button(
                label="Бывший военный",
                callback=_set_and_hide,
                user_data=("input_spec", "Бывший военный", con),
            )
            dpg.add_button(
                label="Член ЧВК",
                callback=_set_and_hide,
                user_data=("input_spec", "Член ЧВК", con),
            )
            dpg.add_button(
                label="Гражданский",
                callback=_set_and_hide,
                user_data=("input_spec", "Гражданский", con),
            )
            dpg.add_button(
                label="Инженер",
                callback=_set_and_hide,
                user_data=("input_spec", "Инженер", con),
            )

    with dpg.group(horizontal=True, parent="add_db_fields"):
        dpg.add_input_text(
            hint="Цель прибытия в сектор",
            tag="input_goal",
        )
        dpg.add_button(label="...")
        with dpg.popup(dpg.last_item(), mousebutton=dpg.mvMouseButton_Left) as con:
            dpg.add_button(
                label="Заработок",
                callback=_set_and_hide,
                user_data=("input_goal", "Заработок", con),
            )
            dpg.add_button(
                label="Работа",
                callback=_set_and_hide,
                user_data=("input_goal", "Работа", con),
            )
            dpg.add_button(
                label="Проживание",
                callback=_set_and_hide,
                user_data=("input_goal", "Проживание", con),
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


def has_cyrillic(text: str) -> bool:
    return bool(re.search(r"[а-яё]", text.lower()))


def has_latin(text: str) -> bool:
    return bool(re.search(r"[a-z]", text.lower()))


def _submit(sender, app_data, user_data) -> None:
    global img_data_path

    if img_data_path is None:
        create_error_popup(
            "Ошибка создания записи",
            "Не обнаружена фотография прикреплённая к записи",
        )
        return

    name_rus: str | None = (
        dpg.get_value("input_name_rus") if dpg.get_value("input_name_rus") else None
    )
    name_eng: str | None = (
        dpg.get_value("input_name_eng") if dpg.get_value("input_name_eng") else None
    )
    cs: str | None = dpg.get_value("input_cs") if dpg.get_value("input_cs") else None

    if not name_rus and not name_eng and not cs:
        create_error_popup(
            "Ошибка создания записи",
            f"Одно из следующих полей обязательно должно быть заполнено: {'Имя' if user_data == 'doll' else 'ФИО'} на русском или английском{'; позывной' if user_data != 'doll' else ''}",
        )
        return

    if name_eng and has_cyrillic(name_eng):
        create_error_popup(
            "Ошибка создания записи",
            f"Английское {'имя' if user_data == 'doll' else 'ФИО'} не может содержать кирилические символы",
        )
        return

    if name_rus and has_latin(name_rus):
        create_error_popup(
            "Ошибка создания записи",
            f"Русское {'имя' if user_data == 'doll' else 'ФИО'} не может содержать латинские символы",
        )
        return

    sex: str | None = dpg.get_value("input_sex")
    match sex:
        case "Мужской":
            sex = "male"

        case "Женский":
            sex = "female"

        case _:
            create_error_popup(
                "Ошибка создания записи",
                "Ошибка определения пола",
            )
            return

    pob: str | None = dpg.get_value("input_pob") if dpg.get_value("input_pob") else None
    spec: str | None = (
        dpg.get_value("input_spec") if dpg.get_value("input_spec") else None
    )
    goal: str | None = (
        dpg.get_value("input_goal") if dpg.get_value("input_goal") else None
    )
    model: str | None = (
        dpg.get_value("input_model") if dpg.get_value("input_model") else None
    )
    type: str | None = (
        dpg.get_value("input_type") if dpg.get_value("input_type") else None
    )

    anser = 0
    match user_data:
        case "human":
            anser = ServerRequests.create_human(
                nameRus=name_rus,
                nameEng=name_eng,
                cs=cs,
                sex=sex,
                pob=pob,
                specialization=spec,
                goal=goal,
                file_path=img_data_path,
            )
        case "halfhuman":
            if not type:
                create_error_popup(
                    "Ошибка создания записи",
                    "Тип получеловека не был определён",
                )
                return

            anser = ServerRequests.create_halfhuman(
                nameRus=name_rus,
                nameEng=name_eng,
                type=type,
                cs=cs,
                sex=sex,
                pob=pob,
                specialization=spec,
                goal=goal,
                file_path=img_data_path,
            )
        case "doll":
            if type != "M" and type != "T" and type != "A":
                create_error_popup(
                    "Ошибка создания записи",
                    "Ошибка определения типа куклы",
                )
                return

            if not model:
                create_error_popup(
                    "Ошибка создания записи",
                    "Модель куклы не была указана",
                )
                return

            anser = ServerRequests.create_doll(
                nameRus=name_rus,
                nameEng=name_eng,
                type=type,
                model=model,
                sex=sex,
                pob=pob,
                specialization=spec,
                goal=goal,
                file_path=img_data_path,
            )
        case _:
            create_error_popup(
                "Ошибка", "У разраба рак мозга. Как вы сюда вообще попали?"
            )

    anser_status = {
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
    }

    ls_anser = anser_status.get(
        anser,
        ["Ошибка создания записи", f"Неизвестная ошибка от сервера #{anser}"],
    )

    create_error_popup(ls_anser[0], ls_anser[1])
    _on_race_cel(None, user_data, None)
