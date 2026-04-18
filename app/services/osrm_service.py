from __future__ import annotations

import asyncio
from collections import OrderedDict

import httpx

from app.utils.coordinate import format_osrm_coordinate, normalize_coordinate


class DistanceCache:
    def __init__(self, max_size: int = 4096) -> None:
        self.max_size = max_size
        self._cache: OrderedDict[tuple[tuple[float, float], tuple[float, float]], float] = OrderedDict()

    def get(self, start: list[float], end: list[float]) -> float | None:
        key = self._make_key(start, end)
        if key not in self._cache:
            return None
        value = self._cache.pop(key)
        self._cache[key] = value
        return value

    def set(self, start: list[float], end: list[float], distance_km: float) -> None:
        key = self._make_key(start, end)
        if key in self._cache:
            self._cache.pop(key)
        self._cache[key] = distance_km
        reverse_key = self._make_key(end, start)
        if reverse_key in self._cache:
            self._cache.pop(reverse_key)
        self._cache[reverse_key] = distance_km
        while len(self._cache) > self.max_size:
            self._cache.popitem(last=False)

    @staticmethod
    def _make_key(start: list[float], end: list[float]) -> tuple[tuple[float, float], tuple[float, float]]:
        return normalize_coordinate(start), normalize_coordinate(end)


class OSRMService:
    def __init__(self, base_url: str = "https://router.project-osrm.org") -> None:
        self.base_url = base_url.rstrip("/")
        self.distance_cache = DistanceCache()
        self._client = httpx.AsyncClient(timeout=httpx.Timeout(12.0, connect=5.0))
        self._semaphore = asyncio.Semaphore(3)

    async def close(self) -> None:
        await self._client.aclose()

    async def get_distance_km(self, start: list[float], end: list[float]) -> float:
        cached_distance = self.distance_cache.get(start, end)
        if cached_distance is not None:
            return cached_distance

        coords = f"{format_osrm_coordinate(start)};{format_osrm_coordinate(end)}"
        url = f"{self.base_url}/route/v1/driving/{coords}"
        params = {"overview": "false"}

        try:
            async with self._semaphore:
                response = await self._client.get(url, params=params)
            response.raise_for_status()
            payload = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise RuntimeError("Unable to fetch route distance from OSRM.") from exc

        routes = payload.get("routes")
        if not routes:
            raise RuntimeError("OSRM returned an empty routing response.")

        distance_meters = routes[0].get("distance")
        if distance_meters is None:
            raise RuntimeError("OSRM response did not include route distance.")

        distance_km = round(distance_meters / 1000, 3)
        self.distance_cache.set(start, end, distance_km)
        return distance_km

    async def get_route_geometry(self, ordered_locations: list[list[float]]) -> list[list[float]]:
        if len(ordered_locations) < 2:
            return ordered_locations

        coords = ";".join(format_osrm_coordinate(location) for location in ordered_locations)
        url = f"{self.base_url}/route/v1/driving/{coords}"
        params = {"overview": "full", "geometries": "geojson"}

        try:
            async with self._semaphore:
                response = await self._client.get(url, params=params)
            response.raise_for_status()
            payload = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise RuntimeError("Unable to fetch route geometry from OSRM.") from exc

        routes = payload.get("routes")
        if not routes:
            raise RuntimeError("OSRM returned an empty geometry response.")

        geometry = routes[0].get("geometry", {})
        coordinates = geometry.get("coordinates")
        if not coordinates:
            raise RuntimeError("OSRM response did not include route geometry.")

        return [[lat, lon] for lon, lat in coordinates]
