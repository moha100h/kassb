import os
from datetime import datetime
from aiogram import Router, F
from aiogram.types import Message, BufferedInputFile
from config import ADMIN_ID, MAX_RESULTS, EXPORT_DIR
from services.osm import search_osm
from services.db import save_results, get_cached
from services.export import make_xlsx

router = Router()

@router.message(F.text & ~F.text.startswith("/"))
async def handle_query(msg: Message):
    if msg.from_user.id != ADMIN_ID:
        return
    text = (msg.text or "").strip()
    if "|" not in text:
        await msg.answer(
            "\u0641\u0631\u0645\u062A \u0627\u0634\u062A\u0628\u0627\u0647. \u0645\u062B\u0627\u0644: "
            "<code>\u062A\u0647\u0631\u0627\u0646 | \u0631\u0633\u062A\u0648\u0631\u0627\u0646</code>"
        )
        return

    city, category = [p.strip() for p in text.split("|", 1)]

    await msg.answer("\u2705 \u062F\u0631\u062E\u0648\u0627\u0633\u062A \u062F\u0631\u0666\u0627\u0641\u062A \u0634\u062F.")
    status = await msg.answer("\uD83D\uDD4D \u062F\u0631 \u062D\u0627\u0644 \u062C\u0633\u062A\u062C\u0648\u2026")

    cached = get_cached(city, category)
    if cached:
        results = cached
        await status.edit_text(f"\uD83D\uDCC8 \u0646\u062A\u0627\u0646\u062C \u0627\u0631\u062A\u0628\u0627\u0627 \u062F\u0627\u062F\u0647 \u0634\u062F: <b>{len(results)}</b>")
    else:
        results = await search_osm(city, category, MAX_RESULTS)
        await status.edit_text(f"\uD83D\uDCC8 \u062A\u0639\u062F\u0627\u062F \u0646\u062A\u0627\u0646\u062C \u067E\u0666\u062F\u0627 \u0634\u062F\u0647: <b>{len(results)}</b>")
        if results:
            save_results(city, category, results)

    if not results:
        await status.edit_text("\u064E\u062A\u0666\u062C\u0647\u200C\u0627\u0666 \u066A\u0627\u0641\u062A \u0646\u0634\u062F.")
        return

    await status.edit_text("\uD83E\uDD79 \u062D\u0629\u0641 \u0645\u0648\u0627\u0631\u062F \u062A\u06A9\u0631\u0627\u0631\u0666\u2026")
    seen, unique = set(), []
    for r in results:
        key = (r.get("name", "").lower(), r.get("phone", ""))
        if key not in seen:
            seen.add(key)
            unique.append(r)

    await status.edit_text(f"\uD83D\uDCC1 \u0633\u0627\u062E\u062A \u0641\u0627\u0666\u0644 \u0627\u06A8\uD83D\uDCB3 ({len(unique)} \u0645\u0648\u0631\u062F)")
    os.makedirs(EXPORT_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"kassb_{city}_{category}_{ts}.xlsx"
    xlsx_data = make_xlsx(unique, city, category)

    await status.edit_text("\uD83D\uDCE4 \u0627\u0631\u0633\u0627\u0644 \u0641\u0627\u0666\u0644\u2026")
    await msg.answer_document(
        BufferedInputFile(xlsx_data, filename=filename),
        caption=f"\u0634\u0647\u0631: {city} | \u062F\u0633\u062A\u0647: {category} | \u062A\u0639\u062F\u0627\u062F: {len(unique)}"
    )
    await status.edit_text("\u2705 \u0639\u0645\u0644\u066A\u0627\u062A \u0628\u0627 \u0645\u0648\u0641\u0642\u0666\u062A \u0627\u0646\u062C\u0627\u0645 \u0634\u062F.")
