import os
from datetime import datetime
from aiogram import Router, F
from aiogram.types import Message, BufferedInputFile
from config import ADMIN_ID, MAX_RESULTS, EXPORT_DIR, NESHAN_API_KEY
from services.osm import search_osm
from services.neshan import search_neshan
from services.balad import search_balad
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
        await status.edit_text('🔍 جستجو در نشان، بلد و OSM…')
        import asyncio
        osm_task     = search_osm(city, category, MAX_RESULTS)
        neshan_task  = search_neshan(city, category, NESHAN_API_KEY, MAX_RESULTS)
        balad_task   = search_balad(city, category, MAX_RESULTS)
        osm_r, neshan_r, balad_r = await asyncio.gather(osm_task, neshan_task, balad_task)

        await status.edit_text(
            f'📊 نتایج: '
            f'نشان <b>{len(neshan_r)}</b> | '
            f'بلد <b>{len(balad_r)}</b> | '
            f'OSM <b>{len(osm_r)}</b>'
        )

        # merge + dedup by name+phone
        seen, results = set(), []
        for r in neshan_r + balad_r + osm_r:
            key = (r.get('name','').strip().lower(), r.get('phone',''))
            if key[0] and key not in seen:
                seen.add(key)
                results.append(r)

        if results:
            save_results(city, category, results)

    if not results:
        await status.edit_text('نتیجه‌ای یافت نشد.')
        return

    await status.edit_text(f'🧹 حذف تکراری و ساخت فایل… ({len(results)} مورد)')
    os.makedirs(EXPORT_DIR, exist_ok=True)
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'kassb_{city}_{category}_{ts}.xlsx'
    xlsx_data = make_xlsx(results, city, category)

    await status.edit_text('📤 ارسال فایل…')
    await msg.answer_document(
        BufferedInputFile(xlsx_data, filename=filename),
        caption=(
            f'شهر: {city} | دسته: {category}\n'
            f'تعداد کل: <b>{len(results)}</b>'
        )
    )
    await status.edit_text('✅ عملیات با موفقیت انجام شد.')
