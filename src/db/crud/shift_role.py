from .base import BaseCRUD
from ..models import ShiftRole
from ..schemas import ShiftReportSchema


class RoleCRUD(BaseCRUD[ShiftRole, ShiftReportSchema]):

    def __init__(self):
        super().__init__(ShiftRole)


shift_role_crud = RoleCRUD()
