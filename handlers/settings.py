from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config import ADMIN_ID
import os, dotenv

router = Router()
ENV_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')

class SetKey(StatesGroup):
    waiting = State()

def _read_env() -> dict:
    vals = {}
    if os.path.exists(ENV_PATH):
        with open(ENV_PATH) as f:
            for line in f:
                line = line.strip()
                if '=' in line and not line.startswith('#'):
                    k, v = line.split('=', 1)
                    vals[k.strip()] = v.strip()
    return vals

def _write_env(vals: dict):
    with open(ENV_PATH, 'w') as f:
        for k, v in vals.items():
            f.write(f'{k}={v}\n')

def _settings_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='🔑 تنظیم NESHAN_API_KEY', callback_data='set:NESHAN_API_KEY')],
        [InlineKeyboardButton(text='📊 تعداد نتایج (MAX_RESULTS)', callback_data='set:MAX_RESULTS')],
        [InlineKeyboardButton(text='❌ بستن', callback_data='set:close')],
    ])

@router.message(F.text == '/settings')
async def cmd_settings(msg: Message):
    if msg.from_user.id != ADMIN_ID:
        return
    vals = _read_env()
    neshan = '✅ تنظیم شده' if vals.get('NESHAN_API_KEY','') not in ('','your_neshan_api_key_here') else '❌ تنظیم نشده'
    max_r  = vals.get('MAX_RESULTS', '200')
    text = (
        '<b>⚙️ تنظیمات بات</b>\n\n'
        f'NESHAN_API_KEY: {neshan}\n'
        f'MAX_RESULTS: <code>{max_r}</code>\n\n'
        'یک گزینه انتخاب کن:'
    )
    await msg.answer(text, reply_markup=_settings_kb())

@router.callback_query(F.data.startswith('set:'))
async def cb_settings(cb: CallbackQuery, state: FSMContext):
    if cb.from_user.id != ADMIN_ID:
        return
    key = cb.data.split(':', 1)[1]
    if key == 'close':
        await cb.message.delete()
        return
    labels = {
        'NESHAN_API_KEY': 'کلید API نشان (از neshan.org رایگان بگیر)',
        'MAX_RESULTS': 'حداکثر تعداد نتایج (عدد صحیح وارد کن)',
    }
    await state.set_state(SetKey.waiting)
    await state.update_data(key=key)
    await cb.message.edit_text(
        f'✏️ {labels.get(key, key)}:\n\n'
        f'مقدار جدید را بفرست:'
    )

@router.message(SetKey.waiting)
async def receive_value(msg: Message, state: FSMContext):
    if msg.from_user.id != ADMIN_ID:
        return
    data = await state.get_data()
    key  = data.get('key','')
    val  = (msg.text or '').strip()
    if not val:
        await msg.answer('مقدار خالی است.')
        return
    if key == 'MAX_RESULTS' and not val.isdigit():
        await msg.answer('فقط عدد وارد کن.')
        return
    vals = _read_env()
    vals[key] = val
    _write_env(vals)
    # reload env in current process
    os.environ[key] = val
    dotenv.load_dotenv(ENV_PATH, override=True)
    await state.clear()
    await msg.answer(
        f'✅ <b>{key}</b> با موفقیت ذخیره شد.\n'
        f'مقدار: <code>{val if key != "NESHAN_API_KEY" else val[:8]+"..."+val[-4:]}</code>'
    )
