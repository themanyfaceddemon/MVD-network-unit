from threading import Event, Thread
from typing import Literal

import dearpygui.dearpygui as dpg
import pyperclip
from structures import UserData, get_display_name
from systems import AppConfig, ServerRequests
from tools import ViewportResizeManager, create_popup_window

CUR_USER_DATA: UserData


def create_user_window(user_id: str) -> None:
    global CUR_USER_DATA
    _delete_window()

    try:
        CUR_USER_DATA = UserData(user_id)
        del user_id

    except ValueError:
        create_popup_window(
            "Ошибка получения данных",
            "Сервер не передал данные о выбранном клиенте",
        )
        return

    # region слева сверху окно
    with dpg.window(
        tag="user_window_main_data",
        no_move=True,
        no_resize=True,
        no_title_bar=True,
    ):
        # region Фото фракции
        dpg.add_image(
            f"{CUR_USER_DATA.fraction_raw}_img_logo",
            tag="user_registration_fraction",
        )
        if ServerRequests.has_access("fraction_control"):
            _image_ch(dpg.last_item())
        # endregion

        # region ФИО
        with dpg.table(
            tag="user_window_main_data_ind_table",
            borders_innerH=True,
            borders_innerV=True,
            borders_outerH=True,
            borders_outerV=True,
            header_row=True,
        ):
            dpg.add_table_column(label="ФИО (Rus)")
            dpg.add_table_column(label="ФИО (Eng)")
            dpg.add_table_column(label="Позывной")

            with dpg.table_row():
                dpg.add_text(CUR_USER_DATA.name_rus, wrap=0)
                _ch_text(dpg.last_item(), _ch_name_rus, "")

                dpg.add_text(CUR_USER_DATA.name_eng, wrap=0)
                _ch_text(dpg.last_item(), _ch_name_eng, "")

                dpg.add_text(CUR_USER_DATA.name_cs, wrap=0)
                _ch_text(dpg.last_item(), _ch_name_cs, "")
        # endregion

        # region Базовая физическая информация
        with dpg.group(horizontal=True):
            with dpg.group():
                dpg.add_text(f"Раса: {CUR_USER_DATA.race}", tag="user_data_race")
                _ch_combo(
                    dpg.last_item(),
                    ["Человек", "Полу-человек", "Кукла"],
                    CUR_USER_DATA.race,
                    _ch_race,
                )

                if CUR_USER_DATA.race_raw != "human":
                    dpg.add_text(f"Тип: {CUR_USER_DATA.user_type}")
                    _ch_text(dpg.last_item(), _ch_user_type, "Тип: ")

                    if CUR_USER_DATA.race_raw == "doll":
                        dpg.add_text(f"Модель: {CUR_USER_DATA.model}")
                        _ch_text(dpg.last_item(), _ch_model, "Модель: ")

            dpg.add_text("|")

            with dpg.group():
                with dpg.group(horizontal=True):
                    dpg.add_text("Пол:")
                    dpg.add_text(
                        CUR_USER_DATA.sex,
                        color=CUR_USER_DATA.sex_color,
                        tag="user_data_sex",
                    )
                    _ch_combo(
                        dpg.last_item(),
                        ["Женский", "Мужской"],
                        CUR_USER_DATA.sex,
                        _ch_sex,
                    )

        dpg.add_text("------")

        with dpg.group(horizontal=True):
            dpg.add_text("Статус:")
            dpg.add_text(
                CUR_USER_DATA.status,
                color=CUR_USER_DATA.status_color,
                tag="user_data_status",
            )
            _ch_combo(
                dpg.last_item(),
                CUR_USER_DATA.list_status,
                CUR_USER_DATA.status,
                _ch_status,
            )
        # endregion

        # region UUID
        with dpg.group(horizontal=True, tag="uuid_user_group"):
            dpg.add_text("UUID:")
            dpg.add_text(
                CUR_USER_DATA.user_uuid.partition("-")[0] + "...",
                color=AppConfig.uuid_color,
            )

        dpg.add_button(
            label="Скопировать",
            tag="uuid_user_copy_btn",
            callback=lambda: pyperclip.copy(CUR_USER_DATA.user_uuid),
        )
        # endregion
    # endregion

    # region слева снизу окно
    with dpg.window(
        tag="user_window_submain_data",
        no_move=True,
        no_resize=True,
        no_title_bar=True,
    ):
        item_lists = []

        if "link_dolls" in CUR_USER_DATA.additional_info:
            item_lists.append("Связанные куклы")

        if "link_owners" in CUR_USER_DATA.additional_info:
            item_lists.append("Командиры куклы")

        if item_lists:
            dpg.add_combo(
                item_lists,
                callback=_select_add_info,
                default_value=item_lists[0],
                user_data=CUR_USER_DATA,
            )
            _select_add_info(None, item_lists[0], CUR_USER_DATA)
            dpg.add_group(tag="user_add_info")

        else:
            dpg.add_text("Дополнительных данных к записи не было обнаружено.", wrap=0)

        with dpg.group(horizontal=True, tag="user_windows_control_btn"):
            dpg.add_button(label="Закрыть", callback=_delete_window)
            dpg.add_button(
                label="Удалить запись",
                callback=_open_del_window,
                user_data=CUR_USER_DATA.user_uuid,
                show=ServerRequests.has_access("delete_user_data"),
            )
    # endregion

    # region Окно изображения
    with dpg.window(
        tag="user_window_image_data",
        no_move=True,
        no_resize=True,
        no_title_bar=True,
    ):
        dpg.add_text("Колёсико мыши - просматривать по вертикали", wrap=0)
        dpg.add_text("Shift + колёсико мыши - просмотра по горизонтали", wrap=0)

        with dpg.child_window(
            auto_resize_x=True,
            auto_resize_y=True,
            horizontal_scrollbar=True,
            tag="user_window_image_data_child_window",
        ):
            with dpg.group(horizontal=True):
                dpg.add_text("Изображение загружается...")
                dpg.add_loading_indicator(
                    color=AppConfig.red_color,
                    secondary_color=AppConfig.attention_color,
                    radius=1.5,
                    circle_count=10,
                )

    load_image(CUR_USER_DATA.user_uuid)
    # endregion

    ViewportResizeManager.add_callback("user_window", _resize_callback)


# region Для доп инфы колбеки
def _select_add_info(sender, app_data, user_data) -> None:
    dpg.delete_item("user_add_info", children_only=True)

    func = {
        "Связанные куклы": _link_dolls,
        "Командиры куклы": _link_owners,
    }.get(app_data, None)

    if func:
        func(user_data)


# region Куклы и овнеры
def _link_dolls(user_data: UserData) -> None:
    _temlp_links(
        user_data,
        "link_dolls",
        "Информация по связанным куклам не была обнаружена",
        lambda s, a, u: _unlinck_doll_owner("doll", u),
    )


def _link_owners(user_data: UserData) -> None:
    _temlp_links(
        user_data,
        "link_owners",
        "Информация по командирам куклы не была обнаружена",
        lambda s, a, u: _unlinck_doll_owner("owner", u),
    )


def _temlp_links(
    user_data: UserData,
    dict_key: str,
    str_if_dict_key_none: str,
    unlinck_func,
) -> None:
    dict_users = user_data.additional_info.get(dict_key)

    if not dict_users:
        dpg.add_text(
            str_if_dict_key_none,
            parent="user_add_info",
        )
        return

    dict_users = dict_users.split(",")
    for user in dict_users:
        if not user:
            continue

        with dpg.group(horizontal=True, parent="user_add_info"):
            dpg.add_button(
                label=get_display_name(ServerRequests.get_user_names(user)),
                callback=lambda: create_user_window(user),
            )
            dpg.add_button(
                label="X", callback=unlinck_func, user_data=(user, user_data)
            )


def _unlinck_doll_owner(
    type: Literal["doll", "owner"],
    user_data: tuple[str, UserData],
):
    match type:
        case "doll":
            ServerRequests.remove_doll_reg(user_data[1].user_uuid, user_data[0])

        case "owner":
            ServerRequests.remove_doll_reg(user_data[0], user_data[1].user_uuid)


# endregion


# endregion


# region Паралельная загрузка изображения через отдельный тред
_current_thread = None
_stop_event = Event()


def load_image(user_id: str):
    global _current_thread, _stop_event

    if _current_thread and _current_thread.is_alive():
        _stop_event.set()
        _current_thread.join()
        _stop_event.clear()

    _stop_event.clear()
    _current_thread = Thread(
        target=_thread_load_image,
        args=(user_id, _stop_event),
        daemon=True,
    )
    _current_thread.start()


def _thread_load_image(user_id: str, stop_flag: Event):
    photo_path = ServerRequests.get_image(user_id)

    if stop_flag.is_set() or not photo_path:
        return

    width, height, _, data = dpg.load_image(str(photo_path))
    with dpg.texture_registry():
        dpg.add_static_texture(width, height, data, tag="user_registration_image")

    if dpg.does_item_exist("user_window_image_data_child_window"):
        dpg.delete_item("user_window_image_data_child_window", children_only=True)
        if dpg.does_item_exist("user_registration_image"):
            dpg.add_image(
                "user_registration_image", parent="user_window_image_data_child_window"
            )
        else:
            dpg.add_text(
                "Изображение не обнаружено",
                parent="user_window_image_data_child_window",
            )
    else:
        if dpg.does_item_exist("user_registration_image"):
            dpg.delete_item("user_registration_image")

    stop_flag.clear()


# endregion


# region Изменение данных
def _image_ch(parent: str | int) -> None:
    global CUR_USER_DATA

    list_combo = [
        "Белое небо",
        "Бармен",
        "DEFY",
        "Наёмник",
        "МВД",
        "Raptor Technology",
        "Sangvis Ferri",
        "Svarog Heavy Industries",
        "Unity Medical Services",
    ]

    with dpg.popup(parent) as gr:
        dpg.add_text("Смена фракции:")
        dpg.add_combo(
            list_combo,
            callback=_fraction_ch,
            default_value=CUR_USER_DATA.fraction,
            user_data=gr,
        )


def _fraction_ch(sender, app_data, user_data):
    global CUR_USER_DATA

    match app_data:
        case "Белое небо":
            CUR_USER_DATA.additional_info["fraction"] = "ws"
            code = ServerRequests.chenge_fraction(CUR_USER_DATA.user_uuid, "ws")

        case "Бармен":
            CUR_USER_DATA.additional_info["fraction"] = "bartender"
            code = ServerRequests.chenge_fraction(CUR_USER_DATA.user_uuid, "bartender")

        case "DEFY":
            CUR_USER_DATA.additional_info["fraction"] = "deffy"
            code = ServerRequests.chenge_fraction(CUR_USER_DATA.user_uuid, "deffy")

        case "Наёмник":
            CUR_USER_DATA.additional_info["fraction"] = "mercenary"
            code = ServerRequests.chenge_fraction(CUR_USER_DATA.user_uuid, "mercenary")

        case "МВД":
            CUR_USER_DATA.additional_info["fraction"] = "mvd"
            code = ServerRequests.chenge_fraction(CUR_USER_DATA.user_uuid, "mvd")

        case "Raptor Technology":
            CUR_USER_DATA.additional_info["fraction"] = "raptor"
            code = ServerRequests.chenge_fraction(CUR_USER_DATA.user_uuid, "raptor")

        case "Sangvis Ferri":
            CUR_USER_DATA.additional_info["fraction"] = "sf"
            code = ServerRequests.chenge_fraction(CUR_USER_DATA.user_uuid, "sf")

        case "Svarog Heavy Industries":
            CUR_USER_DATA.additional_info["fraction"] = "svarog"
            code = ServerRequests.chenge_fraction(CUR_USER_DATA.user_uuid, "svarog")

        case "Unity Medical Services":
            CUR_USER_DATA.additional_info["fraction"] = "ums"
            code = ServerRequests.chenge_fraction(CUR_USER_DATA.user_uuid, "ums")

        case _:
            code = 404

    if code == 200:
        dpg.delete_item("user_registration_fraction")
        dpg.delete_item(user_data)
        dpg.add_image(
            f"{CUR_USER_DATA.fraction_raw}_img_logo",
            tag="user_registration_fraction",
            parent="user_window_main_data",
        )
        if ServerRequests.has_access("fraction_control"):
            _image_ch(dpg.last_item())
        ViewportResizeManager.invoke()

    else:
        create_popup_window(
            "Ошибка обновления фракции", f"Фракция не была изменена. Код ошибки: {code}"
        )


# region смена текста
def _ch_text(parent: str | int, callback, add_to_tag: str | int) -> None:
    with dpg.popup(parent) as gr:
        dpg.add_text("Смена значений:")
        dpg.add_input_text(
            on_enter=True,
            callback=callback,
            user_data=(gr, add_to_tag, parent),
        )


# Похорошему надо сделать один метод, а не 500 методов
def _ch_name_rus(sender, app_data, user_data) -> None:
    CUR_USER_DATA._name_rus = app_data
    ServerRequests.change_user_data(CUR_USER_DATA.user_uuid, name_rus=app_data)
    if not app_data:
        app_data = "Не указано"

    dpg.set_value(user_data[2], f"{user_data[1]}{app_data}")
    dpg.hide_item(user_data[0])


def _ch_name_eng(sender, app_data, user_data) -> None:
    CUR_USER_DATA._name_eng = app_data
    ServerRequests.change_user_data(CUR_USER_DATA.user_uuid, name_eng=app_data)
    if not app_data:
        app_data = "Не указано"

    dpg.set_value(user_data[2], f"{user_data[1]}{app_data}")
    dpg.hide_item(user_data[0])


def _ch_name_cs(sender, app_data, user_data) -> None:
    CUR_USER_DATA._name_cs = app_data
    ServerRequests.change_user_data(CUR_USER_DATA.user_uuid, name_cs=app_data)
    if not app_data:
        app_data = "Не указано"

    dpg.set_value(user_data[2], f"{user_data[1]}{app_data}")
    dpg.hide_item(user_data[0])


def _ch_user_type(sender, app_data, user_data) -> None:
    CUR_USER_DATA._user_type = app_data
    ServerRequests.change_user_data(CUR_USER_DATA.user_uuid, user_type=app_data)
    if not app_data:
        app_data = "Не указано"

    dpg.set_value(user_data[2], f"{user_data[1]}{app_data}")
    dpg.hide_item(user_data[0])


def _ch_model(sender, app_data, user_data) -> None:
    CUR_USER_DATA._model = app_data
    ServerRequests.change_user_data(CUR_USER_DATA.user_uuid, model=app_data)
    if not app_data:
        app_data = "Не указано"

    dpg.set_value(user_data[2], f"{user_data[1]}{app_data}")
    dpg.hide_item(user_data[0])


# endregion


def _ch_combo(
    parent: str | int,
    list_of_values: list[str],
    default_value: str,
    callback,
):
    with dpg.popup(parent) as gr:
        dpg.add_text("Смена значений:")
        dpg.add_combo(
            list_of_values,
            default_value=default_value,
            callback=callback,
            user_data=gr,
        )


def _ch_race(sender, app_data, user_data) -> None:
    global CUR_USER_DATA

    match app_data:
        case "Человек":
            CUR_USER_DATA._race = "human"
            code = ServerRequests.change_user_data(
                CUR_USER_DATA.user_uuid, race="human"
            )

        case "Полу-человек":
            CUR_USER_DATA._race = "halfhuman"
            code = ServerRequests.change_user_data(
                CUR_USER_DATA.user_uuid, race="halfhuman"
            )

        case "Кукла":
            CUR_USER_DATA._race = "doll"
            code = ServerRequests.change_user_data(CUR_USER_DATA.user_uuid, race="doll")

        case _:
            code = 404

    if code != 200:
        create_popup_window(
            "Ошибка смены данных", f"Ошибка смены данных. Код ошибки: {code}"
        )
        return
    else:
        # бубубу. Я заебалась работать. Пойду обнову выкачу.
        create_popup_window(
            "Успешно",
            "Данные успешно обновлены. Для обновления интерфейса просьба перезапросить информацию",
        )

    dpg.set_value("user_data_race", f"Раса: {CUR_USER_DATA.race}")
    dpg.hide_item(user_data)


def _ch_sex(sender, app_data, user_data) -> None:
    global CUR_USER_DATA

    match app_data:
        case "Женский":
            CUR_USER_DATA._sex = "female"
            code = ServerRequests.change_user_data(
                CUR_USER_DATA.user_uuid, sex="female"
            )

        case "Мужской":
            CUR_USER_DATA._sex = "male"
            code = ServerRequests.change_user_data(CUR_USER_DATA.user_uuid, sex="male")

        case _:
            code = 404

    if code != 200:
        create_popup_window(
            "Ошибка смены данных", f"Ошибка смены данных. Код ошибки: {code}"
        )
        return

    dpg.set_value("user_data_sex", CUR_USER_DATA.sex)
    dpg.configure_item("user_data_sex", color=CUR_USER_DATA.sex_color)
    dpg.hide_item(user_data)


def _ch_status(sender, app_data, user_data) -> None:
    global CUR_USER_DATA

    match app_data:
        case "Жив":
            CUR_USER_DATA._status = "alive"
            code = ServerRequests.change_user_data(
                CUR_USER_DATA.user_uuid, status="alive"
            )
        case "Жива":
            CUR_USER_DATA._status = "alive"
            code = ServerRequests.change_user_data(
                CUR_USER_DATA.user_uuid, status="alive"
            )

        case "Мёртв":
            CUR_USER_DATA._status = "dead"
            code = ServerRequests.change_user_data(
                CUR_USER_DATA.user_uuid, status="dead"
            )
        case "Мертва":
            CUR_USER_DATA._status = "dead"
            code = ServerRequests.change_user_data(
                CUR_USER_DATA.user_uuid, status="dead"
            )

        case "Пропал без вести":
            CUR_USER_DATA._status = "missing"
            code = ServerRequests.change_user_data(
                CUR_USER_DATA.user_uuid, status="missing"
            )
        case "Пропала без вести":
            CUR_USER_DATA._status = "missing"
            code = ServerRequests.change_user_data(
                CUR_USER_DATA.user_uuid, status="missing"
            )

        case "На проверке":
            CUR_USER_DATA._status = "on_review"
            code = ServerRequests.change_user_data(
                CUR_USER_DATA.user_uuid, status="on_review"
            )
        case "На проверке":
            CUR_USER_DATA._status = "on_review"
            code = ServerRequests.change_user_data(
                CUR_USER_DATA.user_uuid, status="on_review"
            )

        case _:
            code = 404

    if code != 200:
        create_popup_window(
            "Ошибка смены данных", f"Ошибка смены данных. Код ошибки: {code}"
        )
        return

    dpg.set_value("user_data_status", CUR_USER_DATA.status)
    dpg.configure_item("user_data_status", color=CUR_USER_DATA.status_color)
    dpg.hide_item(user_data)


# endregion


# region Ресайз и чистка
def _resize_callback(app_data):
    item_width: float = app_data[2] * 0.5
    round_item_width = round(item_width)
    item_height: float = app_data[3] * 0.5
    round_item_height = round(item_height)

    # region user_window_main_data
    dpg.set_item_pos("user_window_main_data", [0, 0])
    dpg.set_item_width("user_window_main_data", round_item_width)
    dpg.set_item_height("user_window_main_data", round_item_height)

    dpg.set_item_width(
        "user_window_main_data_ind_table", round(round_item_width * 0.75)
    )

    user_registration_fraction_size = round(round_item_width * 0.2)
    dpg.set_item_pos("user_registration_fraction", [round_item_width * 0.78, 8])
    dpg.set_item_width("user_registration_fraction", user_registration_fraction_size)
    dpg.set_item_height("user_registration_fraction", user_registration_fraction_size)

    dpg.set_item_pos("uuid_user_group", [8, item_height - 30])

    dpg.set_item_pos("uuid_user_copy_btn", [item_width - 115, item_height - 30])
    # endregion

    # user_window_submain_data
    dpg.set_item_pos("user_window_submain_data", [0, item_height])
    dpg.set_item_width("user_window_submain_data", round_item_width)
    dpg.set_item_height("user_window_submain_data", round_item_height)

    dpg.set_item_pos("user_windows_control_btn", [8, item_height - 30])

    # user_window_image_data
    dpg.set_item_pos("user_window_image_data", [item_width, 0])
    dpg.set_item_width("user_window_image_data", round_item_width)
    dpg.set_item_height("user_window_image_data", app_data[3])


def _delete_window():
    ViewportResizeManager.remove_callback("user_window")
    for tag in [
        "user_window_main_data",
        "user_window_submain_data",
        "user_window_image_data",
        "user_registration_image",
    ]:
        if dpg.does_item_exist(tag):
            dpg.delete_item(tag)


# endregion


# region Поддтверждение удаления пользователя (надо будет вынести всё в отдельный конструктор)
def _res_del_window(app_data):
    dpg.set_item_pos(
        "del_user_window",
        [(app_data[2] - 400) * 0.5, (app_data[3] - 200) * 0.5],
    )
    dpg.set_item_pos("del_unit_btns", [(400 - 168) * 0.5, 60])


def _close_del_window():
    ViewportResizeManager.remove_callback("del_user_window")
    if dpg.does_item_exist("del_user_window"):
        dpg.delete_item("del_user_window")


def _open_del_window(sender, app_data, user_data):
    _close_del_window()

    with dpg.window(
        tag="del_user_window",
        no_title_bar=True,
        no_move=True,
        no_resize=True,
        height=200,
        width=400,
        pos=[0, 0],
    ):
        dpg.add_text("Вы точно хотите удалить эту запись?")
        with dpg.group(horizontal=True):
            dpg.add_text("Данную операцию")
            dpg.add_text("невозможно", color=AppConfig.attention_color)
            dpg.add_text("будет откатить")

        with dpg.group(horizontal=True, tag="del_unit_btns"):
            dpg.add_button(
                label="Да",
                callback=_on_del_conf,
                user_data=user_data,
                width=80,
            )
            dpg.add_button(label="Нет", callback=_close_del_window, width=80)

    ViewportResizeManager.add_callback("del_user_window", _res_del_window)


def _on_del_conf(sender, app_data, user_data):
    ServerRequests.delete_user(user_data)
    _close_del_window()
    code = ServerRequests.delete_user_data(user_data)
    if code == 200:
        _delete_window()


# endregion
