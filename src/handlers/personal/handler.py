from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from states.bot_state import BotState

# -------------------------------
# Initialize router
# -------------------------------
router = Router()


@router.message(F.text, BotState.START)
async def echo(message: Message, state: FSMContext):
    """
    Echo handler for messages in the START state.

    - F.text: triggers only on text messages.
    - BotState.START: triggers only when user is in START FSM state.
    - Sends a copy of the received message back to the user.
    """
    # Send a copy of the received message back to the user
    await message.send_copy(message.from_user.id)
