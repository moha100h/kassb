from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from config import ADMIN_ID

router = Router()

HELP = (
    '<b>Kassb Bot</b>\n\n'
    'فرمت ارسال:\n'
    '<code>شهر | دسته‌بندی</code>\n\n'
    '<b>مثال‌ها:</b>\n'
    '  <code>تهران | رستوران</code>\n'
    '  <code>زنجان | نصاب دوربین مداربسته</code>\n'
    '  <code>تبریز | دندانپزشک</code>\n\n'
    '<b>دستورات:</b>\n'
    '/start    - شروع\n'
    '/settings - تنظیمات (API key و غیره)\n'
    '/status   - وضعیت سیستم\n'
    '/help     - راهنما'
)

@router.message(Command('start'))
async def cmd_start(msg: Message):
    if msg.from_user.id != ADMIN_ID:
        await msg.answer('دسترسی ندارید.')
        return
    await msg.answer(HELP)

@router.message(Command('help'))
async def cmd_help(msg: Message):
    if msg.from_user.id != ADMIN_ID:
        return
    await msg.answer(HELP)

@router.message(Command('status'))
async def cmd_status(msg: Message):
    if msg.from_user.id != ADMIN_ID:
        return
    await msg.answer('<b>وضعیت:</b> بات در حال اجراست.')
