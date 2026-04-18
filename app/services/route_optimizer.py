from __future__ import annotations

import asyncio

from app.services.osrm_service import OSRMService
from app.services.tsp_solver import TSPSolver


class RouteOptimizerService:
    def __init__(self) -> None:
        self.osrm_service = OSRMService()
        self.tsp_solver = TSPSolver()
        self.max_locations = 10

    async def optimize(self, locations: list[list[float]]) -> dict[str, list[list[float]] | float]:
        if not locations:
            raise ValueError("At least one location is required.")
        if len(locations) > self.max_locations:
            raise ValueError(f"A maximum of {self.max_locations} locations is supported per request.")
        if len(locations) == 1:
            return {"optimal_route": locations, "total_distance_km": 0.0}

        distance_matrix = await self._build_distance_matrix(locations)
        order, total_distance_km = self.tsp_solver.solve(distance_matrix)
        ordered_locations = [locations[index] for index in order]

        try:
            route_geometry = await self.osrm_service.get_route_geometry(ordered_locations)
        except RuntimeError:
            route_geometry = ordered_locations

        return {
            "optimal_route": route_geometry,
            "total_distance_km": round(total_distance_km, 3),
        }

    async def _build_distance_matrix(self, locations: list[list[float]]) -> list[list[float]]:
        location_count = len(locations)
        matrix = [[0.0 for _ in range(location_count)] for _ in range(location_count)]
        tasks: list[tuple[int, int, asyncio.Task[float]]] = []

        for i in range(location_count):
            for j in range(i + 1, location_count):
                task = asyncio.create_task(self.osrm_service.get_distance_km(locations[i], locations[j]))
                tasks.append((i, j, task))

        for i, j, task in tasks:
            distance = await task
            matrix[i][j] = distance
            matrix[j][i] = distance

        return matrix
