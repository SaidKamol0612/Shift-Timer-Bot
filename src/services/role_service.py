import json
from pathlib import Path
from typing import List
from functools import lru_cache

from db.schemas import RoleSchema


class RoleService:
    def __init__(self):
        self.__ROLES_JSON = Path(__file__).parent.parent / "resources" / "roles.json"

    @lru_cache(maxsize=1)
    def read_roles(self) -> List[RoleSchema]:
        with self.__ROLES_JSON.open("r", encoding="utf-8") as file:
            roles: list[dict] = json.load(file)
        return [RoleSchema(**role) for role in roles]

    @lru_cache(maxsize=None)
    def read_role(self, code: str) -> RoleSchema | None:
        return next((r for r in self.read_roles() if r.code == code), None)


role_service = RoleService()
