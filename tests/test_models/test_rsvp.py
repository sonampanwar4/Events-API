import datetime
from models import RSVP, User, Event


def test_create_rsvp(session):
    user = User(username="alice")
    user.set_password("pass")

    event = Event(title="Meetup", date=datetime.datetime(2026, 1, 1))

    session.add_all([user, event])
    session.commit()

    rsvp = RSVP(user_id=user.id, event_id=event.id)

    session.add(rsvp)
    session.commit()

    saved = session.query(RSVP).first()

    assert saved.user_id == user.id
    assert saved.event_id == event.id


def test_rsvp_default_attending(session):
    event = Event(title="Test", date=datetime.datetime(2026, 3, 1))

    session.add(event)
    session.commit()

    rsvp = RSVP(event_id=event.id)

    session.add(rsvp)
    session.commit()

    assert rsvp.attending is True


def test_rsvp_to_dict(session):
    event = Event(title="Event", date=datetime.datetime(2026, 2, 1))

    session.add(event)
    session.commit()

    rsvp = RSVP(event_id=event.id, attending=False)

    session.add(rsvp)
    session.commit()

    data = rsvp.to_dict()

    assert data["event_id"] == event.id
    assert data["attending"] is False