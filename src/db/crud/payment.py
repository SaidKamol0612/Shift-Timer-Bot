from ..models import Payment
from ..schemas import PaymentSchema

from .base import BaseCRUD


class PaymentCRUD(BaseCRUD[Payment, PaymentSchema]):
    def __init__(self):
        self.MODEL_TYPE = Payment
        super().__init__(Payment)


payment_crud = PaymentCRUD()
