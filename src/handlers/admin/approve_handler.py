from aiogram import Router, F
from aiogram.types import CallbackQuery

from db import db_helper
from db.crud import shift_crud, user_crud
from db.schemas import ShiftUpdateSchema
from utils import AdminUtil

router = Router()


@router.callback_query(F.data.startswith("approve_"))
async def handle_approve(call_back: CallbackQuery):
    sh_id = call_back.data.split("_")[1]
    async with db_helper.session_factory() as session:
        shift = await shift_crud.update(
            session=session,
            model_id=int(sh_id),
            schema=ShiftUpdateSchema(is_approved=True),
        )
        worker = await user_crud.read(session=session, filters={"id": shift.user_id})
    await call_back.message.edit_reply_markup(reply_markup=None)
    await call_back.answer(text="✅ Qabul qilindi.", show_alert=True)
    text = "✅ Sizning hisobot admin tomonidan qabul qilindi."
    await AdminUtil.send_msg(chat_id=worker.tg_id, msg=text)


@router.callback_query(F.data.startswith("cancel_"))
async def handle_approve(call_back: CallbackQuery):
    sh_id = call_back.data.split("_")[1]
    async with db_helper.session_factory() as session:
        shift = await shift_crud.read(
            session=session,
            filters={"id": int(sh_id)},
        )
        worker = await user_crud.read(session=session, filters={"id": shift.user_id})
        await shift_crud.delete(session=session, model_id=shift.id)
    await call_back.message.delete()
    await call_back.answer(text="❌ Bekor qilindi.", show_alert=True)
    text = "❌ Sizning hisobot admin tomonidan bekor qilindi."
    await AdminUtil.send_msg(chat_id=worker.tg_id, msg=text)
