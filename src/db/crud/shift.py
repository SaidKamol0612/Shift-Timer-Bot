from .base import BaseCRUD
from ..models import Shift
from ..schemas import ShiftSchema


class ShiftCRUD(BaseCRUD[Shift, ShiftSchema]):

    def __init__(self):
        super().__init__(Shift)


shift_crud = ShiftCRUD()
