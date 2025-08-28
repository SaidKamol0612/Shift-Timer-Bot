from aiogram.fsm.state import StatesGroup, State


class BotState(StatesGroup):
    """
    Define finite states for the bot using Aiogram's FSM (Finite State Machine).
    """

    START = State()

    class Register(StatesGroup):
        GET_NAME = State()
