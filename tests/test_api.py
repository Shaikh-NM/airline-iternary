import uuid

import pytest
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db

TICKETS_URL = "/api/v1/tickets/"
RECONSTRUCT_URL = "/api/v1/itineraries/reconstruct/"
EXAMPLE_2 = [["JFK", "SFO"], ["JFK", "ATL"], ["SFO", "ATL"], ["ATL", "JFK"], ["ATL", "SFO"]]


@pytest.fixture
def client():
    return APIClient()


def submit(client, tickets):
    return client.post(TICKETS_URL, {"tickets": tickets}, format="json")


def test_submit_and_retrieve_tickets(client):
    res = submit(client, EXAMPLE_2)
    assert res.status_code == 201
    assert res.data["ticket_count"] == 5
    assert res.data["tickets"] == EXAMPLE_2

    got = client.get(TICKETS_URL, {"batch_id": res.data["batch_id"]})
    assert got.status_code == 200
    assert got.data["tickets"] == EXAMPLE_2


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"tickets": []},
        {"tickets": [["JFK"]]},
        {"tickets": [["JFK", "JFK"]]},
        {"tickets": [["jfk", "atl"]]},
        {"tickets": [["JFKK", "ATL"]]},
        {"tickets": [["JF1", "ATL"]]},
        {"tickets": [["JFK", "ATL"]] * 301},
    ],
)
def test_invalid_ticket_payloads_rejected(client, payload):
    res = client.post(TICKETS_URL, payload, format="json")
    assert res.status_code == 400


def test_get_tickets_requires_valid_known_batch(client):
    assert client.get(TICKETS_URL).status_code == 400
    assert client.get(TICKETS_URL, {"batch_id": "not-a-uuid"}).status_code == 400
    assert client.get(TICKETS_URL, {"batch_id": str(uuid.uuid4())}).status_code == 404


def test_reconstruct_and_retrieve_itinerary(client):
    batch_id = submit(client, EXAMPLE_2).data["batch_id"]

    res = client.post(RECONSTRUCT_URL, {"batch_id": batch_id}, format="json")
    assert res.status_code == 201
    assert res.data["status"] == "COMPLETED"
    assert res.data["route"] == ["JFK", "ATL", "JFK", "SFO", "ATL", "SFO"]

    got = client.get(f"/api/v1/itineraries/{res.data['id']}/")
    assert got.status_code == 200
    assert got.data["route"] == res.data["route"]


def test_reconstruct_is_idempotent(client):
    batch_id = submit(client, EXAMPLE_2).data["batch_id"]
    first = client.post(RECONSTRUCT_URL, {"batch_id": batch_id}, format="json")
    second = client.post(RECONSTRUCT_URL, {"batch_id": batch_id}, format="json")
    assert second.status_code == 200
    assert second.data["id"] == first.data["id"]


def test_unreconstructable_batch_is_failed(client):
    batch_id = submit(client, [["JFK", "ATL"], ["SFO", "LAX"]]).data["batch_id"]
    res = client.post(RECONSTRUCT_URL, {"batch_id": batch_id}, format="json")
    assert res.status_code == 422
    assert res.data["status"] == "FAILED"
    assert res.data["error_message"]

    got = client.get(f"/api/v1/itineraries/{res.data['id']}/")
    assert got.data["status"] == "FAILED"


def test_reconstruct_unknown_or_invalid_batch(client):
    res = client.post(RECONSTRUCT_URL, {"batch_id": str(uuid.uuid4())}, format="json")
    assert res.status_code == 404
    assert client.post(RECONSTRUCT_URL, {"batch_id": "x"}, format="json").status_code == 400


def test_unknown_itinerary_404(client):
    assert client.get(f"/api/v1/itineraries/{uuid.uuid4()}/").status_code == 404
