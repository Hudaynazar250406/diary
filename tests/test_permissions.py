from app.models.user import User


def test_anonymous_user_redirected_from_protected_api(
    anonymous_client,
):
    response = anonymous_client.get("/groups")

    assert response.status_code == 302
    assert response.headers["Location"].endswith(
        "/login",
    )


def test_student_cannot_read_groups(
    student_client,
):
    response = student_client.get("/groups")

    assert response.status_code == 403


def test_student_cannot_read_all_grades(
    student_client,
):
    response = student_client.get("/grades")

    assert response.status_code == 403


def test_teacher_can_read_groups(
    teacher_client,
):
    response = teacher_client.get("/groups")

    assert response.status_code == 200


def test_teacher_cannot_create_group(
    teacher_client,
):
    response = teacher_client.post(
        "/groups",
        json={
            "group_name": "241-352",
            "year": 2026,
        },
    )

    assert response.status_code == 403


def test_teacher_cannot_create_student(
    teacher_client,
):
    response = teacher_client.post(
        "/students",
        json={
            "full_name": "Тестовый студент",
            "group_id": 1,
        },
    )

    assert response.status_code == 403


def test_teacher_cannot_access_admin_panel(
    teacher_client,
):
    response = teacher_client.get(
        "/admin/users",
    )

    assert response.status_code == 403


def test_student_cannot_access_admin_panel(
    student_client,
):
    response = student_client.get(
        "/admin/users",
    )

    assert response.status_code == 403


def test_admin_can_access_admin_panel(
    client,
):
    response = client.get(
        "/admin/users",
    )

    assert response.status_code == 200


def test_user_has_role(app):
    with app.app_context():
        user = User(
            username="role_test",
            email="role_test@example.com",
            role=User.ROLE_TEACHER,
        )

        assert user.has_role(
            User.ROLE_TEACHER,
        ) is True

        assert user.has_role(
            User.ROLE_ADMIN,
        ) is False