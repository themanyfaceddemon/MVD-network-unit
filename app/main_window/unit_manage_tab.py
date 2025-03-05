from datetime import UTC, datetime
from typing import Set

import dearpygui.dearpygui as dpg
import pyperclip
from systems import AppConfig, ServerRequests
from tools import TimerManager, ViewportResizeManager, create_error_popup

# Бога тут нет. Нехер сюда смотреть. Это говнокод лютый

SAL_GR = []
COLLAPSE_STATES = {}

RANKS_BY_GROUP = {
    "КГБ": [
        "Директор",
        "Резидент",
        "Спецагент",
        "Майор",
        "Шифровальщик",
        "Смотрящий",
    ],
    "Военная полиция": ["Не указано"],
    "УО FoxHound": [
        "Дозорный",
        "Голос",
        "Крест",
        "Подавитель",
        "Патронаж",
        "Шкурка",
    ],
    "Полиция": [
        "Старший инспектор",
        "Инспектор",
        "Старший сержант",
        "Сержант",
        "Младший сержант",
        "Рядовой",
    ],
    "DEFY": ["Наблюдение"],
    "UMS": ["Наблюдение"],
}

ACCESS_PRESETS = {
    "КГБ": {
        "unit_manage",
        "see_hide_unit",
        "see_user_queue",
        "get_db_data",
        "register_user",
        "change_user_data",
        "delete_user_data",
        "register_user_can_approved",
    },
    "Доверенный сотрудник": {
        "get_db_data",
        "register_user",
        "register_user_can_approved",
    },
    "Базовый сотрудник": {
        "get_db_data",
        "register_user",
    },
    "Сотрудник на испытательном сроке": {
        "get_db_data",
        "register_user",
        "register_user_need_approved",
    },
    "Наблюдатель": {
        "get_db_data",
    },
}

ALL_ACCESS = {
    "unit_manage": [
        "Управление юнитом",
        "Позволяет изменять, создавать и удалять записи пользователей",
        "Предупреждение: Данное право позволяет выдавать себе ЛЮБЫЕ другие права! Оно крайне опасно!",
    ],
    "see_hide_unit": [
        "Просмотр скрытых юнитов",
        "Позволяет видеть юниты, скрытые от обычных пользователей.",
        None,
    ],
    "see_user_queue": [
        "Просмотр чужих запросов в бд",
        "Позволяет видеть чужие запросы в БД.",
        None,
    ],
    "get_db_data": [
        "Просматривать записи в БД",
        "Позволяет просматривать записи в базе данных",
        None,
    ],
    "register_user": [
        "Создавать записи в БД",
        "Позволяет добавлять новые записи в базу данных.",
        None,
    ],
    "change_user_data": [
        "Изменять записи в БД",
        "Позволяет изменять записи в БД",
        None,
    ],
    "delete_user_data": [
        "Удалять записи из БД",
        "Позволяет удалять записи из БД",
        None,
    ],
    "register_user_can_approved": [
        "Одобрять записи в БД",
        "Позволяет подтверждать и одобрять добавленные в базу данные.",
        None,
    ],
    "register_user_need_approved": [
        "Необходимо подтверждение для добавления в бд",
        "Все новые записи должны быть одобрены перед добавлением в базу данных.",
        None,
    ],
}


def create_unit_manage_tab():
    if dpg.does_item_exist("unit_manage_tab"):
        dpg.show_item("unit_manage_tab")
        dpg.set_value("main_tab_bar", "unit_manage_tab")
        return

    with dpg.tab(
        label="Список юнитов",
        parent="main_tab_bar",
        tag="unit_manage_tab",
        closable=True,
        order_mode=dpg.mvTabOrder_Reorderable,
    ):
        with dpg.group(horizontal=True):
            dpg.add_checkbox(
                label="Отображать скрытые",
                default_value=False,
                show=ServerRequests.has_access("see_hide_unit"),
                tag="show_hidden_checkbox",
                callback=_on_hide_toggle,
            )
            dpg.add_text(
                "|",
                show=ServerRequests.has_access("see_hide_unit")
                and ServerRequests.has_access("unit_manage"),
            )
            dpg.add_button(
                label="Создать пользователя",
                callback=_open_cr_window,
                show=ServerRequests.has_access("unit_manage"),
            )
        dpg.add_separator()
        dpg.add_group(tag="unit_manage_group")

    TimerManager.add_timer(
        "rerender_units",
        _render_units,
        AppConfig.server_data_update_time,
    )
    _render_units()
    dpg.set_value("main_tab_bar", "unit_manage_tab")


def _res_cr_window(app_data):
    dpg.set_item_pos(
        "cr_unit_window", [(app_data[2] - 400) * 0.5, (app_data[3] - 200) * 0.5]
    )


def _close_cr_window():
    ViewportResizeManager.remove_callback("cr_unit_window")
    if dpg.does_item_exist("cr_unit_window"):
        dpg.delete_item("cr_unit_window")


def _open_cr_window(sender, app_data, user_data):
    if dpg.does_item_exist("cr_unit_window"):
        _close_cr_window()

    with dpg.window(
        tag="cr_unit_window",
        no_title_bar=True,
        no_move=True,
        no_resize=True,
        height=200,
        width=400,
        pos=[0, 0],
        on_close=_close_cr_window,
    ):
        dpg.add_text("Создание Т.А.В.")
        dpg.add_input_text(
            hint="Введите ФИО/ID КПК сотрудника",
            width=384,
            on_enter=True,
            tag="name_input_fuck_u",
            callback=send_to_create,
        )

        with dpg.group(horizontal=True):
            dpg.add_button(label="Создать", callback=send_to_create)
            dpg.add_button(label="Закрыть", callback=_close_cr_window)

        dpg.add_text("", tag="tav_token", wrap=0, color=AppConfig.attention_color)
        with dpg.popup(dpg.last_item()) as popup:
            dpg.add_button(label="Копировать", user_data=popup, callback=copy_tav_token)

    ViewportResizeManager.add_callback("cr_unit_window", _res_cr_window)


def send_to_create():
    if not dpg.does_item_exist("name_input_fuck_u"):
        return

    name: str | None = dpg.get_value("name_input_fuck_u")
    if not name:
        return

    name = name.strip()
    dpg.set_value("name_input_fuck_u", name)
    anser = ServerRequests.create_unit(name)
    if "registration_token" in anser:
        dpg.set_value("tav_token", anser.get("registration_token"))
    else:
        create_error_popup(
            "Ошибка создания Т.А.В.",
            "Попытка создать одинаковые ID кпк была отклонена сервером",
        )


def copy_tav_token(sender, app_data, user_data):
    if dpg.does_item_exist("tav_token"):
        pyperclip.copy(dpg.get_value("tav_token"))

    if dpg.does_item_exist(user_data):
        dpg.hide_item(user_data)


def _render_units():
    global COLLAPSE_STATES

    if dpg.does_item_exist("unit_manage_group"):
        children = dpg.get_item_children("unit_manage_group", 1)
        if children:
            for child in children:
                if dpg.get_item_type(child) == "mvAppItemType::mvCollapsingHeader":
                    COLLAPSE_STATES[dpg.get_item_label(child)] = dpg.get_value(child)

    users: dict = ServerRequests.get_units()
    grouped_users = {}
    for name, data in users.items():
        group = (
            data.get("user_group") if data.get("user_group") else "Группа не назначена"
        )
        if group not in grouped_users:
            grouped_users[group] = []
        grouped_users[group].append((name, data))

    show_hidden = dpg.get_value("show_hidden_checkbox")
    dpg.delete_item("unit_manage_group", children_only=True)

    sorted_groups = sorted(grouped_users.items(), key=lambda x: x[0])

    for group, units in sorted_groups:
        visible_units = [
            (name, unit)
            for name, unit in units
            if not unit.get("hide", False) or show_hidden
        ]

        if not visible_units:
            continue

        is_open = COLLAPSE_STATES.get(group, False)
        with dpg.collapsing_header(
            label=group,
            parent="unit_manage_group",
            default_open=is_open,
        ):
            sorted_units = sorted(
                visible_units,
                key=lambda x: (x[1].get("user_order") or float("inf"), x[0]),
            )
            for name, data in sorted_units:
                rank = data.get("rank") if data.get("rank") else ""
                fake_name = data.get("fake_name") if data.get("fake_name") else ""
                specialization = (
                    data.get("specialization") if data.get("specialization") else ""
                )
                text_name = (
                    name
                    + (f" ({fake_name})" if fake_name else "")
                    + (": " if rank or specialization else "")
                    + rank
                    + (" | " if rank and specialization else "")
                    + specialization
                )
                dpg.add_text(text_name)
                if not ServerRequests.has_access("unit_manage"):
                    continue

                global RANKS_BY_GROUP

                with dpg.popup(dpg.last_item()):
                    with dpg.group(horizontal=True):
                        dpg.add_text("Изменение")
                        dpg.add_text(name, color=AppConfig.attention_color)
                    dpg.add_separator()

                    if name == "System":
                        dpg.add_text("Изменение системы невозможно")
                        continue

                    dpg.add_checkbox(
                        label="Не показывать по умолчанию?",
                        default_value=bool(data.get("hide")),
                        user_data=name,
                        callback=_on_hide_set,
                        show=ServerRequests.has_access("see_hide_unit"),
                    )

                    dpg.add_input_text(
                        label="Позывной (ложное имя)",
                        default_value=fake_name,
                        user_data=name,
                        callback=_on_fake_name_set,
                        on_enter=True,
                        show=ServerRequests.has_access("see_hide_unit"),
                    )
                    with dpg.tooltip(dpg.last_item()):
                        with dpg.group(horizontal=True):
                            dpg.add_text("Для применения")
                            dpg.add_text("НЕОБХОДИМО", color=AppConfig.attention_color)
                            dpg.add_text("нажать Enter")

                    dpg.add_separator()
                    dpg.add_input_int(
                        label="Зарплата",
                        min_clamped=True,
                        min_value=0,
                        default_value=data.get("salary") if data.get("salary") else 0,
                        user_data=name,
                        callback=_on_salary_set,
                    )

                    dpg.add_separator()

                    available_ranks = RANKS_BY_GROUP.get(
                        data.get("user_group"), ["Не указано"]
                    )
                    rank_id = dpg.add_combo(
                        available_ranks,
                        label="Звание",
                        default_value=rank,
                        user_data=name,
                        callback=_on_rank_set,
                    )
                    dpg.add_combo(
                        list(RANKS_BY_GROUP.keys()),
                        label="Отряд",
                        default_value=data.get("user_group")
                        if data.get("user_group")
                        else "Группа не назначена",
                        user_data=(name, rank_id),
                        callback=lambda sender, app_data, user_data: update_ranks(
                            sender, app_data, user_data, RANKS_BY_GROUP
                        ),
                    )
                    dpg.add_input_text(
                        label="Специализация",
                        default_value=specialization,
                        user_data=name,
                        callback=_on_specialization_set,
                        on_enter=True,
                    )
                    with dpg.tooltip(dpg.last_item()):
                        with dpg.group(horizontal=True):
                            dpg.add_text("Для применения")
                            dpg.add_text("НЕОБХОДИМО", color=AppConfig.attention_color)
                            dpg.add_text("нажать Enter")

                    dpg.add_separator()
                    with dpg.group(horizontal=True):
                        dpg.add_button(
                            label="Удалить запись",
                            user_data=name,
                            callback=_open_del_window,
                        )
                        dpg.add_button(
                            label="Изменить права",
                            user_data=name,
                            callback=_open_access_change_window,
                        )
                        dpg.add_button(
                            label="Подсчёт зарплаты",
                            user_data=name,
                            callback=_open_salary,
                        )


def _res_salary(app_data):
    dpg.set_item_pos(
        "salary_window",
        [(app_data[2] - 700) * 0.5, (app_data[3] - 500) * 0.5],
    )


def _del_salary():
    ViewportResizeManager.remove_callback("salary_window")
    if dpg.does_item_exist("salary_window"):
        dpg.delete_item("salary_window")


def _open_salary(sender, app_data, user_data):
    _del_salary()

    data = ServerRequests.get_unit_info(user_data)
    if not data:
        create_error_popup(
            "Ошибка получения данных",
            "Данные не были отправлены с сервера",
        )
        return

    global SAL_GR
    SAL_GR.clear()

    with dpg.window(
        tag="salary_window",
        no_title_bar=True,
        no_move=True,
        no_resize=True,
        height=500,
        width=700,
        pos=[0, 0],
    ):
        cur_data_w = datetime.now(UTC).strftime("%Y-%W")
        data_to_print = AppConfig.get_game_time().strftime("%Y-%W")
        salary = data.get("salary")
        registration_stats = data.get("registration_stats", [])

        dpg.add_text(f"Текущая неделя: {data_to_print}")
        dpg.add_text(
            f"Текущая базовая зарплата: {salary}", tag="base_salaty", user_data=salary
        )
        entry = next(
            (entry for entry in registration_stats if entry.get("week") == cur_data_w),
            None,
        )

        dpg.add_separator()
        if entry:
            dpg.add_text(
                f"Регистраций в БД за текущую неделю: {entry.get('registrations', 0)}",
                user_data=entry.get("registrations", 0),
                tag="registrations_count",
            )
            dpg.add_text(
                f"Подтверждений в БД за текущую неделю: {entry.get('approvals', 0)}",
                user_data=entry.get("approvals", 0),
                tag="approvals_count",
            )
        else:
            dpg.add_text("Нет данных по работе в БД за текущую неделю")

        dpg.add_separator()
        dpg.add_input_int(
            label="Стоймость 1 регистрации",
            tag="reg_cost",
            min_clamped=True,
            min_value=0,
            default_value=AppConfig.get("reg_cost", 0),
            callback=_sal_ch,
        )
        dpg.add_input_int(
            label="Стоймость 1 подтверждения",
            tag="approv_cost",
            min_clamped=True,
            min_value=0,
            default_value=AppConfig.get("approv_cost", 0),
            callback=_sal_ch,
        )

        dpg.add_separator()
        dpg.add_checkbox(
            label="Не учитывать работу в БД",
            tag="no_db_work",
            callback=_sal_ch,
        )

        dpg.add_separator()
        dpg.add_button(label="Добавить дополнительное поле", callback=_add_fil_sal)
        dpg.add_collapsing_header(label="Дополнительные поля", tag="addi_fil")
        dpg.add_separator()
        dpg.add_text("Для выдачи: ", tag="end_count")
        dpg.add_separator()
        with dpg.group(horizontal=True):
            dpg.add_button(label="Закрыть", callback=_del_salary)
            dpg.add_button(
                label="Скопировать отчёт для discord",
                callback=_dis_copy,
                user_data=user_data,
            )

        _sal_ch()

    ViewportResizeManager.add_callback("salary_window", _res_salary)


def _dis_copy(sender=None, app_data=None, user_data=None):
    no_db_work: bool = dpg.get_value("no_db_work")
    reg_cost: int = AppConfig.get("reg_cost", 0)
    approv_cost: int = AppConfig.get("approv_cost", 0)

    registrations_count = dpg.get_item_user_data("registrations_count") or 0
    approvals_count = dpg.get_item_user_data("approvals_count") or 0

    db_work_end = reg_cost * registrations_count + approv_cost * approvals_count

    count_end = 0
    global SAL_GR
    add_sal = ""
    for groop in SAL_GR:
        if not dpg.does_item_exist(groop):
            SAL_GR.remove(groop)
            continue

        childrens = dpg.get_item_children(groop, 1)
        if not childrens:
            continue

        cost = dpg.get_value(childrens[4]) or 0
        count = dpg.get_value(childrens[5]) or 0
        count_end += cost * count

        reason = dpg.get_item_children(childrens[2], 1)
        if not reason:
            continue

        reason = dpg.get_value(reason[0]) or "Не указано"
        add_sal += f"`{reason}`: `{cost}*{count}={cost * count}`\n"

    base_salary = dpg.get_item_user_data("base_salaty") or 0
    string_to_copy = f"Отчёт о зарплате сотрудника `{user_data}` за неделю {AppConfig.get_game_time().strftime('%Y-%W')}\n"
    string_to_copy += f"Базовая заработная плата: `{base_salary}`\n"
    string_to_copy += (
        f"Учитывается работа в БД: `{'ДА' if not no_db_work else 'НЕТ'}`\n"
    )
    if not no_db_work:
        string_to_copy += f"Количество за регистрацию: `{reg_cost}*{registrations_count}={reg_cost * registrations_count}`\n"
        string_to_copy += f"Количество за подтверждение: `{approv_cost}*{approvals_count}={approv_cost * approvals_count}`\n"
    if add_sal:
        string_to_copy += "\nДополнительные выплаты|штрафы:\n"
        string_to_copy += add_sal

    string_to_copy += (
        f"\n\nОбщая сумма выплаты: {db_work_end + count_end + base_salary}"
    )

    pyperclip.copy(string_to_copy)


def _sal_ch(
    sender=None,
    app_data=None,
    user_data=None,
):
    if sender == "reg_cost":
        AppConfig.set("reg_cost", app_data)
    elif sender == "approv_cost":
        AppConfig.set("approv_cost", app_data)

    no_db_work: bool = dpg.get_value("no_db_work")
    if not no_db_work:
        reg_cost: int = AppConfig.get("reg_cost", 0)
        approv_cost: int = AppConfig.get("approv_cost", 0)

        registrations_count = dpg.get_item_user_data("registrations_count") or 0
        approvals_count = dpg.get_item_user_data("approvals_count") or 0

        db_work_end = reg_cost * registrations_count + approv_cost * approvals_count
    else:
        db_work_end = 0

    count_end = 0
    global SAL_GR
    for groop in SAL_GR:
        if not dpg.does_item_exist(groop):
            SAL_GR.remove(groop)
            continue

        childrens = dpg.get_item_children(groop, 1)
        try:
            cost = dpg.get_value(childrens[4]) or 0  # type: ignore
            count = dpg.get_value(childrens[5]) or 0  # type: ignore
        except Exception:
            continue

        count_end += cost * count

    base_salary = dpg.get_item_user_data("base_salaty") or 0
    dpg.set_value("end_count", f"Для выдачи: {db_work_end + count_end + base_salary}")


def _add_fil_sal():
    global SAL_GR

    with dpg.group(parent="addi_fil") as gr:
        dpg.add_separator()
        dpg.add_separator()
        with dpg.group(horizontal=True):
            dpg.add_input_text(hint="За что надбавка/штраф")
            dpg.add_button(label="X", callback=lambda: dpg.delete_item(gr))

        dpg.add_separator()
        dpg.add_input_int(label="Стоймость", callback=_sal_ch)
        dpg.add_input_int(
            min_clamped=True,
            min_value=0,
            label="Количество",
            callback=_sal_ch,
        )

    SAL_GR.append(gr)
    _sal_ch()


def update_ranks(sender, app_data, user_data, ranks_by_group):
    name, rank_id = user_data
    available_ranks = ranks_by_group.get(app_data, [])

    dpg.configure_item(rank_id, items=available_ranks, default_value="Не указано")
    ServerRequests.update_unit(name, user_group=app_data, rank="Не указано")
    _render_units()


def _on_hide_toggle(sender, app_data):
    _render_units()


def _on_hide_set(sender, app_data, user_data):
    ServerRequests.update_unit(user_data, hide=app_data)
    _render_units()


def _on_salary_set(sender, app_data, user_data):
    ServerRequests.update_unit(user_data, salary=app_data)


def _on_fake_name_set(sender, app_data, user_data):
    ServerRequests.update_unit(user_data, fake_name=app_data)
    _render_units()


def _on_specialization_set(sender, app_data, user_data):
    ServerRequests.update_unit(user_data, specialization=app_data)
    _render_units()


def _on_rank_set(sender, app_data, user_data):
    global RANKS_BY_GROUP

    user_order = 0
    for ranks in RANKS_BY_GROUP.values():
        if app_data in ranks:
            user_order = ranks.index(app_data) + 1
            break

    ServerRequests.update_unit(user_data, rank=app_data, user_order=user_order)
    _render_units()


def _res_del_window(app_data):
    dpg.set_item_pos(
        "del_unit_window",
        [(app_data[2] - 400) * 0.5, (app_data[3] - 200) * 0.5],
    )
    dpg.set_item_pos("del_unit_btns", [(400 - 168) * 0.5, 60])


def _close_del_window():
    ViewportResizeManager.remove_callback("del_unit_window")
    if dpg.does_item_exist("del_unit_window"):
        dpg.delete_item("del_unit_window")


def _open_del_window(sender, app_data, user_data):
    _close_del_window()

    with dpg.window(
        tag="del_unit_window",
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

    ViewportResizeManager.add_callback("del_unit_window", _res_del_window)


def _on_del_conf(sender, app_data, user_data):
    ServerRequests.delete_user(user_data)
    _close_del_window()
    _render_units()


def _res_access_change_window(app_data):
    dpg.set_item_pos(
        "access_change_unit_window",
        [(app_data[2] - 700) * 0.5, (app_data[3] - 500) * 0.5],
    )


def _close_access_change_window():
    ViewportResizeManager.remove_callback("access_change_unit_window")
    if dpg.does_item_exist("access_change_unit_window"):
        dpg.delete_item("access_change_unit_window")


def _open_access_change_window(sender, app_data, user_data):
    _close_access_change_window()

    unit_name = user_data
    access = set(ServerRequests.get_unit_access(unit_name).get("access"))
    with dpg.window(
        tag="access_change_unit_window",
        no_title_bar=True,
        no_move=True,
        no_resize=True,
        height=500,
        width=700,
        pos=[0, 0],
    ):
        preset_names = list(ACCESS_PRESETS.keys()) + ["Кастомный"]
        current_preset = "Кастомный"
        for name, preset_access in ACCESS_PRESETS.items():
            if access == preset_access:
                current_preset = name
                break

        dpg.add_combo(
            tag="preset_combo",
            label="Пресет прав",
            items=preset_names,
            default_value=current_preset,
            callback=_on_preset_selected,
            user_data=unit_name,
        )

        dpg.add_separator()
        with dpg.collapsing_header(label="Ручная настройка прав"):
            for db_access, value in ALL_ACCESS.items():
                _add_ch_box(value[0], value[1], db_access, access, unit_name, value[2])

        dpg.add_separator()
        dpg.add_button(label="Закрыть", callback=_close_access_change_window)

    ViewportResizeManager.add_callback(
        "access_change_unit_window", _res_access_change_window
    )


def _on_preset_selected(sender, app_data, user_data):
    if app_data == "Кастомный":
        return

    new_access = ACCESS_PRESETS.get(app_data, set())
    ServerRequests.update_unit(user_data, access=new_access)
    _open_access_change_window(None, None, user_data)


def _has_access(tag: str, access: Set[str]):
    return tag in access or "all" in access


def _add_ch_box(
    name: str,
    help_text: str,
    access: str,
    user_access: Set[str],
    username: str,
    warning: str | None = None,
):
    dpg.add_checkbox(
        label=name,
        default_value=_has_access(access, user_access),
        user_data=(access, username),
        callback=_on_ch_box,
    )
    with dpg.tooltip(dpg.last_item()):
        dpg.add_text(name)
        dpg.add_separator()
        dpg.add_text(help_text, wrap=400)
        if warning:
            dpg.add_text(warning, wrap=400, color=AppConfig.red_color)


def _on_ch_box(sender, app_data, user_data):
    access, unit_name = user_data
    dpg.set_value("preset_combo", "Кастомный")
    if app_data:
        ServerRequests.add_unit_access(unit_name, access)
    else:
        ServerRequests.remove_unit_access(unit_name, access)
