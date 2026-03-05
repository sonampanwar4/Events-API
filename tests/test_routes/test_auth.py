from models import User

def test_register_success(client, session):
    """Test that a user can successfully register with a valid username and password."""
    response = client.post(
        "/api/auth/register",
        json={
            "username": "alice",
            "password": "password123"
        }
    )

    data = response.get_json()


    assert response.status_code == 201
    assert data["message"] == "User created successfully"
    assert data["user"]["username"] == "alice"

    # verify user exists in database
    user = session.query(User).filter_by(username="alice").first()
    assert user is not None

def test_register_missing_fields(client):
    """Test that registration fails when required fields are missing."""
    response = client.post(
        "/api/auth/register",
        json={"username": "alice"}
    )

    data = response.get_json()

    assert response.status_code == 400
    assert data["error"] == "Username and password are required"

def test_register_duplicate_username(client, session):
    """Test that registering with an existing username is rejected."""
    user = User(username="alice")
    user.set_password("password")
    session.add(user)
    session.commit()

    response = client.post(
        "/api/auth/register",
        json={
            "username": "alice",
            "password": "newpass"
        }
    )

    data = response.get_json()

    assert response.status_code == 400
    assert data["error"] == "Username already exists"

def test_first_user_is_admin(client):
    """Test that the first registered user automatically becomes an admin."""
    response = client.post(
        "/api/auth/register",
        json={
            "username": "admin",
            "password": "password"
        }
    )

    data = response.get_json()

    assert response.status_code == 201
    assert data["user"]["is_admin"] is True


def test_login_success(client, session):
    """Test that a user can log in with valid credentials."""
    user = User(username="bob")
    user.set_password("secret")

    session.add(user)
    session.commit()

    response = client.post(
        "/api/auth/login",
        json={
            "username": "bob",
            "password": "secret"
        }
    )

    data = response.get_json()

    assert response.status_code == 200
    assert "access_token" in data
    assert data["user"]["username"] == "bob"


def test_login_invalid_credentials(client, session):
    """Test that login fails when the password is incorrect."""
    user = User(username="charlie")
    user.set_password("password")

    session.add(user)
    session.commit()

    response = client.post(
        "/api/auth/login",
        json={
            "username": "charlie",
            "password": "wrongpassword"
        }
    )

    data = response.get_json()

    assert response.status_code == 401
    assert data["error"] == "Invalid credentials"


def test_login_missing_fields(client):
    """Test that login fails when required fields are missing."""
    response = client.post(
        "/api/auth/login",
        json={"username": "alice"}
    )

    data = response.get_json()

    assert response.status_code == 400
    assert data["error"] == "Username and password are required"