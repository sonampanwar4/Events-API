import datetime
from models import Event, User, RSVP

def test_create_event(session):
    """Test an event creation."""
    event = Event(
        title="Python Meetup",
        description="Learn pytest",
        date=datetime.datetime(2026, 5, 1, 18, 0),
        location="Berlin",
        capacity=50
    )

    session.add(event)
    session.commit()
    saved_event = session.query(Event).first()

    assert saved_event is not None
    assert saved_event.title == "Python Meetup"
    assert saved_event.capacity == 50

def test_event_defaults(session):
    """Test default values."""
    event = Event(
        title="Test Event",
        date=datetime.datetime(2026, 2, 1)
    )

    session.add(event)
    session.commit()
    saved = session.query(Event).first()

    assert saved.is_public is True
    assert saved.requires_admin is False


def test_event_to_dict(session):
    """Test an event to store as dictionary."""
    event = Event(
        title="Conference",
        description="Tech conference",
        date=datetime.datetime(2026, 2, 10),
        location="Hamburg",
        capacity=100
    )

    session.add(event)
    session.commit()

    data = event.to_dict()

    assert data["title"] == "Conference"
    assert data["description"] == "Tech conference"
    assert data["location"] == "Hamburg"
    assert data["capacity"] == 100
    assert data["rsvp_count"] == 0
    assert data["attendees"] == []

def test_event_rsvp_count(session):
    """Test for count RSVP for an event."""
    user = User(username="alice")
    user.set_password("pass")

    event = Event(
        title="Party",
        date=datetime.datetime(2026, 8, 1)
    )

    session.add_all([user, event])
    session.commit()

    rsvp = RSVP(user_id=user.id, event_id=event.id, attending=True)

    session.add(rsvp)
    session.commit()

    assert event.to_dict()["rsvp_count"] == 1


def test_event_attendees_list(session):
    """ Test Attendees list for an event. """
    user1 = User(username="alice")
    user1.set_password("pass")

    user2 = User(username="bob")
    user2.set_password("pass")

    event = Event(
        title="Workshop",
        date=datetime.datetime(2026, 9, 1)
    )

    session.add_all([user1, user2, event])
    session.commit()

    rsvp1 = RSVP(user_id=user1.id, event_id=event.id, attending=True)
    rsvp2 = RSVP(user_id=user2.id, event_id=event.id, attending=False)

    session.add_all([rsvp1, rsvp2])
    session.commit()

    data = event.to_dict()

    assert data["rsvp_count"] == 2
    assert data["attendees"] == [user1.id]

def test_event_delete_cascades_rsvp(session):
    """ Test for deleting an event deletes RSVPs. """
    user = User(username="alice")
    user.set_password("pass")

    event = Event(
        title="Delete Test",
        date=datetime.datetime(2026, 10, 1)
    )

    session.add_all([user, event])
    session.commit()

    rsvp = RSVP(user_id=user.id, event_id=event.id)

    session.add(rsvp)
    session.commit()

    session.delete(event)
    session.commit()

    remaining_rsvp = session.query(RSVP).count()

    assert remaining_rsvp == 0