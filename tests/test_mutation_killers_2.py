"""Вторая волна тестов для убийства выживших мутаций.

Цель — закрыть edge cases в routes/auth.py и routes/admin.py,
которые показал pytest-gremlins:
- логин по email (а не по username)
- границы длины email (120 символов)
- редиректы после логина/регистрации с проверкой Location
- админские операции: смена роли, привязка к студенту
"""
from app.extensions import db
from app.models.student import Student
from app.models.user import User


def _register_and_login(client, username, email, password="password123"):
    """Регистрирует и логинит пользователя, возвращает response логина."""
    client.post(
        "/register",
        data={
            "username": username,
            "email": email,
            "password": password,
            "password_confirm": password,
        },
    )
    return client.post(
        "/login",
        data={"identifier": username, "password": password},
    )


# ---------------------------------------------------- auth.py: логин по email


def test_login_by_email_works(anonymous_client, app):
    """Логин работает не только по username, но и по email."""
    _register_and_login(
        anonymous_client,
        username="emailuser",
        email="emailuser@example.com",
    )
    anonymous_client.post("/logout")

    response = anonymous_client.post(
        "/login",
        data={
            "identifier": "emailuser@example.com",
            "password": "password123",
        },
    )
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/dashboard")


def test_login_by_email_case_insensitive(anonymous_client):
    """Логин по email не зависит от регистра."""
    _register_and_login(
        anonymous_client,
        username="caseuser",
        email="CaseUser@Example.com",
    )
    anonymous_client.post("/logout")

    response = anonymous_client.post(
        "/login",
        data={
            "identifier": "caseuser@example.com",
            "password": "password123",
        },
    )
    assert response.status_code == 302


def test_login_wrong_email_does_not_login(anonymous_client):
    """Неверный email не пускает в систему."""
    _register_and_login(
        anonymous_client,
        username="wrongmailuser",
        email="wrongmail@example.com",
    )
    anonymous_client.post("/logout")

    response = anonymous_client.post(
        "/login",
        data={
            "identifier": "othermail@example.com",
            "password": "password123",
        },
    )
    assert response.status_code == 200
    with anonymous_client.session_transaction() as session:
        assert "user_id" not in session


# ---------------------------------------------------- auth.py: границы email


def test_register_email_exactly_120_accepted(anonymous_client, app):
    """email ровно 120 символов принимается."""
    # 120 символов: 110 до @ + @ + 9 после
    local = "a" * 110
    domain = "b.com"  # 5 символов
    email = f"{local}@{domain}"  # 110+1+5 = 116 — уточним
    # Соберём ровно 120: 110 + 1 + 9
    email = "a" * 110 + "@" + "b" * 7 + ".com"  # 110+1+7+4 = 122 — пересчёт
    # Проще: собираем строку длины 120
    tail = "@example.com"  # 12 символов
    email = "x" * (120 - len(tail)) + tail  # 108 + 12 = 120
    assert len(email) == 120

    response = anonymous_client.post(
        "/register",
        data={
            "username": "email120",
            "email": email,
            "password": "password123",
            "password_confirm": "password123",
        },
    )
    assert response.status_code == 302


def test_register_email_121_rejected(anonymous_client, app):
    """email 121 символ отклоняется (> 120)."""
    tail = "@example.com"
    email = "x" * (121 - len(tail)) + tail
    assert len(email) == 121

    response = anonymous_client.post(
        "/register",
        data={
            "username": "email121",
            "email": email,
            "password": "password123",
            "password_confirm": "password123",
        },
    )
    assert response.status_code == 200
    with app.app_context():
        assert User.query.filter_by(username="email121").count() == 0


def test_register_email_empty_rejected(anonymous_client, app):
    """Пустой email отклоняется."""
    response = anonymous_client.post(
        "/register",
        data={
            "username": "emptymail",
            "email": "",
            "password": "password123",
            "password_confirm": "password123",
        },
    )
    assert response.status_code == 200
    with app.app_context():
        assert User.query.filter_by(username="emptymail").count() == 0


# ---------------------------------------------------- auth.py: редиректы


def test_login_redirects_to_dashboard_not_other(anonymous_client):
    """После логина редирект именно на /dashboard."""
    _register_and_login(
        anonymous_client,
        username="rediruser",
        email="rediruser@example.com",
    )
    # вышли — логинимся заново, ловим Location
    anonymous_client.post("/logout")

    response = anonymous_client.post(
        "/login",
        data={"identifier": "rediruser", "password": "password123"},
    )
    assert response.status_code == 302
    location = response.headers["Location"]
    assert location.endswith("/dashboard")
    # Явно убеждаемся, что не редирект на /login
    assert not location.endswith("/login")


def test_register_redirects_to_login(anonymous_client):
    """После регистрации редирект именно на /login."""
    response = anonymous_client.post(
        "/register",
        data={
            "username": "regredir",
            "email": "regredir@example.com",
            "password": "password123",
            "password_confirm": "password123",
        },
    )
    assert response.status_code == 302
    location = response.headers["Location"]
    assert location.endswith("/login")
    assert not location.endswith("/dashboard")


# ---------------------------------------------------- admin.py: смена роли


def _make_admin(app):
    """Создаёт админа и возвращает (client, admin_id)."""
    with app.app_context():
        admin = User(
            username="theadmin",
            email="theadmin@example.com",
            role=User.ROLE_ADMIN,
        )
        admin.set_password("adminpass123")
        db.session.add(admin)
        db.session.commit()
        admin_id = admin.id

    client = app.test_client()
    with client.session_transaction() as session:
        session["user_id"] = admin_id

    return client, admin_id


def test_admin_can_change_student_to_teacher(app):
    """Админ меняет роль student → teacher."""
    client, _ = _make_admin(app)

    with app.app_context():
        target = User(
            username="target_student",
            email="target_student@example.com",
            role=User.ROLE_STUDENT,
        )
        target.set_password("password123")
        db.session.add(target)
        db.session.commit()
        target_id = target.id

    response = client.put(
        f"/admin/users/{target_id}/role",
        json={"role": "teacher"},
    )
    assert response.status_code == 200

    with app.app_context():
        user = db.session.get(User, target_id)
        assert user.role == User.ROLE_TEACHER


def test_admin_can_change_teacher_to_student(app):
    """Админ меняет роль teacher → student."""
    client, _ = _make_admin(app)

    with app.app_context():
        target = User(
            username="target_teacher",
            email="target_teacher@example.com",
            role=User.ROLE_TEACHER,
        )
        target.set_password("password123")
        db.session.add(target)
        db.session.commit()
        target_id = target.id

    response = client.put(
        f"/admin/users/{target_id}/role",
        json={"role": "student"},
    )
    assert response.status_code == 200

    with app.app_context():
        user = db.session.get(User, target_id)
        assert user.role == User.ROLE_STUDENT


def test_admin_change_role_invalid_role_rejected(app):
    """Невалидная роль отклоняется."""
    client, _ = _make_admin(app)

    with app.app_context():
        target = User(
            username="invalidrole_target",
            email="invalidrole@example.com",
            role=User.ROLE_STUDENT,
        )
        target.set_password("password123")
        db.session.add(target)
        db.session.commit()
        target_id = target.id

    response = client.put(
        f"/admin/users/{target_id}/role",
        json={"role": "superadmin"},
    )
    assert response.status_code in (400, 403)


# ---------------------------------------------------- admin.py: привязка студента


def test_admin_can_link_student_to_user(app):
    """Админ привязывает запись Student к User с ролью student."""
    client, _ = _make_admin(app)

    with app.app_context():
        from app.models.group import Group

        group = Group(group_name="LINK-1", year=2024)
        db.session.add(group)
        db.session.commit()

        student = Student(full_name="Linked Student", group_id=group.id)
        db.session.add(student)
        db.session.commit()
        student_id = student.id

        target = User(
            username="link_target",
            email="link_target@example.com",
            role=User.ROLE_STUDENT,
        )
        target.set_password("password123")
        db.session.add(target)
        db.session.commit()
        target_id = target.id

    response = client.put(
        f"/admin/users/{target_id}/student",
        json={"student_id": student_id},
    )
    assert response.status_code == 200

    with app.app_context():
        user = db.session.get(User, target_id)
        assert user.student_id == student_id


def test_admin_can_unlink_student_from_user(app):
    """Админ отвязывает студента от user."""
    client, _ = _make_admin(app)

    with app.app_context():
        from app.models.group import Group

        group = Group(group_name="LINK-2", year=2024)
        db.session.add(group)
        db.session.commit()

        student = Student(full_name="Unlink Student", group_id=group.id)
        db.session.add(student)
        db.session.commit()

        target = User(
            username="unlink_target",
            email="unlink_target@example.com",
            role=User.ROLE_STUDENT,
            student_id=student.id,
        )
        target.set_password("password123")
        db.session.add(target)
        db.session.commit()
        target_id = target.id

    response = client.put(
        f"/admin/users/{target_id}/student",
        json={"student_id": None},
    )
    assert response.status_code == 200

    with app.app_context():
        user = db.session.get(User, target_id)
        assert user.student_id is None