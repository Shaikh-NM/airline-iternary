from typing import Dict, List

START_AIRPORT = "JFK"


def build_itinerary(graph: Dict[str, List[str]], start: str = START_AIRPORT) -> List[str]:
    """Hierholzer's algorithm for an Eulerian path starting at ``start``.

    Always walking to the lexically smallest unused destination and
    appending airports in post-order (then reversing) yields the
    lexically smallest valid itinerary. Runs in O(E log E) including
    the sort done by the graph builder.

    The input graph is not mutated. If the tickets do not form a single
    path from ``start``, the returned route will be shorter than
    ``tickets + 1``; callers must run ``validate_itinerary``.
    """
    remaining = {airport: list(dests) for airport, dests in graph.items()}
    stack = [start]
    route: List[str] = []
    while stack:
        while remaining.get(stack[-1]):
            stack.append(remaining[stack[-1]].pop())
        route.append(stack.pop())
    route.reverse()
    return route
