import aiohttp, logging
from .city_map import resolve_city

logger = logging.getLogger(__name__)
BASE = 'https://api.neshan.org/v1/search'

async def search_neshan(city: str, category: str, api_key: str, max_results: int = 200) -> list:
    if not api_key or api_key == 'your_neshan_api_key_here':
        return []
    info = resolve_city(city)
    headers = {'Api-Key': api_key}
    params = {
        'term': category,
        'lat': str(info['lat']),
        'lng': str(info['lng']),
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(BASE, headers=headers, params=params,
                                   timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    logger.warning(f'Neshan HTTP {r.status}')
                    return []
                data = await r.json()
    except Exception as e:
        logger.warning(f'Neshan: {e}')
        return []

    results = []
    for item in (data.get('items') or [])[:max_results]:
        loc = item.get('location') or {}
        results.append({
            'name': item.get('title', ''),
            'phone': '',
            'address': item.get('address', ''),
            'city': item.get('region', city),
            'province': item.get('neighbourhood', ''),
            'website': '',
            'rating': '',
            'category': item.get('type', ''),
            'latitude': str(loc.get('y', '')),
            'longitude': str(loc.get('x', '')),
            'source': 'neshan',
        })
    return results
