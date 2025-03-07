import dearpygui.dearpygui as dpg
from systems import AppConfig, ServerRequests
from tools import TimerManager

from .create_tab import create_create_tab
from .search_tab import create_search_tab
from .system_tab import create_system_tab
from .unit_manage_tab import create_unit_manage_tab


class AppMainWindow:
    @classmethod
    def init(cls):
        cls._create_window()

        with dpg.menu_bar(
            parent="main_window",
        ):
            with dpg.menu(label="???", tag="auth_username"):
                dpg.add_menu_item(
                    label="Закрыть программу", callback=lambda: dpg.stop_dearpygui()
                )

            dpg.add_menu_item(label="|", enabled=False)

            dpg.add_menu_item(label="???", tag="time", enabled=False)
            TimerManager.add_timer("timer", cls._time_callback, 1)
            cls._time_callback()

    @classmethod
    def _time_callback(cls):
        current_datetime = AppConfig.get_game_time().strftime("%Y-%m-%d %H:%M:%S")
        dpg.set_item_label("time", current_datetime)

    @classmethod
    def _create_window(cls):
        with dpg.window(
            pos=(0, 0),
            no_move=True,
            no_resize=True,
            no_title_bar=True,
            tag="main_window",
        ):
            dpg.set_primary_window("main_window", value=True)
            dpg.add_tab_bar(tag="main_tab_bar", parent="main_window")
            cls._main_tab()

    @classmethod
    def _main_tab(cls):
        with dpg.tab(
            label="Главная",
            parent="main_tab_bar",
            tag="main_tab",
            order_mode=dpg.mvTabOrder_Leading,
        ):
            # Откровенно говоря то что closable в dpg.tab СКРЫВАЕТ, а не закрывает вкладку для меня контр интуитивно
            dpg.add_text("Создание вкладок:")
            dpg.add_group(tag="main_btn_group")
            cls._main_btn_render()
            dpg.add_separator()

    @classmethod
    def _main_btn_render(cls):
        if dpg.does_item_exist("main_btn_group"):
            dpg.delete_item("main_btn_group", children_only=True)

            dpg.add_button(
                label="Создать вкладку поиска",
                callback=create_search_tab,
                show=ServerRequests.has_access("get_db_data"),
                width=423,
                parent="main_btn_group",
            )

            dpg.add_button(
                label="Создать вкладку создания записей",
                callback=create_create_tab,
                show=ServerRequests.has_access("register_user"),
                width=423,
                parent="main_btn_group",
            )

            dpg.add_button(
                label="Создать вкладку управления юнитами",
                callback=create_unit_manage_tab,
                width=423,
                parent="main_btn_group",
            )

            dpg.add_button(
                label="System_control",
                callback=create_system_tab,
                show=ServerRequests.has_access("all"),
                width=423,
                parent="main_btn_group",
            )
