import os
from datetime import datetime
from aiogram import Router, F
from aiogram.types import Message, BufferedInputFile
from config import ADMIN_ID, MAX_RESULTS, EXPORT_DIR
from services.osm import search_osm
from services.db import save_results, get_cached
from services.export import make_xlsx

router = Router()

@router.message(F.text & ~F.text.startswith('/'))
async def handle_query(msg: Message):
    if msg.from_user.id != ADMIN_ID:
        return
    text = (msg.text or '').strip()
    if '|' not in text:
        await msg.answer('فرمت اشتباه. مثال: <code>تهران | رستوران</code>')
        return
    city, category = [p.strip() for p in text.split('|', 1)]
    await msg.answer('✅ درخواست دریافت شد.')
    status = await msg.answer('🔍 در حال جستجو…')
    cached = get_cached(city, category)
    if cached:
        results = cached
        await status.edit_text(f'📊 نتایج از کش: <b>{len(results)}</b>')
    else:
        results = await search_osm(city, category, MAX_RESULTS)
        await status.edit_text(f'📊 تعداد نتایج پیدا شده: <b>{len(results)}</b>')
        if results:
            save_results(city, category, results)
    if not results:
        await status.edit_text('نتیجه‌ای یافت نشد.')
        return
    await status.edit_text('🧹 حذف موارد تکراری…')
    seen, unique = set(), []
    for r in results:
        key = (r.get('name', '').lower(), r.get('phone', ''))
        if key not in seen:
            seen.add(key)
            unique.append(r)
    await status.edit_text(f'📁 ساخت فایل اکسل… ({len(unique)} مورد)')
    os.makedirs(EXPORT_DIR, exist_ok=True)
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'kassb_{city}_{category}_{ts}.xlsx'
    xlsx_data = make_xlsx(unique, city, category)
    await status.edit_text('📤 ارسال فایل…')
    await msg.answer_document(
        BufferedInputFile(xlsx_data, filename=filename),
        caption=f'شهر: {city} | دسته: {category} | تعداد: {len(unique)}'
    )
    await status.edit_text('✅ عملیات با موفقیت انجام شد.')
