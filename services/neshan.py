import aiohttp, logging

logger = logging.getLogger(__name__)
BASE = 'https://api.neshan.org/v1/search'

async def search_neshan(city: str, category: str, api_key: str, max_results: int = 200) -> list:
    if not api_key:
        return []
    headers = {'Api-Key': api_key}
    params = {'term': f'{category} {city}', 'lat': '35.6892', 'lng': '51.3890'}
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
            'city': item.get('region', ''),
            'province': item.get('neighbourhood', ''),
            'website': '',
            'rating': '',
            'category': item.get('type', ''),
            'latitude': str(loc.get('y', '')),
            'longitude': str(loc.get('x', '')),
            'source': 'neshan',
        })
    return results
