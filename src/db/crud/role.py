from .base import BaseCRUD
from ..models import Role
from ..schemas import RoleSchema


class RoleCRUD(BaseCRUD[Role, RoleSchema]):

    def __init__(self):
        super().__init__(Role)


role_crud = RoleCRUD()
