from aiogram.fsm.state import StatesGroup, State


class BotState(StatesGroup):
    """
    Define finite states for the bot using Aiogram's FSM (Finite State Machine).
    """

    START = State()

    ADMIN_MENU = State()
    
    WORKER_MENU = State()
    SET_START = State()

    class Register(StatesGroup):
        GET_NAME = State()
