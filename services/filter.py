import re

# کلیدواژه‌های مرتبط برای هر دسته
CATEGORY_KEYWORDS = {
    'تعویض روغنی': ['روغن', 'تعویض', 'اتوسرویس', 'خودرو', 'سرویس', 'oil', 'lube'],
    'نصاب دوربین': ['دوربین', 'مداربسته', 'cctv', 'امنیتی', 'نصاب', 'سیستم'],
    'چشم پزشکی': ['چشم', 'بینایی', 'عینک', 'اپتیک', 'چشمپزشک', 'eye', 'optic'],
    'دندانپزشک': ['دندان', 'دندانپزشک', 'کلینیک دندان', 'dental', 'dentist'],
    'رستوران': ['رستوران', 'غذا', 'کباب', 'فست فود', 'چلوکباب', 'سفره', 'restaurant'],
    'داروخانه': ['دارو', 'پخش', 'داروخانه', 'pharmacy'],
    'تعمیرگاه': ['تعمیر', 'سرویس', 'تعمیرگاه', 'مکانیکی', 'repair', 'garage'],
    'بیمارستان': ['بیمارستان', 'درمانگاه', 'کلینیک', 'hospital'],
    'هتل': ['هتل', 'مهمانپذیر', 'اقامت', 'hotel'],
    'سوپرمارکت': ['سوپر', 'فروشگاه', 'هایپر', 'supermarket', 'shop'],
}

def _get_keywords(category: str) -> list:
    cat = category.strip().lower()
    for key, kws in CATEGORY_KEYWORDS.items():
        if key in cat or cat in key:
            return kws
    # fallback: کلمات خود دسته‌بندی
    return [w for w in re.split(r'\s+', cat) if len(w) > 2]

def _score(item: dict, city: str, keywords: list) -> int:
    score = 0
    name    = (item.get('name','') or '').lower()
    address = (item.get('address','') or '').lower()
    cat     = (item.get('category','') or '').lower()
    city_l  = city.strip().lower()

    # شهر باید توی آدرس یا city فیلد باشه
    item_city = (item.get('city','') or '').lower()
    if city_l in item_city or city_l in address:
        score += 10
    else:
        score -= 5  # جریمه اگه شهر مطابقت نداره

    # کلیدواژه‌های دسته توی اسم یا دسته
    for kw in keywords:
        if kw in name:    score += 5
        if kw in cat:     score += 3
        if kw in address: score += 1

    # داشتن شماره تلفن = امتیاز بیشتر
    if item.get('phone',''):
        score += 3

    # منبع: نشان و بلد معتبرترن
    src = item.get('source','')
    if src == 'neshan': score += 4
    elif src == 'balad': score += 3

    return score

def filter_and_rank(results: list, city: str, category: str, min_score: int = 0) -> list:
    """فیلتر نتایج بی‌ربط و مرتب‌سازی بر اساس امتیاز"""
    keywords = _get_keywords(category)
    scored = []
    for item in results:
        s = _score(item, city, keywords)
        if s >= min_score:
            item['_score'] = s
            scored.append(item)
    scored.sort(key=lambda x: x.get('_score', 0), reverse=True)
    return scored
