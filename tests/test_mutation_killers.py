"""Тесты для убийства выживших мутаций.

Каждый тест точечно закрывает то, что показал pytest-gremlins
в отчёте: границы валидации, методы модели User, семестры.
"""
from app.models.user import User


# ---------------------------------------------------------------- User methods

def test_user_has_role_returns_true_for_matching_role(app):
    """User.has_role возвращает True для совпадающей роли."""
    with app.app_context():
        user = User(role=User.ROLE_TEACHER)
        assert user.has_role(User.ROLE_TEACHER) is True
        assert user.has_role(User.ROLE_STUDENT, User.ROLE_TEACHER) is True


def test_user_has_role_returns_false_for_other_role(app):
    """User.has_role возвращает False для чужой роли."""
    with app.app_context():
        user = User(role=User.ROLE_STUDENT)
        assert user.has_role(User.ROLE_ADMIN) is False
        assert user.has_role(User.ROLE_TEACHER) is False


def test_user_check_password_positive(app):
    """check_password возвращает True для правильного пароля."""
    with app.app_context():
        user = User(role=User.ROLE_STUDENT)
        user.set_password("correct_password_123")
        assert user.check_password("correct_password_123") is True


def test_user_check_password_negative(app):
    """check_password возвращает False для неправильного пароля."""
    with app.app_context():
        user = User(role=User.ROLE_STUDENT)
        user.set_password("correct_password_123")
        assert user.check_password("wrong_password") is False
        assert user.check_password("") is False


def test_user_set_password_hashes(app):
    """set_password не сохраняет пароль в открытом виде."""
    with app.app_context():
        user = User(role=User.ROLE_STUDENT)
        user.set_password("secret12345")
        assert user.password_hash != "secret12345"
        assert user.password_hash is not None
        assert len(user.password_hash) > 20


# ---------------------------------------------------------------- Registration boundaries

def test_register_username_too_short(anonymous_client, app):
    """username длиной 2 символа отклоняется (граница < 3)."""
    response = anonymous_client.post(
        "/register",
        data={
            "username": "ab",
            "email": "ab@example.com",
            "password": "password123",
            "password_confirm": "password123",
        },
    )
    assert response.status_code == 200
    with app.app_context():
        assert User.query.filter_by(username="ab").count() == 0


def test_register_username_exactly_3_accepted(anonymous_client, app):
    """username ровно из 3 символов принимается."""
    response = anonymous_client.post(
        "/register",
        data={
            "username": "abc",
            "email": "abc@example.com",
            "password": "password123",
            "password_confirm": "password123",
        },
    )
    assert response.status_code == 302
    with app.app_context():
        assert User.query.filter_by(username="abc").count() == 1


def test_register_username_too_long(anonymous_client, app):
    """username длиной 51 символ отклоняется (> 50)."""
    response = anonymous_client.post(
        "/register",
        data={
            "username": "a" * 51,
            "email": "long@example.com",
            "password": "password123",
            "password_confirm": "password123",
        },
    )
    assert response.status_code == 200
    with app.app_context():
        assert User.query.filter_by(username="a" * 51).count() == 0


def test_register_username_exactly_50_accepted(anonymous_client, app):
    """username ровно из 50 символов принимается."""
    username = "b" * 50
    response = anonymous_client.post(
        "/register",
        data={
            "username": username,
            "email": "b50@example.com",
            "password": "password123",
            "password_confirm": "password123",
        },
    )
    assert response.status_code == 302


def test_register_password_too_short(anonymous_client, app):
    """пароль из 7 символов отклоняется (< 8)."""
    response = anonymous_client.post(
        "/register",
        data={
            "username": "shortpw",
            "email": "shortpw@example.com",
            "password": "1234567",
            "password_confirm": "1234567",
        },
    )
    assert response.status_code == 200
    with app.app_context():
        assert User.query.filter_by(username="shortpw").count() == 0


def test_register_password_exactly_8_accepted(anonymous_client, app):
    """пароль ровно из 8 символов принимается."""
    response = anonymous_client.post(
        "/register",
        data={
            "username": "exact8",
            "email": "exact8@example.com",
            "password": "12345678",
            "password_confirm": "12345678",
        },
    )
    assert response.status_code == 302
    with app.app_context():
        assert User.query.filter_by(username="exact8").count() == 1


def test_register_email_too_long(anonymous_client, app):
    """email длиной > 120 символов отклоняется."""
    long_email = "a" * 120 + "@example.com"
    response = anonymous_client.post(
        "/register",
        data={
            "username": "longmail",
            "email": long_email,
            "password": "password123",
            "password_confirm": "password123",
        },
    )
    assert response.status_code == 200


def test_register_email_without_at(anonymous_client, app):
    """email без @ отклоняется."""
    response = anonymous_client.post(
        "/register",
        data={
            "username": "noat",
            "email": "noat.example.com",
            "password": "password123",
            "password_confirm": "password123",
        },
    )
    assert response.status_code == 200
    with app.app_context():
        assert User.query.filter_by(username="noat").count() == 0


def test_register_password_mismatch(anonymous_client, app):
    """пароль и подтверждение должны совпадать."""
    response = anonymous_client.post(
        "/register",
        data={
            "username": "mismatch",
            "email": "mismatch@example.com",
            "password": "password123",
            "password_confirm": "different456",
        },
    )
    assert response.status_code == 200
    with app.app_context():
        assert User.query.filter_by(username="mismatch").count() == 0


# ---------------------------------------------------------------- Study plan semester

def test_create_study_plan_semester_zero_rejected(client, app):
    """семестр 0 отклоняется (< 1)."""
    from app.models.discipline import Discipline
    from app.models.group import Group

    with app.app_context():
        group = Group(group_name="TZ-1", year=2024)
        disc = Discipline(discipline_name="Для semester zero")
        db_session = __import__("app.extensions", fromlist=["db"]).db.session
        db_session.add_all([group, disc])
        db_session.commit()
        group_id, disc_id = group.id, disc.id

    response = client.post(
        "/study_plans",
        json={"group_id": group_id, "discipline_id": disc_id, "semester": 0},
    )
    assert response.status_code == 400


def test_create_study_plan_semester_one_accepted(client, app):
    """семестр 1 принимается."""
    from app.models.discipline import Discipline
    from app.models.group import Group

    with app.app_context():
        group = Group(group_name="TZ-2", year=2024)
        disc = Discipline(discipline_name="Для semester one")
        db_session = __import__("app.extensions", fromlist=["db"]).db.session
        db_session.add_all([group, disc])
        db_session.commit()
        group_id, disc_id = group.id, disc.id

    response = client.post(
        "/study_plans",
        json={"group_id": group_id, "discipline_id": disc_id, "semester": 1},
    )
    assert response.status_code == 201


# ---------------------------------------------------------------- Grades boundaries

def test_create_grade_zero_rejected(client, app):
    """оценка 0 отклоняется (value < 1)."""
    from app.models.discipline import Discipline
    from app.models.group import Group
    from app.models.student import Student
    from app.models.study_plan import StudyPlan

    with app.app_context():
        group = Group(group_name="G0", year=2024)
        disc = Discipline(discipline_name="Disc grade zero")
        db_session = __import__("app.extensions", fromlist=["db"]).db.session
        db_session.add_all([group, disc])
        db_session.commit()
        student = Student(full_name="Zero Grade", group_id=group.id)
        db_session.add(student)
        db_session.commit()
        db_session.add(
            StudyPlan(group_id=group.id, discipline_id=disc.id, semester=1)
        )
        db_session.commit()
        sid, did = student.id, disc.id

    response = client.post(
        "/grades",
        json={"student_id": sid, "discipline_id": did, "grade": 0},
    )
    assert response.status_code == 400


def test_create_grade_six_rejected(client, app):
    """оценка 6 отклоняется (value > 5)."""
    from app.models.discipline import Discipline
    from app.models.group import Group
    from app.models.student import Student
    from app.models.study_plan import StudyPlan

    with app.app_context():
        group = Group(group_name="G6", year=2024)
        disc = Discipline(discipline_name="Disc grade six")
        db_session = __import__("app.extensions", fromlist=["db"]).db.session
        db_session.add_all([group, disc])
        db_session.commit()
        student = Student(full_name="Six Grade", group_id=group.id)
        db_session.add(student)
        db_session.commit()
        db_session.add(
            StudyPlan(group_id=group.id, discipline_id=disc.id, semester=1)
        )
        db_session.commit()
        sid, did = student.id, disc.id

    response = client.post(
        "/grades",
        json={"student_id": sid, "discipline_id": did, "grade": 6},
    )
    assert response.status_code == 400


# ---------------------------------------------------------------- Schedule boundaries

def test_create_schedule_weekday_zero_rejected(client, app):
    """weekday 0 отклоняется (< 1)."""
    from app.models.discipline import Discipline
    from app.models.group import Group
    from app.models.study_plan import StudyPlan

    with app.app_context():
        group = Group(group_name="SW0", year=2024)
        disc = Discipline(discipline_name="Sch weekday zero")
        db_session = __import__("app.extensions", fromlist=["db"]).db.session
        db_session.add_all([group, disc])
        db_session.commit()
        db_session.add(
            StudyPlan(group_id=group.id, discipline_id=disc.id, semester=1)
        )
        db_session.commit()
        gid, did = group.id, disc.id

    response = client.post(
        "/schedules",
        json={
            "group_id": gid,
            "discipline_id": did,
            "weekday": 0,
            "start_time": "10:00",
            "end_time": "11:30",
        },
    )
    assert response.status_code == 400


def test_create_schedule_weekday_eight_rejected(client, app):
    """weekday 8 отклоняется (> 7)."""
    from app.models.discipline import Discipline
    from app.models.group import Group
    from app.models.study_plan import StudyPlan

    with app.app_context():
        group = Group(group_name="SW8", year=2024)
        disc = Discipline(discipline_name="Sch weekday eight")
        db_session = __import__("app.extensions", fromlist=["db"]).db.session
        db_session.add_all([group, disc])
        db_session.commit()
        db_session.add(
            StudyPlan(group_id=group.id, discipline_id=disc.id, semester=1)
        )
        db_session.commit()
        gid, did = group.id, disc.id

    response = client.post(
        "/schedules",
        json={
            "group_id": gid,
            "discipline_id": did,
            "weekday": 8,
            "start_time": "10:00",
            "end_time": "11:30",
        },
    )
    assert response.status_code == 400


def test_create_schedule_end_equal_start_rejected(client, app):
    """конец равен началу — недопустимо (end <= start)."""
    from app.models.discipline import Discipline
    from app.models.group import Group
    from app.models.study_plan import StudyPlan

    with app.app_context():
        group = Group(group_name="SEQ", year=2024)
        disc = Discipline(discipline_name="Sch equal time")
        db_session = __import__("app.extensions", fromlist=["db"]).db.session
        db_session.add_all([group, disc])
        db_session.commit()
        db_session.add(
            StudyPlan(group_id=group.id, discipline_id=disc.id, semester=1)
        )
        db_session.commit()
        gid, did = group.id, disc.id

    response = client.post(
        "/schedules",
        json={
            "group_id": gid,
            "discipline_id": did,
            "weekday": 1,
            "start_time": "10:00",
            "end_time": "10:00",
        },
    )
    assert response.status_code == 400