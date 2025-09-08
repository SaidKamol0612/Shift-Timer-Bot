from .base import BaseCRUD
from ..models import ShiftRole
from ..schemas import ShiftSchema


class RoleCRUD(BaseCRUD[ShiftRole, ShiftSchema]):

    def __init__(self):
        super().__init__(ShiftRole)


shift_role_crud = RoleCRUD()
