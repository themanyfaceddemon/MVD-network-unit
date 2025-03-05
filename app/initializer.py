import logging
import sys
import traceback

import dearpygui.dearpygui as dpg
from systems import AppConfig
from tools import FontManager


class AppInitializer:
    @classmethod
    def init(cls):
        sys.excepthook = cls.global_exception_handler
        cls._init_dpg()
        cls._init_viewport()
        FontManager.load_fonts()
        cls._theme_register()
        cls._reg_static_img()
        cls._setup_default_theme()

    @classmethod
    def _init_dpg(cls):
        dpg.create_context()
        dpg.setup_dearpygui()

    @classmethod
    def _init_viewport(cls):
        dpg.create_viewport(
            title="MVD network unit",
            width=800,
            min_width=800,
            height=600,
            min_height=600,
        )
        dpg.set_viewport_small_icon(str(AppConfig.img_fold / "mvd-red.ico"))
        dpg.set_viewport_large_icon(str(AppConfig.img_fold / "mvd-red.ico"))
        dpg.show_viewport()

    @classmethod
    def _theme_register(cls):
        with dpg.theme(tag="theme_low"):
            with dpg.theme_component(dpg.mvProgressBar):
                dpg.add_theme_color(
                    dpg.mvThemeCol_PlotHistogram,
                    (144, 255, 144),
                    category=dpg.mvThemeCat_Core,
                )

        with dpg.theme(tag="theme_medium"):
            with dpg.theme_component(dpg.mvProgressBar):
                dpg.add_theme_color(
                    dpg.mvThemeCol_PlotHistogram,
                    (255, 255, 50),
                    category=dpg.mvThemeCat_Core,
                )

        with dpg.theme(tag="theme_high"):
            with dpg.theme_component(dpg.mvProgressBar):
                dpg.add_theme_color(
                    dpg.mvThemeCol_PlotHistogram,
                    (255, 50, 50),
                    category=dpg.mvThemeCat_Core,
                )

    @classmethod
    def _reg_static_img(cls):
        width, height, _, data = dpg.load_image(
            str(AppConfig.img_fold / "mvd 256x256.png")
        )
        with dpg.texture_registry():
            dpg.add_static_texture(width, height, data, tag="mvd_img_256_256")

    @classmethod
    def _setup_default_theme(cls):
        with dpg.theme() as default_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(
                    dpg.mvThemeCol_TitleBg,
                    AppConfig.attention_color,
                    category=dpg.mvThemeCat_Core,
                )
                dpg.add_theme_color(
                    dpg.mvThemeCol_TitleBgActive,
                    AppConfig.attention_color,
                    category=dpg.mvThemeCat_Core,
                )
                dpg.add_theme_color(
                    dpg.mvThemeCol_TitleBgCollapsed,
                    AppConfig.attention_color,
                    category=dpg.mvThemeCat_Core,
                )
                dpg.add_theme_color(
                    dpg.mvThemeCol_Border,
                    (0, 0, 0, 255),
                    category=dpg.mvThemeCat_Core,
                )
                dpg.add_theme_color(
                    dpg.mvThemeCol_BorderShadow,
                    (0, 0, 0, 255),
                    category=dpg.mvThemeCat_Core,
                )

            dpg.set_global_font_scale(1.0)
            dpg.bind_theme(default_theme)

    @classmethod
    def global_exception_handler(cls, exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        error_message = "".join(
            traceback.format_exception(exc_type, exc_value, exc_traceback)
        )
        logging.error("Необработанная ошибка системы:\n%s", error_message)
