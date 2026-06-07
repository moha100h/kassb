import aiohttp, logging, os

logger = logging.getLogger(__name__)
BASE = 'https://api.neshan.org/v1/search'

async def search_neshan(city: str, category: str, api_key: str = '', max_results: int = 200) -> list:
    key = api_key or os.environ.get('NESHAN_API_KEY', '')
    if not key or key == 'your_neshan_api_key_here':
        logger.warning('Neshan: NESHAN_API_KEY not set, skipping')
        return []
    headers = {'Api-Key': key}
    params  = {'term': f'{category} {city}', 'lat': '35.6892', 'lng': '51.3890'}
    logger.info(f'Neshan search: {category} in {city}')
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(BASE, headers=headers, params=params,
                                   timeout=aiohttp.ClientTimeout(total=15)) as r:
                logger.info(f'Neshan HTTP {r.status}')
                if r.status != 200:
                    body = await r.text()
                    logger.warning(f'Neshan error body: {body[:200]}')
                    return []
                data = await r.json()
    except Exception as e:
        logger.warning(f'Neshan exception: {e}')
        return []

    items = data.get('items') or []
    logger.info(f'Neshan returned {len(items)} items')
    results = []
    for item in items[:max_results]:
        loc = item.get('location') or {}
        results.append({
            'name':      item.get('title', ''),
            'phone':     '',
            'address':   item.get('address', ''),
            'city':      item.get('region', ''),
            'province':  item.get('neighbourhood', ''),
            'website':   '',
            'rating':    '',
            'category':  item.get('type', ''),
            'latitude':  str(loc.get('y', '')),
            'longitude': str(loc.get('x', '')),
            'source':    'neshan',
        })
    return results
