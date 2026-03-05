import datetime
from models import Event, RSVP, User

def test_rsvp_public_event_anonymous(client, session):
    """
    Test that an anonymous user can RSVP to a public event.
    """

    event = Event(
        title="Public Event",
        date=datetime.datetime(2026, 5, 1),
        is_public=True
    )

    session.add(event)
    session.commit()

    response = client.post(
        f"/api/rsvps/event/{event.id}",
        json={}
    )

    data = response.get_json()

    assert response.status_code == 201
    assert data["event_id"] == event.id
    assert data["attending"] is True

def test_rsvp_authenticated_user(client, session, auth_headers, user):
    """
    Test that an authenticated user can RSVP to an event.
    """

    event = Event(
        title="Auth Event",
        date=datetime.datetime(2026, 6, 1)
    )

    session.add(event)
    session.commit()

    response = client.post(
        f"/api/rsvps/event/{event.id}",
        json={},
        headers=auth_headers
    )

    data = response.get_json()

    assert response.status_code == 201
    assert data["user_id"] == user["id"]

def test_update_existing_rsvp(client, session, auth_headers, user):
    """
    Test that submitting RSVP again updates the existing RSVP.
    """

    event = Event(
        title="Update RSVP Event",
        date=datetime.datetime(2026, 7, 1)
    )

    session.add(event)
    session.commit()

    rsvp = RSVP(
        event_id=event.id,
        user_id=user["id"],
        attending=True
    )

    session.add(rsvp)
    session.commit()

    response = client.post(
        f"/api/rsvps/event/{event.id}",
        headers=auth_headers,
        json={"attending": False}
    )

    data = response.get_json()

    assert response.status_code == 200
    assert data["attending"] is False

def test_rsvp_private_event_requires_auth(client, session):
    """
    Ensure RSVP fails for private events when user is not authenticated.
    """

    event = Event(
        title="Private Event",
        date=datetime.datetime(2026, 8, 1),
        is_public=False
    )

    session.add(event)
    session.commit()

    response = client.post(f"/api/rsvps/event/{event.id}", json={})

    data = response.get_json()

    assert response.status_code == 401
    assert "Authentication required" in data["error"]

def test_rsvp_admin_event_requires_admin(client, session, auth_headers):
    """
    Ensure non-admin users cannot RSVP to admin-only events.
    """

    event = Event(
        title="Admin Event",
        date=datetime.datetime(2026, 9, 1),
        requires_admin=True
    )

    session.add(event)
    session.commit()

    response = client.post(
        f"/api/rsvps/event/{event.id}",
        json={},
        headers=auth_headers
    )

    data = response.get_json()

    assert response.status_code == 403
    assert "Admin access required" in data["error"]

def test_rsvp_event_capacity_limit(client, session, auth_headers, user):
    """
    Ensure RSVP fails when event has reached capacity.
    """

    event = Event(
        title="Limited Event",
        date=datetime.datetime(2026, 10, 1),
        capacity=1
    )

    session.add(event)
    session.commit()

    # Fill capacity
    rsvp = RSVP(
        event_id=event.id,
        user_id=user["id"],
        attending=True
    )

    session.add(rsvp)
    session.commit()

    response = client.post(
        f"/api/rsvps/event/{event.id}",
        json={},
        headers=auth_headers
    )

    data = response.get_json()

    assert response.status_code == 400
    assert "full capacity" in data["error"]

def test_get_rsvps_for_event(client, session, user):
    """
    Test that GET /api/rsvps/event/<id> returns RSVP list and statistics.
    """

    event = Event(
        title="RSVP Stats Event",
        date=datetime.datetime(2026, 11, 1)
    )

    session.add(event)
    session.commit()

    rsvp1 = RSVP(event_id=event.id, user_id=user["id"], attending=True)
    rsvp2 = RSVP(event_id=event.id, user_id=None, attending=False)

    session.add_all([rsvp1, rsvp2])
    session.commit()

    response = client.get(f"/api/rsvps/event/{event.id}", json={})

    data = response.get_json()

    assert response.status_code == 200
    assert data["stats"]["attending"] == 1
    assert data["stats"]["not_attending"] == 1
    assert data["stats"]["total"] == 2