from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from config import ADMIN_ID

router = Router()

HELP = (
    "<b>Kassb Bot</b> \u2704\ufe0f\n\n"
    "\u0631\u0628\u0627\u062A\u062F \u062C\u0633\u062A\u062C\u0628 \u0627\u0637\u0644\u0627\u0639\u0627\u062A\u0645\u0648\u0645\u0644\u0648\u0645 \u062A\u0626\u062F\u0627\u0634\u062A\u0647\u200C\u0647\u0627\n\n"
    "<b>\u0641\u0631\u0645\u062A:</b>\n"
    "<code>\u0634\u0647\u0631 | \u062F\u0633\u062A\u0647\u200C\u0628\u0646\u062F\u0662</code>\n\n"
    "<b>\u0645\u062B\u0627\u0644\u200C\u0647\u0621:</b>\n"
    "  <code>\u062A\u0647\u0631\u0627\u0646 | \u0631\u0633\u062A\u0648\u0631\u0627\u0646</code>\n"
    "  <code>\u062A\u0628\u0631\u0666\u0662 | \u062F\u0646\u062F\u0627\u0646\u067E\u0634\u06A9</code>\n"
    "  <code>\u0645\u0634\u0647\u062F | \u062A\u0639\u0645\u0666\u0631\u062F\u0627\u0647 \u062E\u0648\u062F\u0631\u0648</code>\n\n"
    "<b>\u062F\u0633\u062A\u0648\u0631\u0627\u062A:</b>\n"
    "/start - \u0634\u0631\u0648\u0639\n"
    "/help  - \u0631\u0627\u0647\u0646\u0645\u0627\n"
    "/status - \u0648\u0636\u0649\u062A\u0646"
)

@router.message(Command("start"))
async def cmd_start(msg: Message):
    if msg.from_user.id != ADMIN_ID:
        await msg.answer("\u062F\u0633\u062A\u0631\u0633\u0666 \u0646\u062F\u0627\u0631\u0666\u062F.")
        return
    await msg.answer(HELP)

@router.message(Command("help"))
async def cmd_help(msg: Message):
    if msg.from_user.id != ADMIN_ID:
        return
    await msg.answer(HELP)

@router.message(Command("status"))
async def cmd_status(msg: Message):
    if msg.from_user.id != ADMIN_ID:
        return
    await msg.answer("<b>\u0648\u0636\u0649\u062A\u064B:</b> \u0628\u0627\u062A\u0646"
                     " \u062F\u0631 \u062D\u0627\u0644 \u0627\u062C\u0631\u0627\u0633\u062A\u064B.")
