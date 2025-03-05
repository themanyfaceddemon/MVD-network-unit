import dearpygui.dearpygui as dpg
from systems import AppConfig, ServerRequests
from tools import TimerManager, ViewportResizeManager, create_error_popup


def create_approve_tab():
    if dpg.does_item_exist("approve_tab"):
        dpg.show_item("approve_tab")
        dpg.set_value("main_tab_bar", "approve_tab")
        return

    with dpg.tab(
        label="Подтверждение запросов",
        parent="main_tab_bar",
        tag="approve_tab",
        closable=True,
        order_mode=dpg.mvTabOrder_Reorderable,
    ):
        dpg.add_button(label="Синхронизация", callback=_update_approve_all)
        with dpg.child_window(
            autosize_x=True,
            autosize_y=True,
            tag="approve_all",
        ):
            pass

    TimerManager.add_timer(
        "update_approve_all",
        _update_approve_all,
        AppConfig.server_data_update_time,
    )
    _update_approve_all()

    dpg.set_value("main_tab_bar", "approve_tab")


def _update_approve_all(sender=None, app_data=None):
    dpg.delete_item("approve_all", children_only=True)
    answer = ServerRequests.get_need_approved()
    if not answer:
        return

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
        return " / ".join(parts) or "Без имени"

    items = [(get_display_name(item.get("data")), item) for item in answer]

    if not items:
        dpg.add_text("По вашему запросу ничего не найдено", parent="approve_all")
        return

    with dpg.table(
        parent="approve_all",
        header_row=False,
        policy=dpg.mvTable_SizingStretchSame,
        resizable=False,
        borders_innerV=True,
        borders_outerV=True,
        borders_outerH=True,
        borders_innerH=True,
    ):
        dpg.add_table_column()
        dpg.add_table_column()
        dpg.add_table_column()

        for i in range(0, len(items), 3):
            with dpg.table_row():
                for item in items[i : i + 3]:
                    dpg.add_button(
                        label=item[0],
                        user_data=item[1],
                        callback=lambda s, d, u: _create_user_window(u),
                    )


def _create_user_window(user_data: dict) -> None:
    _del()
    apr_data: dict = user_data.get("data")  # type: ignore

    name_rus = apr_data.get("nameRus") or None
    name_eng = apr_data.get("nameEng") or None
    cs = apr_data.get("cs") or None

    race = user_data.get("user_table") or None
    pob = apr_data.get("pob") or None
    goal = apr_data.get("goal") or None
    type = apr_data.get("type") or None
    model = apr_data.get("model") or None
    specialization = apr_data.get("specialization") or None

    photo_file = apr_data.get("file_path")
    photo_path = ServerRequests.get_image(photo_file)

    if photo_path:
        width, height, _, data = dpg.load_image(str(photo_path))
        with dpg.texture_registry():
            dpg.add_static_texture(width, height, data, tag="apr_texture")

    sex = "Мужской" if apr_data.get("sex") == "male" else "Женский"

    with dpg.window(
        tag="approve_window",
        no_move=True,
        no_resize=True,
        no_collapse=True,
        pos=[0, 0],
    ):
        with dpg.table(
            header_row=True,
            policy=dpg.mvTable_SizingStretchSame,
            resizable=False,
            borders_innerV=True,
            borders_outerV=True,
            borders_outerH=True,
            borders_innerH=True,
        ):
            dpg.add_table_column(label="Имя (RUS):" if race == "doll" else "ФИО (RUS):")
            dpg.add_table_column(label="Имя (ENG):" if race == "doll" else "ФИО (ENG):")
            dpg.add_table_column(label="Позывной:")
            with dpg.table_row():
                dpg.add_text(name_rus if name_rus else "Отсутствует")
                dpg.add_text(name_eng if name_eng else "Отсутствует")
                dpg.add_text(cs if cs else "Отсутствует")

        with dpg.group(horizontal=True):
            tr_race = {
                "doll": "Кукла",
                "human": "Человек",
                "halfhuman": "Полу-человек",
            }
            dpg.add_text("Раса:")
            dpg.add_text(tr_race.get(race, "ERROR"))  # type: ignore

        if race != "human":
            with dpg.group(horizontal=True):
                dpg.add_text("Тип куклы:" if race == "doll" else "Тип полулюда:")
                dpg.add_text(type if type else "Не указано")

        if race == "doll":
            with dpg.group(horizontal=True):
                dpg.add_text("Модель:")
                dpg.add_text(model if model else "Не указано")

        dpg.add_separator()
        with dpg.group(horizontal=True):
            dpg.add_text("Пол:")
            dpg.add_text(
                sex,
                color=AppConfig.female_color
                if sex == "Женский"
                else AppConfig.male_color,
            )

        dpg.add_separator()
        with dpg.group(horizontal=True):
            dpg.add_text("Место производства:" if race == "doll" else "Место рождения:")
            dpg.add_text(pob if pob else "Отсутствует")

        with dpg.group(horizontal=True):
            dpg.add_text("Цель в секторе:")
            dpg.add_text(goal if goal else "Отсутствует")

        with dpg.group(horizontal=True):
            dpg.add_text("Специализация:")
            dpg.add_text(specialization if specialization else "Отсутствует")

        dpg.add_separator()
        if photo_path:
            with dpg.collapsing_header(label="Изображение"):
                dpg.add_image("apr_texture")
        else:
            dpg.add_text("Изображение не обнаружено")

        dpg.add_button(
            label="Принять заявку в БД", user_data=user_data.get("id"), callback=_apr
        )
        dpg.add_button(
            label="Отклонить заявку в БД", user_data=user_data.get("id"), callback=_reg
        )

    ViewportResizeManager.add_callback("approve_window", _res)


def _apr(sender, app_data, user_data):
    anser = ServerRequests.approve_queue(user_data, True)
    if anser == 200:
        create_error_popup("Успешно", "Заявка успешно подтверждена")
        _del()
        _update_approve_all()
    else:
        create_error_popup("Ошибка", f"Сервер словил неизветсную ошибку {anser}")


def _reg(sender, app_data, user_data):
    if not dpg.does_item_exist("_reg_aprv"):
        with dpg.window(
            modal=True,
            no_collapse=True,
            no_move=True,
            no_resize=True,
            no_close=True,
            label="Укажите причину",
            tag="_reg_aprv",
            pos=[0, 0],
        ):
            dpg.add_text("Укажите причину отказа заявки, и нажмите на Enter", wrap=0)
            dpg.add_input_text(
                hint="Причина отклонения заявки",
                on_enter=True,
                callback=_del_item_p,
                user_data=user_data,
            )
            dpg.add_button(label="Отмена", callback=_del_p)

        ViewportResizeManager.add_callback("_reg_aprv", _res_p)
        dpg.focus_item("_reg_aprv")


def _res_p(app_data):
    dpg.set_item_width("_reg_aprv", app_data[2] * 0.5)
    dpg.set_item_height("_reg_aprv", app_data[3] * 0.5)
    dpg.set_item_pos(
        "_reg_aprv",
        [
            (app_data[2] - app_data[2] * 0.5) * 0.5,
            (app_data[3] - app_data[3] * 0.5) * 0.5,
        ],
    )


def _del_p():
    ViewportResizeManager.remove_callback("_reg_aprv")

    if dpg.does_item_exist("_reg_aprv"):
        dpg.delete_item("_reg_aprv")


def _del_item_p(sender, app_data, user_data):
    anser = ServerRequests.approve_queue(user_data, False, app_data)
    if anser == 200:
        create_error_popup("Успешно", "Заявка успешно отклонена")
        _del()
        _update_approve_all()
    else:
        create_error_popup("Ошибка", f"Сервер словил неизветсную ошибку {anser}")

    _del_p()


def _res(app_data):
    dpg.set_item_width("approve_window", app_data[2])
    dpg.set_item_height("approve_window", app_data[3])


def _del():
    ViewportResizeManager.remove_callback("approve_window")

    if dpg.does_item_exist("approve_window"):
        dpg.delete_item("approve_window")

    if dpg.does_item_exist("apr_texture"):
        dpg.delete_item("apr_texture")
