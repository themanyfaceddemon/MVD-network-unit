import atexit
import logging
import tempfile
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, Final, List, Literal, Set

import requests
from PIL import Image

logger = logging.getLogger("С.С МВД")


class ServerRequests:
    _base_url: Final[str] = "http://194.87.94.191:7000"

    _session = requests.Session()
    _session.headers.update({"X-App-Version": "1.0.1"})

    _access: Set[str] = set()

    cur_username: str = ""

    @classmethod
    def _kill(cls, response: requests.Response) -> None:
        raise RuntimeError(
            f"Сервер МВД нашёл запасы алкоголя Вуди. \n| Код ошибки: {response.status_code}\n| Последние слова сервера: {response.json()}"
        )

    @classmethod
    def who_am_i(cls) -> None:
        response = cls._session.get(cls._base_url + "/unit/who_am_i")
        if response.status_code != 200:
            cls._kill(response)
            return

        json = response.json()
        cls.cur_username = json.get("username", "???")
        cls._access = set(json.get("access", []))
        logger.info(f"Авторизован в сервере МВД как '{cls.cur_username}'")

    @classmethod
    def login(cls, login: str, password: str) -> int:
        response = cls._session.post(
            cls._base_url + "/unit/login",
            json={"username": login, "password": password},
        )

        if response.status_code == 200:
            token = response.json()["token"]
            cls._session.headers.update({"Authorization": f"Bearer {token}"})
            cls.who_am_i()
            atexit.register(cls.logout)
            return 200

        return response.status_code

    @classmethod
    def register(cls, token: str, password: str) -> int:
        response = cls._session.post(
            cls._base_url + "/unit/register",
            json={"token": token, "password": password},
        )
        if response.status_code == 200:
            token = response.json()["token"]
            cls._session.headers.update({"Authorization": f"Bearer {token}"})
            cls.who_am_i()
            atexit.register(cls.logout)
            return 200

        return response.status_code

    @classmethod
    def logout(cls) -> None:
        logger.info("Отключение от сервера МВД")
        cls._session.get(cls._base_url + "/unit/logout")
        cls._session.headers.pop("Authorization")

    @classmethod
    def has_access(
        cls,
        need_access: Set[str] | str,
        type_check: Literal["&&", "||"] = "&&",
    ) -> bool:
        if "all" in cls._access:
            return True

        if isinstance(need_access, str):
            return need_access in cls._access

        if type_check == "&&":
            return need_access.issubset(cls._access)

        elif type_check == "||":
            return not need_access.isdisjoint(cls._access)

        raise ValueError(f"Invalid type_check value: {type_check}")

    # region Работа с юнитами
    @classmethod
    def create_unit(cls, username: str):
        response = cls._session.post(
            cls._base_url + "/unit/create_unit",
            json={"username": username},
        )

        return response.json()

    @classmethod
    def update_unit(
        cls,
        name: str,
        fake_name: str | None = None,
        salary: int | None = None,
        user_group: str | None = None,
        user_order: int | None = None,
        rank: str | None = None,
        specialization: str | None = None,
        hide: bool | None = None,
        access: set[str] | None = None,
    ):
        json = {
            "name": name,
            "fake_name": fake_name,
            "salary": salary,
            "user_group": user_group,
            "user_order": user_order,
            "rank": rank,
            "specialization": specialization,
            "hide": hide,
        }
        if access:
            json["access"] = list(access)

        response = cls._session.post(cls._base_url + "/unit/update_unit", json=json)

        return response.json()

    @classmethod
    def get_unit_info(cls, username: str) -> dict | None:
        response = cls._session.post(
            cls._base_url + "/unit/get_unit_info",
            json={"username": username},
        )

        return response.json()

    @classmethod
    def delete_user(cls, username: str):
        cls._session.post(
            cls._base_url + "/unit/delete_unit",
            json={"username": username},
        )

    @classmethod
    def get_units(cls):
        response = cls._session.get(cls._base_url + "/unit/get_units")

        return response.json()

    @classmethod
    def get_unit_access(cls, username):
        response = cls._session.post(
            cls._base_url + "/unit/get_unit_access",
            json={"username": username},
        )

        return response.json()

    @classmethod
    def add_unit_access(cls, username: str, access: str) -> dict:
        response = cls._session.post(
            cls._base_url + "/unit/add_unit_access",
            json={"username": username, "access": access},
        )

        return response.json()

    @classmethod
    def remove_unit_access(cls, username: str, access: str) -> dict:
        response = cls._session.post(
            cls._base_url + "/unit/remove_unit_access",
            json={"username": username, "access": access},
        )

        return response.json()

    # endregion

    @classmethod
    def create_human(
        cls,
        nameRus: str | None,
        nameEng: str | None,
        cs: str | None,
        sex: Literal["male", "female"],
        pob: str | None,
        specialization: str | None,
        goal: str | None,
        file_path: Path,
    ) -> int:
        with open(str(file_path), "rb") as file:
            file = {"image": file}
            resp = cls._session.post(
                cls._base_url + "/user/create/human",
                data={
                    "nameRus": nameRus,
                    "nameEng": nameEng,
                    "cs": cs,
                    "sex": sex,
                    "pob": pob,
                    "specialization": specialization,
                    "goal": goal,
                },
                files=file,
            )

        return resp.status_code

    @classmethod
    def create_doll(
        cls,
        nameRus: str | None,
        nameEng: str | None,
        type: Literal["T", "A", "M"],
        model: str | None,
        sex: Literal["male", "female"],
        pob: str | None,
        specialization: str | None,
        goal: str | None,
        file_path: Path,
    ) -> int:
        with open(str(file_path), "rb") as file:
            file = {"image": file}
            resp = cls._session.post(
                cls._base_url + "/user/create/doll",
                data={
                    "nameRus": nameRus,
                    "nameEng": nameEng,
                    "type": type,
                    "model": model,
                    "sex": sex,
                    "pob": pob,
                    "specialization": specialization,
                    "goal": goal,
                },
                files=file,
            )

        return resp.status_code

    @classmethod
    def create_halfhuman(
        cls,
        nameRus: str | None,
        nameEng: str | None,
        type: str | None,
        cs: str | None,
        sex: Literal["male", "female"],
        pob: str | None,
        specialization: str | None,
        goal: str | None,
        file_path: Path,
    ) -> int:
        with open(str(file_path), "rb") as file:
            file = {"image": file}
            resp = cls._session.post(
                cls._base_url + "/user/create/halfhuman",
                data={
                    "nameRus": nameRus,
                    "nameEng": nameEng,
                    "type": type,
                    "cs": cs,
                    "sex": sex,
                    "pob": pob,
                    "specialization": specialization,
                    "goal": goal,
                },
                files=file,
            )

        return resp.status_code

    @classmethod
    def get_all_users(cls) -> List[Dict[str, str]]:
        resp = cls._session.get(cls._base_url + "/user/data/all_users")

        return resp.json()

    @classmethod
    def get_user_info(cls, user_id: str) -> Dict[str, Any] | None:
        resp = cls._session.get(
            cls._base_url + "/user/data/info", params={"user_id": user_id}
        )

        if resp.status_code == 200:
            return resp.json()

        return None

    @classmethod
    def get_image(
        cls,
        user_id: str | None,
        max_size: tuple = (1024, 1024),
    ) -> Path | None:
        if user_id is None:
            return None

        resp = cls._session.get(
            cls._base_url + "/user/data/image",
            params={"filename": user_id},
        )
        if resp.status_code != 200:
            return None

        try:
            with Image.open(BytesIO(resp.content)) as img:
                img.thumbnail(max_size)

                with tempfile.NamedTemporaryFile(
                    delete=False, suffix=".png", mode="wb"
                ) as temp_file:
                    img.save(temp_file, format="PNG")
                    return Path(temp_file.name)

        except Exception:
            return None

    @classmethod
    def change_user_data(
        cls,
        user_id: str,
        status: Literal["alive", "dead", "missing", "on_review"] | None = None,
        race: Literal["human", "doll", "halfhuman"] | None = None,
        name_rus: str | None = None,
        name_eng: str | None = None,
        name_cs: str | None = None,
        user_type: str | None = None,
        model: str | None = None,
        sex: Literal["male", "female"] | None = None,
        place_of_birth: str | None = None,
        specialization: str | None = None,
        goal: str | None = None,
    ) -> int:
        response = cls._session.post(
            cls._base_url + "/user/data/change",
            json={
                "user_id": user_id,
                "status": status,
                "race": race,
                "name_rus": name_rus,
                "name_eng": name_eng,
                "name_cs": name_cs,
                "user_type": user_type,
                "model": model,
                "sex": sex,
                "place_of_birth": place_of_birth,
                "specialization": specialization,
                "goal": goal,
            },
        )

        return response.status_code

    @classmethod
    def delete_user_data(cls, user_id: str) -> int:
        response = cls._session.post(
            cls._base_url + "/user/data/delete",
            json={"user_id": user_id},
        )

        return response.status_code
