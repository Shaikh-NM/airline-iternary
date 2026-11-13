from collections import defaultdict
from typing import Dict, Iterable, List, Tuple


def build_adjacency_list(tickets: Iterable[Tuple[str, str]]) -> Dict[str, List[str]]:
    """Build a directed multigraph as {airport: [destinations]}.

    Each destination list is sorted in DESCENDING lexical order so the
    smallest destination can be taken with an O(1) ``list.pop()``.
    Duplicate tickets are kept as separate edges.
    """
    graph: Dict[str, List[str]] = defaultdict(list)
    for origin, destination in tickets:
        graph[origin].append(destination)
    for destinations in graph.values():
        destinations.sort(reverse=True)
    return dict(graph)
