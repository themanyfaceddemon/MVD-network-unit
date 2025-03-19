from typing import Literal

from systems import AppConfig, ServerRequests


class UserData:
    _STATE_LOC: dict[str, tuple[str, str]] = {
        "alive": ("Жив", "Жива"),
        "dead": ("Мёртв", "Мертва"),
        "missing": ("Пропал без вести", "Пропала без вести"),
        "on_review": ("На проверке", "На проверке"),
    }

    _STATUS_COLOR: dict[str, list[int]] = {
        "alive": AppConfig.alive_color,
        "dead": AppConfig.dead_color,
        "missing": AppConfig.missing_color,
        "on_review": AppConfig.on_review_color,
    }

    _SEX_LOC: dict[str, str] = {
        "male": "Мужской",
        "female": "Женский",
    }

    _RACE_LOC: dict[str, str] = {
        "human": "Человек",
        "halfhuman": "Полу-человек",
        "doll": "Кукла",
    }

    _FRACTION_LOC: dict[str, str] = {
        "ws": "Белое небо",
        "404": "Отряд 404",
        "bartender": "Бармен",
        "deffy": "DEFY",
        "mercenary": "Наёмник",
        "mvd": "МВД",
        "raptor": "Raptor Technology",
        "sf": "Sangvis Ferri",
        "svarog": "Svarog Heavy Industries",
        "ums": "Unity Medical Services",
    }

    def __init__(self, user_uuid: str) -> None:
        self._user_uuid: str = user_uuid
        user_data_dict = ServerRequests.get_user_info(user_uuid)
        if not user_data_dict:
            raise ValueError("emtpy data from server")

        self._name_rus: str | None = user_data_dict.get("name_rus")
        self._name_eng: str | None = user_data_dict.get("name_eng")
        self._name_cs: str | None = user_data_dict.get("name_cs")

        self._race: Literal["human", "halfhuman", "doll"] = user_data_dict.get("race")  # type: ignore

        self._user_type: str | None = user_data_dict.get("user_type")
        self._model: str | None = user_data_dict.get("model")

        self._place_of_birth: str | None = user_data_dict.get("place_of_birth")
        self._specialization: str | None = user_data_dict.get("specialization")
        self._goal: str | None = user_data_dict.get("goal")

        self._sex: Literal["male", "female"] = user_data_dict.get("sex")  # type: ignore
        self._status: Literal["alive", "dead", "missing", "on_review"] = (
            user_data_dict.get("status")
        )  # type: ignore

        self.additional_info: dict[str, str] = user_data_dict.get("additional_info", {})

    # region гетеры данных
    @property
    def user_uuid(self) -> str:
        return self._user_uuid

    @property
    def name_eng(self) -> str:
        return self._name_eng or "Не указано"

    @property
    def name_rus(self) -> str:
        return self._name_rus or "Не указано"

    @property
    def name_cs(self) -> str:
        return self._name_cs or "Не указано"

    @property
    def race(self) -> str:
        return self._RACE_LOC.get(self._race, "Неизвестная раса")

    @property
    def race_raw(self) -> str:
        return self._race

    @property
    def user_type(self) -> str:
        return self._user_type or "Не указано"

    @property
    def model(self) -> str:
        return self._model or "Не указано"

    @property
    def place_of_birth(self) -> str:
        return self._place_of_birth or "Не указано"

    @property
    def specialization(self) -> str:
        return self._specialization or "Не указано"

    @property
    def goal(self) -> str:
        return self._goal or "Не указано"

    @property
    def sex(self) -> str:
        return self._SEX_LOC.get(self._sex, "Неизвестный пол")

    @property
    def sex_color(self) -> list[int]:
        return AppConfig.male_color if self._sex == "male" else AppConfig.female_color

    @property
    def list_status(self) -> list[str]:
        list_of_return = []
        for values in self._STATE_LOC.values():
            list_of_return.append(values[0] if self._sex == "male" else values[1])

        return list_of_return

    @property
    def status(self) -> str:
        status_value = self._STATE_LOC.get(
            self._status, ("Неизвестный статус", "Неизвестный статус")
        )

        return status_value[0] if self._sex == "male" else status_value[1]

    @property
    def status_color(self) -> list[int]:
        return self._STATUS_COLOR.get(self._status, [255, 255, 255, 255])

    @property
    def has_add_fields(self) -> bool:
        return self._race != "human"

    @property
    def fraction(self) -> str:
        return self._FRACTION_LOC.get(self.fraction_raw, "Наёмник")

    @property
    def fraction_raw(self) -> str:
        return self.additional_info.get("fraction", "mercenary")

    # endregion


def get_display_name(user: dict[str, str] | None) -> str:
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
