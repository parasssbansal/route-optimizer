from __future__ import annotations

import itertools
import math


class TSPSolver:
    def solve(self, distance_matrix: list[list[float]]) -> tuple[list[int], float]:
        location_count = len(distance_matrix)
        if location_count == 0:
            return [], 0.0
        if location_count == 1:
            return [0], 0.0
        if location_count == 2:
            return [0, 1], distance_matrix[0][1]
        if location_count <= 3:
            return self._solve_small(distance_matrix)
        return self._solve_dp(distance_matrix)

    def _solve_small(self, distance_matrix: list[list[float]]) -> tuple[list[int], float]:
        location_count = len(distance_matrix)
        best_order: list[int] | None = None
        best_cost = math.inf

        for permutation in itertools.permutations(range(1, location_count)):
            order = [0, *permutation]
            cost = self._calculate_path_cost(order, distance_matrix)
            if cost < best_cost:
                best_cost = cost
                best_order = list(order)

        return best_order or [0], best_cost if best_cost != math.inf else 0.0

    def _solve_dp(self, distance_matrix: list[list[float]]) -> tuple[list[int], float]:
        location_count = len(distance_matrix)
        memo: dict[tuple[int, int], float] = {}
        parent: dict[tuple[int, int], int] = {}

        for node in range(1, location_count):
            mask = (1 << 0) | (1 << node)
            memo[(mask, node)] = distance_matrix[0][node]
            parent[(mask, node)] = 0

        for subset_size in range(3, location_count + 1):
            for subset in itertools.combinations(range(1, location_count), subset_size - 1):
                mask = 1
                for node in subset:
                    mask |= 1 << node

                for last in subset:
                    prev_mask = mask ^ (1 << last)
                    best_cost = math.inf
                    best_prev = -1

                    for prev in subset:
                        if prev == last:
                            continue
                        candidate = memo[(prev_mask, prev)] + distance_matrix[prev][last]
                        if candidate < best_cost:
                            best_cost = candidate
                            best_prev = prev

                    memo[(mask, last)] = best_cost
                    parent[(mask, last)] = best_prev

        full_mask = (1 << location_count) - 1
        end_node = min(
            range(1, location_count),
            key=lambda node: memo[(full_mask, node)],
        )
        best_cost = memo[(full_mask, end_node)]

        order = [end_node]
        mask = full_mask
        last = end_node

        while last != 0:
            prev = parent[(mask, last)]
            order.append(prev)
            mask ^= 1 << last
            last = prev

        order.reverse()
        return order, round(best_cost, 3)

    @staticmethod
    def _calculate_path_cost(order: list[int], distance_matrix: list[list[float]]) -> float:
        total = 0.0
        for index in range(len(order) - 1):
            total += distance_matrix[order[index]][order[index + 1]]
        return round(total, 3)
