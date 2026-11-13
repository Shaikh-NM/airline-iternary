import pytest

from apps.itineraries.algorithm.exceptions import InvalidItineraryError
from apps.itineraries.algorithm.graph_builder import build_adjacency_list
from apps.itineraries.algorithm.itinerary_builder import build_itinerary
from apps.itineraries.algorithm.validators import validate_itinerary


def solve(tickets):
    route = build_itinerary(build_adjacency_list(tickets))
    validate_itinerary(tickets, route)
    return route


def test_graph_is_sorted_descending():
    graph = build_adjacency_list([("JFK", "SFO"), ("JFK", "ATL"), ("JFK", "LAX")])
    assert graph == {"JFK": ["SFO", "LAX", "ATL"]}


def test_example_1():
    tickets = [("MUC", "LHR"), ("JFK", "MUC"), ("SFO", "SJC"), ("LHR", "SFO")]
    assert solve(tickets) == ["JFK", "MUC", "LHR", "SFO", "SJC"]


def test_example_2():
    tickets = [("JFK", "SFO"), ("JFK", "ATL"), ("SFO", "ATL"), ("ATL", "JFK"), ("ATL", "SFO")]
    assert solve(tickets) == ["JFK", "ATL", "JFK", "SFO", "ATL", "SFO"]


def test_dead_end_branch_is_visited_last():
    tickets = [("JFK", "KUL"), ("JFK", "NRT"), ("NRT", "JFK")]
    assert solve(tickets) == ["JFK", "NRT", "JFK", "KUL"]


def test_duplicate_tickets():
    tickets = [("JFK", "ATL"), ("ATL", "JFK"), ("JFK", "ATL")]
    assert solve(tickets) == ["JFK", "ATL", "JFK", "ATL"]


def test_builder_does_not_mutate_graph():
    graph = build_adjacency_list([("JFK", "ATL"), ("ATL", "SFO")])
    snapshot = {k: list(v) for k, v in graph.items()}
    build_itinerary(graph)
    assert graph == snapshot


def test_max_size_chain():
    airports = [f"{chr(65 + i // 26)}{chr(65 + i % 26)}X" for i in range(300)]
    stops = ["JFK"] + airports
    tickets = list(zip(stops, stops[1:]))
    assert len(tickets) == 300
    assert solve(tickets) == stops


def test_disconnected_tickets_fail_validation():
    tickets = [("JFK", "ATL"), ("SFO", "LAX")]
    with pytest.raises(InvalidItineraryError):
        solve(tickets)


def test_no_ticket_from_jfk_fails():
    with pytest.raises(InvalidItineraryError):
        solve([("ATL", "SFO")])


def test_validator_rejects_wrong_route():
    tickets = [("JFK", "ATL"), ("ATL", "SFO")]
    with pytest.raises(InvalidItineraryError):
        validate_itinerary(tickets, ["JFK", "SFO", "ATL"])
    with pytest.raises(InvalidItineraryError):
        validate_itinerary(tickets, ["ATL", "SFO"])
