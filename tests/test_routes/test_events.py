import datetime
from models import Event, User

def test_get_events_returns_all_events(client, session):
    """
    Test that GET /api/events returns a list of all events.

    This test creates two events in the database and verifies
    that the endpoint returns both events in the response.
    """

    event1 = Event(title="Event 1", date=datetime.datetime(2025, 5, 1))
    event2 = Event(title="Event 2", date=datetime.datetime(2025, 6, 1))

    session.add_all([event1, event2])
    session.commit()

    response = client.get("/api/events")
    data = response.get_json()

    assert response.status_code == 200
    assert len(data) == 2
    assert data[0]["title"] == "Event 1"

def test_get_single_event(client, session):
    """
    Test that GET /api/events/<id> returns the correct event.

    The test creates one event and ensures the API
    returns the correct event when queried by ID.
    """

    event = Event(title="Conference", date=datetime.datetime(2025, 7, 1))
    session.add(event)
    session.commit()

    response = client.get(f"/api/events/{event.id}")
    data = response.get_json()

    assert response.status_code == 200
    assert data["title"] == "Conference"
    assert data["id"] == event.id

def test_get_event_not_found(client):
    """
    Test that requesting a non-existent event returns 404.
    """

    response = client.get("/api/events/999")

    assert response.status_code == 404

def test_create_event_success(client, auth_headers):
    """
    Test that an authenticated user can create an event.
    """

    response = client.post(
        "/api/events",
        headers=auth_headers,
        json={
            "title": "Python Meetup",
            "date": "2026-05-01T18:00:00"
        }
    )

    data = response.get_json()

    assert response.status_code == 201
    assert data["title"] == "Python Meetup"

def test_create_event_requires_authentication(client):
    """
    Test that creating an event without a JWT token
    returns a 401 Unauthorized response.
    """

    response = client.post(
        "/api/events",
        json={
            "title": "Unauthorized Event",
            "date": "2026-05-01T18:00:00"
        }
    )

    assert response.status_code == 401

def test_create_event_missing_title(client, auth_headers):
    """
    Ensure API returns error when title is missing.
    """

    response = client.post(
        "/api/events",
        headers=auth_headers,
        json={
            "date": "2026-05-01T18:00:00"
        }
    )

    data = response.get_json()

    assert response.status_code == 400
    assert data["error"] == "Title is required"

def test_create_event_missing_date(client, session, auth_headers):
    """
    Test that the API returns a 400 error when
    the event date is missing.
    """

    user = User(username="charlie")
    user.set_password("pass")

    session.add(user)
    session.commit()

    response = client.post(
        "/api/events",
        headers=auth_headers,
        json={
            "title": "Event Without Date"
        }
    )

    data = response.get_json()

    assert response.status_code == 400
    assert data["error"] == "Date is required"

def test_create_event_invalid_date_format(client, session, auth_headers):
    """
    Test that the API returns a 400 error when
    the provided date format is invalid.
    """

    user = User(username="david")
    user.set_password("pass")

    session.add(user)
    session.commit()

    response = client.post(
        "/api/events",
        headers=auth_headers,
        json={
            "title": "Bad Date Event",
            "date": "not-a-date"
        }
    )

    data = response.get_json()

    assert response.status_code == 400
    assert "Invalid date format" in data["error"]