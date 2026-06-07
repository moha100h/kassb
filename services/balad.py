import aiohttp, logging
from .city_map import resolve_city

logger = logging.getLogger(__name__)
BASE = 'https://search.balad.ir/v5/place/search'

async def search_balad(city: str, category: str, max_results: int = 200) -> list:
    info = resolve_city(city)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Android 12; Mobile) AppleWebKit/537.36',
        'Accept': 'application/json',
        'Referer': 'https://balad.ir/',
    }
    # جستجو با نام فارسی و انگلیسی هر دو
    queries = list(dict.fromkeys([f'{category} {info["fa"]}', f'{category} {info["en"]}']))
    seen, results = set(), []
    async with aiohttp.ClientSession() as session:
        for q in queries:
            params = {'q': q, 'page': 1}
            try:
                async with session.get(BASE, headers=headers, params=params,
                                       timeout=aiohttp.ClientTimeout(total=15)) as r:
                    if r.status != 200:
                        logger.warning(f'Balad HTTP {r.status} for [{q}]')
                        continue
                    data = await r.json()
            except Exception as e:
                logger.warning(f'Balad [{q}]: {e}')
                continue
            for item in (data.get('results') or [])[:max_results]:
                geo   = item.get('geometry') or {}
                coords= geo.get('location') or {}
                props = item.get('properties') or {}
                phones= props.get('phones') or []
                phone = phones[0] if phones else ''
                name  = item.get('title', '')
                key   = (name.lower(), phone)
                if not name or key in seen: continue
                seen.add(key)
                results.append({
                    'name': name,
                    'phone': phone,
                    'address': item.get('address', ''),
                    'city': props.get('city', city),
                    'province': props.get('province', ''),
                    'website': props.get('website', ''),
                    'rating': str(props.get('rating', '')),
                    'category': item.get('category', ''),
                    'latitude': str(coords.get('lat', '')),
                    'longitude': str(coords.get('lng', '')),
                    'source': 'balad',
                })
    return results[:max_results]
