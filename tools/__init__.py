from typing import Any

from .error_popup import create_popup_window
from .select_file_folder import FileManager
from .timer import TimerManager
from .viewport_resize import ViewportResizeManager


def get_display_name(user: dict[str, Any] | None) -> str:
    if user is None:
        return "Без имени"
    
    parts = []
    name_rus = user.get("name_rus") or None
    name_eng = user.get("name_eng") or None
    name_cs = user.get("name_cs") or None

    if name_rus:
        parts.append(name_rus)
    if name_eng:
        parts.append(name_eng)
    if name_cs:
        parts.append(f"'{name_cs}'")
    return " | ".join(parts) or "Без имени"
