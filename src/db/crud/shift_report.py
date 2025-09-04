from .base import BaseCRUD
from ..models import ShiftReport
from ..schemas import ShiftReportSchema


class ShiftReportCRUD(BaseCRUD[ShiftReport, ShiftReportSchema]):

    def __init__(self):
        super().__init__(ShiftReport)


shift_report_crud = ShiftReportCRUD()
