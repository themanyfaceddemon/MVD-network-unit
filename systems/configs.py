import pickle
from atexit import register
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, Dict


class AppConfig:
    data_fold = Path(__file__).resolve().parents[1] / "data"
    img_fold = data_fold / "img"
    _config_data: Dict[str, Any] = {}
    _config_file = data_fold / "config.pkl"
    

    server_data_update_time: int = 60

    uuid_color = [50, 205, 50, 255]
    attention_color = [255, 165, 0, 255]
    red_color = [178, 34, 34, 255]
    green_color = [102, 204, 0, 255]
    male_color = [0, 206, 209, 255]
    female_color = [219, 112, 147, 255]

    @classmethod
    def init(cls) -> None:
        if cls._config_file.exists():
            try:
                with cls._config_file.open("rb") as file:
                    cls._config_data = pickle.load(file)
            except (pickle.PickleError, EOFError):
                cls._config_data = {}

        else:
            cls._config_data = {}

        register(cls._save)

    @classmethod
    def _save(cls) -> None:
        with cls._config_file.open("wb") as file:
            pickle.dump(cls._config_data, file)

    @classmethod
    def get(cls, key: str, default: Any | None = None):
        return cls._config_data.get(key, default)

    @classmethod
    def has(cls, key: str) -> bool:
        return key in cls._config_data

    @classmethod
    def set(cls, key: str, value: Any):
        cls._config_data[key] = value

    @classmethod
    def pop(cls, key: str):
        cls._config_data.pop(key)

    @classmethod
    def get_game_time(cls) -> datetime:
        return datetime.now(UTC) + timedelta(365 * 40)
