from aiogram.fsm.state import StatesGroup, State

class BotState(StatesGroup):
    """
    Define finite states for the bot using Aiogram's FSM (Finite State Machine).

    Example usage:
        - START: initial state when user interacts with the bot.
        - Additional states can be added as needed for multi-step workflows.
    """
    
    START = State()  # Initial state when user sends /start or begins interaction
