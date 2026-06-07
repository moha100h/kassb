import aiohttp, asyncio, logging

logger = logging.getLogger(__name__)
NOMINATIM = "https://nominatim.openstreetmap.org/search"
OVERPASS  = "https://overpass-api.de/api/interpreter"
HEADERS   = {"User-Agent": "KassbBot/1.0"}

def _norm_phone(p):
    if not p: return ""
    d = "".join(c for c in p if c.isdigit())
    if len(d) == 11 and d.startswith("0"): return "+98" + d[1:]
    if len(d) == 10: return "+98" + d
    if len(d) == 12 and d.startswith("98"): return "+" + d
    return p

async def _nominatim(session, city, category, limit=50):
    params = {"q": f"{category} {city}", "format": "json", "limit": limit,
              "addressdetails": 1, "extratags": 1, "namedetails": 1}
    try:
        async with session.get(NOMINATIM, params=params, headers=HEADERS,
                               timeout=aiohttp.ClientTimeout(total=30)) as r:
            if r.status == 200:
                return await r.json()
    except Exception as e:
        logger.warning(f"Nominatim: {e}")
    return []

async def _overpass(session, city, category):
    ql = (f'[out:json][timeout:30];area[name="{city}"]->.a;'
          f'(node["amenity"](area.a);way["amenity"](area.a);'
          f'node["shop"](area.a);node["name"~"{category}",i](area.a););'
          f'out body;>;out skel qt;')
    try:
        async with session.post(OVERPASS, timeout=aiohttp.ClientTimeout(total=35),
                                 data=ql) as r:
            if r.status == 200:
                data = await r.json()
                return data.get("elements", [])
    except Exception as e:
        logger.warning(f"Overpass: {e}")
    return []

async def search_osm(city, category, max_results=200):
    seen, results = set(), []
    async with aiohttp.ClientSession() as session:
        nom, ovr = await asyncio.gather(
            _nominatim(session, city, category, 50),
            _overpass(session, city, category)
        )
    for d in nom:
        tags = d.get("extratags") or {}
        nd   = d.get("namedetails") or {}
        name = nd.get("name:fa") or nd.get("name") or d.get("display_name", "").split(",")[0].strip()
        if not name: continue
        key = (name.lower(), d.get("lat", ""))
        if key in seen: continue
        seen.add(key)
        addr = d.get("address") or {}
        results.append({
            "name": name,
            "phone": _norm_phone(tags.get("phone", "") or tags.get("contact:phone", "")),
            "address": d.get("display_name", ""),
            "city": addr.get("city") or addr.get("town") or addr.get("village", ""),
            "province": addr.get("state", ""),
            "website": tags.get("website", "") or tags.get("contact:website", ""),
            "rating": "",
            "category": d.get("type", "") or tags.get("amenity", "") or tags.get("shop", ""),
            "latitude": d.get("lat", ""),
            "longitude": d.get("lon", ""),
            "source": "nominatim",
        })
    for d in ovr:
        tags = d.get("tags") or {}
        name = tags.get("name:fa") or tags.get("name", "")
        if not name: continue
        lat = str(d.get("lat", "") or (d.get("center") or {}).get("lat", ""))
        key = (name.lower(), lat)
        if key in seen: continue
        seen.add(key)
        results.append({
            "name": name,
            "phone": _norm_phone(tags.get("phone", "") or tags.get("contact:phone", "")),
            "address": ", ".join(filter(None, [tags.get("addr:street", ""), tags.get("addr:housenumber", ""), tags.get("addr:city", "")])),
            "city": tags.get("addr:city", ""),
            "province": tags.get("addr:province", ""),
            "website": tags.get("website", "") or tags.get("contact:website", ""),
            "rating": "",
            "category": tags.get("amenity", "") or tags.get("shop", ""),
            "latitude": lat,
            "longitude": str(d.get("lon", "") or (d.get("center") or {}).get("lon", "")),
            "source": "overpass",
        })
    return results[:max_results]
