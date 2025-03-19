import logging
import sys
import traceback

import dearpygui.dearpygui as dpg
from systems import AppConfig


class AppInitializer:
    @classmethod
    def init(cls):
        sys.excepthook = cls.global_exception_handler
        cls._init_dpg()
        cls._init_viewport()
        cls._load_fonts()
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
            vsync=True,
        )
        dpg.set_viewport_small_icon(str(AppConfig.img_fold / "mvd-red.ico"))
        dpg.set_viewport_large_icon(str(AppConfig.img_fold / "mvd-red.ico"))
        dpg.show_viewport()

    @classmethod
    def _theme_register(cls):
        pass

    @classmethod
    def _reg_static_img(cls):
        for file in [
            "ws 256x256.png",
            "404 256x256.png",
            "bartender 256x256.png",
            "deffy 256x256.png",
            "mercenary 256x256.png",
            "mvd 256x256.png",
            "raptor 256x256.png",
            "sf 256x256.png",
            "svarog 256x256.png",
            "ums 256x256.png",
        ]:
            _, _, _, data = dpg.load_image(str(AppConfig.img_fold / file))
            with dpg.texture_registry():
                dpg.add_static_texture(
                    256, 256, data, tag=f"{file.split()[0]}_img_logo"
                )

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

    @classmethod
    def _load_fonts(cls):
        font_base_path = AppConfig.data_fold / "fonts"
        default_font_path = font_base_path / "Monocraft" / "Monocraft.otf"

        with dpg.font_registry():
            with dpg.font(str(default_font_path), 14) as default_font:
                dpg.add_font_range_hint(dpg.mvFontRangeHint_Default)
                dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic)
                dpg.add_font_range(0x0391, 0x03C9)
                dpg.add_font_range(0x2070, 0x209F)

        dpg.bind_font(default_font)
