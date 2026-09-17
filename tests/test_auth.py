from app.models.user import User


def register(
    client,
    username="testuser",
    email="test@example.com",
    password="password123",
):
    return client.post(
        "/register",
        data={
            "username": username,
            "email": email,
            "password": password,
            "password_confirm": password,
        },
    )


def login(
    client,
    identifier="testuser",
    password="password123",
):
    return client.post(
        "/login",
        data={
            "identifier": identifier,
            "password": password,
        },
    )


def test_register_page(anonymous_client):
    response = anonymous_client.get("/register")

    assert response.status_code == 200


def test_register_creates_user(
    anonymous_client,
    app,
):
    response = register(anonymous_client)

    assert response.status_code == 302
    assert response.headers["Location"].endswith(
        "/login",
    )

    with app.app_context():
        user = User.query.filter_by(
            username="testuser",
        ).first()

        assert user is not None
        assert user.email == "test@example.com"
        assert user.role == User.ROLE_STUDENT
        assert user.password_hash != "password123"
        assert user.check_password("password123") is True


def test_duplicate_username_is_rejected(
    anonymous_client,
    app,
):
    register(anonymous_client)

    response = register(
        anonymous_client,
        email="second@example.com",
    )

    assert response.status_code == 200

    with app.app_context():
        count = User.query.filter_by(
            username="testuser",
        ).count()

        assert count == 1


def test_login_creates_session(
    anonymous_client,
):
    register(anonymous_client)

    response = login(anonymous_client)

    assert response.status_code == 302
    assert response.headers["Location"].endswith(
        "/dashboard",
    )

    with anonymous_client.session_transaction() as session:
        assert "user_id" in session


def test_dashboard_requires_login(
    anonymous_client,
):
    response = anonymous_client.get(
        "/dashboard",
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith(
        "/login",
    )


def test_dashboard_available_after_login(
    anonymous_client,
):
    register(anonymous_client)
    login(anonymous_client)

    response = anonymous_client.get(
        "/dashboard",
    )

    assert response.status_code == 200
    assert "StudentTrack" in response.get_data(
        as_text=True,
    )


def test_logout_clears_session(
    anonymous_client,
):
    register(anonymous_client)
    login(anonymous_client)

    response = anonymous_client.post(
        "/logout",
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith(
        "/login",
    )

    with anonymous_client.session_transaction() as session:
        assert "user_id" not in session


def test_registration_cannot_assign_admin_role(
    anonymous_client,
    app,
):
    response = anonymous_client.post(
        "/register",
        data={
            "username": "hacker",
            "email": "hacker@example.com",
            "password": "password123",
            "password_confirm": "password123",
            "role": "admin",
        },
    )

    assert response.status_code == 302

    with app.app_context():
        user = User.query.filter_by(
            username="hacker",
        ).first()

        assert user is not None
        assert user.role == User.ROLE_STUDENT