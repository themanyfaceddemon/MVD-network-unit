import dearpygui.dearpygui as dpg
from systems import AppConfig, ServerRequests
from tools import ViewportResizeManager, create_popup_window

from app.main_window import AppMainWindow


class AuthWindow:
    @classmethod
    def init(cls):
        if AppConfig.get("remember_login", False):
            cls._on_login_btn_click(
                None,
                None,
                [
                    AppConfig.get("remember_login_value", ""),
                    AppConfig.get("remember_password_value", ""),
                ],
            )
        else:
            cls._create_login_window()

    @classmethod
    def _del_and_enter(cls):
        cls._del_login_callback()
        cls._del_tae_callback()
        AppMainWindow.init()
        dpg.set_item_label("auth_username", ServerRequests.cur_username)

    @classmethod
    def _del_login_callback(cls):
        if dpg.does_item_exist("login_window"):
            dpg.delete_item("login_window")

        ViewportResizeManager.remove_callback("login_window")

    @classmethod
    def _res_login_callback(cls, app_data) -> None:
        dpg.set_item_pos("main_auth_header", [(app_data[2] - 171) * 0.5, 8])

        center_input_text = (app_data[2] - 408) * 0.5
        center_btn = (app_data[2] - 208) * 0.5
        dpg.set_item_pos("intput_text_auth_login", [center_input_text, 48])
        dpg.set_item_pos("intput_text_auth_password", [center_input_text, 78])
        dpg.set_item_pos("remember_login", [(app_data[2] - 195) * 0.5, 108])
        dpg.set_item_pos("login_btns", [center_btn, 138])

        dpg.set_item_pos("login_logo", [(app_data[2] - 256) * 0.5, 228])

    @classmethod
    def _create_login_window(cls):
        with dpg.window(
            pos=(0, 0),
            no_move=True,
            no_resize=True,
            no_title_bar=True,
            tag="login_window",
            on_close=cls._del_login_callback,
        ):
            dpg.set_primary_window("login_window", True)
            dpg.add_text("М.В.Д. network unit", tag="main_auth_header")
            dpg.add_input_text(
                hint="ID кпк",
                tag="intput_text_auth_login",
                width=408,
                on_enter=True,
                callback=lambda: dpg.focus_item("intput_text_auth_password"),
            )
            dpg.add_input_text(
                hint="Пароль",
                tag="intput_text_auth_password",
                password=True,
                width=408,
                on_enter=True,
                callback=cls._on_login_btn_click,
            )
            with dpg.group(tag="login_btns"):
                dpg.add_button(
                    label="Войти",
                    width=208,
                    callback=cls._on_login_btn_click,
                )
                dpg.add_button(
                    label="Использовать Т.А.В.",
                    width=208,
                    callback=cls._create_tae_window,
                )

            dpg.add_checkbox(
                label="Автоматический вход",
                tag="remember_login",
                default_value=AppConfig.get("remember_login", False),
                callback=lambda s, a, u: AppConfig.set("remember_login", a),
            )
            with dpg.tooltip(dpg.last_item()):
                dpg.add_text("Автоматически входит в систему")

            dpg.add_image("mvd_img_logo", tag="login_logo")
            ViewportResizeManager.add_callback("login_window", cls._res_login_callback)

    @classmethod
    def _on_login_btn_click(cls, sender, app_data, user_data) -> None:
        if sender is None:
            code = ServerRequests.login(user_data[0].strip(), user_data[1].strip())
            if code == 200:
                cls._del_and_enter()
            else:
                AppConfig.set("remember_login", False)
                AppConfig.pop("remember_login_value")
                AppConfig.pop("remember_password_value")
                cls._create_login_window()

            return

        login: str = dpg.get_value("intput_text_auth_login")
        password: str = dpg.get_value("intput_text_auth_password")

        if login.startswith("CREATE-AUTH-"):
            create_popup_window(
                "Ошибка авторизации",
                "Вы использовали Т.А.В в качестве КПК ID",
            )
            return

        code = ServerRequests.login(login.strip(), password.strip())
        if code == 200:
            if AppConfig.get("remember_login", False):
                AppConfig.set("remember_login_value", login)
                AppConfig.set("remember_password_value", password)
            cls._del_and_enter()
            return

        error_msg = {
            429: "Слишком много попыток авторизации. Повторите попытку позже",
            426: "Версия вашего MVD network unit устарела. Утановите/запросите новую версию",
            401: "ID КПК или пароль введены неверно",
            400: "ID КПК или пароль не были введены",
        }.get(
            code,
            f"Сервер вернул неизвестную ошибку #{code}. Просьба связаться со старшими сотрудниками МВД для решения проблемы",
        )

        create_popup_window("Ошибка авторизации", error_msg)

    @classmethod
    def _del_tae_callback(cls):
        if dpg.does_item_exist("tae_window"):
            dpg.delete_item("tae_window")

        ViewportResizeManager.remove_callback("tae_window")

    @classmethod
    def _res_tae_callback(cls, app_data):
        dpg.set_item_width("tae_window", app_data[2])
        dpg.set_item_height("tae_window", app_data[3])

        dpg.set_item_pos("main_tae_header", [(app_data[2] - 216) * 0.5, 8])

        center = (app_data[2] - 408) * 0.5
        dpg.set_item_pos("tae_token_input_text", [center, 48])
        dpg.set_item_pos("tae_password_1_input_text", [center, 78])
        dpg.set_item_pos("tae_password_2_input_text", [center, 108])
        dpg.set_item_pos("tae_btns", [center, 148])

        dpg.set_item_pos("tae_logo", [(app_data[2] - 256) / 2, 228])

    @classmethod
    def _create_tae_window(cls):
        with dpg.window(
            pos=(0, 0),
            no_move=True,
            no_resize=True,
            no_title_bar=True,
            tag="tae_window",
            on_close=cls._del_login_callback,
        ):
            dpg.add_text("Авторизация через Т.А.В.", tag="main_tae_header")
            with dpg.tooltip("main_tae_header"):
                dpg.add_text("ПКМ для более подробной информации")

            with dpg.popup("main_tae_header"):
                with dpg.group(horizontal=True):
                    dpg.add_text("Т.А.В.", color=AppConfig.attention_color)
                    dpg.add_text("- Токен Авторизации Входа")

                dpg.add_text(
                    "Это одноразовый токен для того чтобы иметь возможность создать свой собственный пароль на учётную запись. После использования Т. А. В. считается системой недействительным.",
                    wrap=0,
                )

            dpg.add_input_text(
                hint="Т. А. В.",
                tag="tae_token_input_text",
                width=408,
            )
            dpg.add_input_text(
                hint="Пароль",
                tag="tae_password_1_input_text",
                password=True,
                width=408,
            )
            dpg.add_input_text(
                hint="Повтор пароля",
                tag="tae_password_2_input_text",
                password=True,
                width=408,
            )

            with dpg.group(horizontal=True, tag="tae_btns"):
                dpg.add_button(
                    label="Отмена",
                    callback=cls._del_tae_callback,
                    width=200,
                )
                dpg.add_button(
                    label="Подтвердить",
                    callback=cls._on_tae_complite,
                    width=200,
                )

            dpg.add_image("mvd_img_logo", tag="tae_logo")

        ViewportResizeManager.add_callback("tae_window", cls._res_tae_callback)

    @classmethod
    def _on_tae_complite(cls):
        token: str = dpg.get_value("tae_token_input_text")
        password_1: str = dpg.get_value("tae_password_1_input_text")
        password_2: str = dpg.get_value("tae_password_2_input_text")

        if not all([token, password_1, password_2]):
            create_popup_window(
                "Ошибка ввода Т.А.В",
                "Поле с Т.А.В, или паролями не заполнено",
            )
            return

        if password_1 != password_2:
            create_popup_window(
                "Ошибка ввода Т.А.В",
                "Пароли не совпадают",
            )
            return

        if not token.startswith("CREATE-AUTH-"):
            create_popup_window(
                "Ошибка ввода Т.А.В",
                "Вы использовали НЕ токен создания в качестве КПК ID. Перепроверьте токен, вставив его повторно",
            )
            return

        code = ServerRequests.register(token, password_1.strip())
        if code == 200:
            cls._del_and_enter()
            return

        error_msg = {
            429: "Слишком много попыток ввода Т.А.В. Повторите попытку позже",
            426: "Версия вашего MVD network unit устарела. Запросите новую версию",
            403: "Т.А.В не опознан системой",
            400: "Т.А.В или пароль не были введены",
        }.get(
            code,
            f"Сервер вернул неизвестную ошибку #{code}. Просьба связаться со старшими сотрудниками МВД для решения проблемы",
        )

        create_popup_window("Ошибка авторизации", error_msg)
