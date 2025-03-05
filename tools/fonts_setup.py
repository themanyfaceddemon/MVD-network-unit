import dearpygui.dearpygui as dpg
from systems import AppConfig


class FontManager:
    @staticmethod
    def load_fonts():
        font_base_path = AppConfig.data_fold / "fonts"
        default_font_path = font_base_path / "Monocraft" / "Monocraft.otf"

        with dpg.font_registry():
            with dpg.font(str(default_font_path), 14) as default_font:
                dpg.add_font_range_hint(dpg.mvFontRangeHint_Default)
                dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic)
                dpg.add_font_range(0x0391, 0x03C9)
                dpg.add_font_range(0x2070, 0x209F)

        dpg.bind_font(default_font)
