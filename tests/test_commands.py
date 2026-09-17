from app.extensions import db
from app.models.user import User


def test_create_admin_command(
    app,
):
    runner = app.test_cli_runner()

    result = runner.invoke(
        args=[
            "create-admin",
            "root",
            "root@example.com",
            "--password",
            "password123",
        ],
    )

    assert result.exit_code == 0
    assert "Администратор root создан." in result.output

    with app.app_context():
        user = User.query.filter_by(
            username="root",
        ).first()

        assert user is not None
        assert user.role == User.ROLE_ADMIN
        assert user.check_password(
            "password123"
        ) is True


def test_create_admin_rejects_short_password(
    app,
):
    runner = app.test_cli_runner()

    result = runner.invoke(
        args=[
            "create-admin",
            "root",
            "root@example.com",
            "--password",
            "123",
        ],
    )

    assert result.exit_code != 0
    assert "минимум 8 символов" in result.output


def test_create_admin_rejects_duplicate_username(
    app,
):
    runner = app.test_cli_runner()

    runner.invoke(
        args=[
            "create-admin",
            "root",
            "root@example.com",
            "--password",
            "password123",
        ],
    )

    result = runner.invoke(
        args=[
            "create-admin",
            "root",
            "other@example.com",
            "--password",
            "password123",
        ],
    )

    assert result.exit_code != 0


def test_set_role_command(
    app,
):
    with app.app_context():
        user = User(
            username="teacher_candidate",
            email="candidate@example.com",
            role=User.ROLE_STUDENT,
        )

        user.set_password("password123")

        db.session.add(user)
        db.session.commit()

    runner = app.test_cli_runner()

    result = runner.invoke(
        args=[
            "set-role",
            "teacher_candidate",
            "teacher",
        ],
    )

    assert result.exit_code == 0

    with app.app_context():
        user = User.query.filter_by(
            username="teacher_candidate",
        ).first()

        assert user.role == User.ROLE_TEACHER


def test_set_role_unknown_user(
    app,
):
    runner = app.test_cli_runner()

    result = runner.invoke(
        args=[
            "set-role",
            "missing",
            "teacher",
        ],
    )

    assert result.exit_code != 0
    assert "Пользователь не найден" in result.output