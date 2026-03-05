import pytest
from sqlalchemy.exc import IntegrityError
from models import User


def test_create_user(session):
    user = User(username="alice")
    user.set_password("secret123")

    session.add(user)
    session.commit()

    saved_user = session.query(User).filter_by(username="alice").first()

    assert saved_user is not None
    assert saved_user.username == "alice"

def test_set_password_hashes_password():
    user = User(username="bob")
    user.set_password("mypass123")

    assert user.password_hash != "mypass123"
    assert user.password_hash is not None

def test_check_password():
    user = User(username="charlie")
    user.set_password("secret123")

    assert user.check_password("secret123") is True
    assert user.check_password("mypass123") is False

def test_to_dict(session):
    user = User(username="david", is_admin=True)
    user.set_password("pass123")

    session.add(user)
    session.commit()

    data = user.to_dict()

    assert data["username"] == "david"
    assert data["is_admin"] is True
    assert "id" in data
    assert "created_at" in data

def test_username_unique(session):
    user1 = User(username="alice")
    user1.set_password("mypass123")

    user2 = User(username="alice")
    user2.set_password("mypass456")

    session.add(user1)
    session.commit()

    session.add(user2)

    with pytest.raises(IntegrityError):
        session.commit()
