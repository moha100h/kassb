import aiohttp, asyncio, logging

logger = logging.getLogger(__name__)
NOMINATIM = 'https://nominatim.openstreetmap.org/search'
OVERPASS  = 'https://overpass-api.de/api/interpreter'
HEADERS   = {'User-Agent': 'KassbBot/1.0'}

SYNONYMS = {
    'نصاب دوربین': ['دوربین مداربسته', 'CCTV', 'دوربین امنیتی', 'سیستم امنیتی', 'نصب دوربین'],
    'رستوران': ['رستوران', 'غذاخوری', 'کبابی', 'فست فود', 'restaurant', 'food'],
    'دندانپزشک': ['دندانپزشک', 'کلینیک دندانپزشکی', 'dentist', 'dental'],
    'تعمیرگاه خودرو': ['تعمیرگاه', 'سرویس خودرو', 'اتوسرویس', 'car repair', 'garage'],
    'داروخانه': ['داروخانه', 'پخش دارو', 'pharmacy', 'drugstore'],
    'بیمارستان': ['بیمارستان', 'درمانگاه', 'کلینیک', 'hospital', 'clinic'],
    'هتل': ['هتل', 'مهمانپذیر', 'اقامتگاه', 'hotel'],
    'بانک': ['بانک', 'شعبه بانک', 'bank'],
    'مدرسه': ['مدرسه', 'دبستان', 'دبیرستان', 'school'],
    'سوپرمارکت': ['سوپرمارکت', 'فروشگاه', 'هایپرمارکت', 'supermarket', 'shop'],
}

def _expand(category: str) -> list:
    cat = category.strip()
    for key, synonyms in SYNONYMS.items():
        if key in cat or cat in key:
            return list(dict.fromkeys([cat] + synonyms))
    return [cat]

def _norm_phone(p):
    if not p: return ''
    d = ''.join(c for c in p if c.isdigit())
    if len(d) == 11 and d.startswith('0'): return '+98' + d[1:]
    if len(d) == 10: return '+98' + d
    if len(d) == 12 and d.startswith('98'): return '+' + d
    return p

async def _nominatim(session, city, term, limit=50):
    params = {'q': f'{term} {city}', 'format': 'json', 'limit': limit,
              'addressdetails': 1, 'extratags': 1, 'namedetails': 1}
    try:
        async with session.get(NOMINATIM, params=params, headers=HEADERS,
                               timeout=aiohttp.ClientTimeout(total=20)) as r:
            if r.status == 200:
                return await r.json()
    except Exception as e:
        logger.warning(f'Nominatim [{term}]: {e}')
    return []

async def _overpass(session, city, term):
    ql = (
        f'[out:json][timeout:25];area[name="{city}"]->.a;'
        f'(node["amenity"](area.a);way["amenity"](area.a);'
        f'node["shop"](area.a);node["name"~"{term}",i](area.a););'
        f'out body;>;out skel qt;'
    )
    try:
        async with session.post(OVERPASS, data=ql,
                                timeout=aiohttp.ClientTimeout(total=30)) as r:
            if r.status == 200:
                return (await r.json()).get('elements', [])
    except Exception as e:
        logger.warning(f'Overpass [{term}]: {e}')
    return []

async def search_osm(city: str, category: str, max_results: int = 200) -> list:
    terms = _expand(category)
    seen, results = set(), []

    async with aiohttp.ClientSession() as session:
        tasks = []
        for term in terms:
            tasks.append(_nominatim(session, city, term, 50))
            tasks.append(_overpass(session, city, term))
        all_results = await asyncio.gather(*tasks, return_exceptions=True)

    nom_results = [r for i, r in enumerate(all_results) if i % 2 == 0 and isinstance(r, list)]
    ovr_results = [r for i, r in enumerate(all_results) if i % 2 == 1 and isinstance(r, list)]

    for nom in nom_results:
        for d in nom:
            tags = d.get('extratags') or {}
            nd   = d.get('namedetails') or {}
            name = nd.get('name:fa') or nd.get('name') or d.get('display_name','').split(',')[0].strip()
            if not name: continue
            key = (name.lower(), d.get('lat',''))
            if key in seen: continue
            seen.add(key)
            addr = d.get('address') or {}
            results.append({
                'name': name,
                'phone': _norm_phone(tags.get('phone','') or tags.get('contact:phone','')),
                'address': d.get('display_name',''),
                'city': addr.get('city') or addr.get('town') or addr.get('village',''),
                'province': addr.get('state',''),
                'website': tags.get('website','') or tags.get('contact:website',''),
                'rating': '',
                'category': d.get('type','') or tags.get('amenity','') or tags.get('shop',''),
                'latitude': d.get('lat',''),
                'longitude': d.get('lon',''),
                'source': 'osm',
            })

    for ovr in ovr_results:
        for d in ovr:
            tags = d.get('tags') or {}
            name = tags.get('name:fa') or tags.get('name','')
            if not name: continue
            lat = str(d.get('lat','') or (d.get('center') or {}).get('lat',''))
            key = (name.lower(), lat)
            if key in seen: continue
            seen.add(key)
            results.append({
                'name': name,
                'phone': _norm_phone(tags.get('phone','') or tags.get('contact:phone','')),
                'address': ', '.join(filter(None,[tags.get('addr:street',''),tags.get('addr:housenumber',''),tags.get('addr:city','')])),
                'city': tags.get('addr:city',''),
                'province': tags.get('addr:province',''),
                'website': tags.get('website','') or tags.get('contact:website',''),
                'rating': '',
                'category': tags.get('amenity','') or tags.get('shop',''),
                'latitude': lat,
                'longitude': str(d.get('lon','') or (d.get('center') or {}).get('lon','')),
                'source': 'osm',
            })

    return results[:max_results]
