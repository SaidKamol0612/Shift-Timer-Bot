from aiogram.fsm.state import StatesGroup, State


class BotState(StatesGroup):
    """
    Define finite states for the bot using Aiogram's FSM (Finite State Machine).
    """

    START = State()

    ADMIN_MENU = State()

    class SetPayment(StatesGroup):
        CHOOSE_WORKER = State()
        SET_AMOUNT = State()
        SET_COMMENT = State()

    class GetReport(StatesGroup):
        CHOOSE_WORKER = State()

    WORKER_MENU = State()

    class SetDayShift(StatesGroup):
        SET_START = State()
        SET_END = State()
        SET_PAUSE = State()
        SET_ROLES = State()
        ACCEPT = State()

    class SetNightShift(StatesGroup):
        SET_COUNT = State()
        SET_ROLES = State()
        ACCEPT = State()

    class Register(StatesGroup):
        GET_NAME = State()
