import pytest

from app.extensions import db
from app.models.discipline import Discipline
from app.models.group import Group
from app.models.study_plan import StudyPlan


@pytest.fixture
def schedule_seed(app):
    with app.app_context():
        group = Group(
            group_name="241-352",
            year=2026,
        )

        discipline = Discipline(
            discipline_name="DevOps",
        )

        outside_discipline = Discipline(
            discipline_name="Криптография",
        )

        db.session.add_all(
            [
                group,
                discipline,
                outside_discipline,
            ]
        )

        db.session.flush()

        plan = StudyPlan(
            group_id=group.id,
            discipline_id=discipline.id,
            semester=1,
        )

        db.session.add(plan)
        db.session.commit()

        return {
            "group_id": group.id,
            "discipline_id": discipline.id,
            "outside_discipline_id": outside_discipline.id,
        }


def schedule_payload(seed):
    return {
        "group_id": seed["group_id"],
        "discipline_id": seed["discipline_id"],
        "weekday": 1,
        "start_time": "09:00",
        "end_time": "10:30",
        "room": "401",
    }


def test_teacher_can_create_schedule(
    teacher_client,
    schedule_seed,
):
    response = teacher_client.post(
        "/schedules",
        json=schedule_payload(schedule_seed),
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["weekday"] == 1
    assert data["start_time"] == "09:00"
    assert data["end_time"] == "10:30"
    assert data["room"] == "401"


def test_admin_can_create_schedule(
    client,
    schedule_seed,
):
    response = client.post(
        "/schedules",
        json=schedule_payload(schedule_seed),
    )

    assert response.status_code == 201


def test_student_cannot_create_schedule(
    student_client,
    schedule_seed,
):
    response = student_client.post(
        "/schedules",
        json=schedule_payload(schedule_seed),
    )

    assert response.status_code == 403


def test_schedule_requires_fields(
    teacher_client,
):
    response = teacher_client.post(
        "/schedules",
        json={},
    )

    assert response.status_code == 400


def test_schedule_rejects_nonexistent_group(
    teacher_client,
    schedule_seed,
):
    payload = schedule_payload(
        schedule_seed,
    )

    payload["group_id"] = 99999

    response = teacher_client.post(
        "/schedules",
        json=payload,
    )

    assert response.status_code == 400


def test_schedule_rejects_nonexistent_discipline(
    teacher_client,
    schedule_seed,
):
    payload = schedule_payload(
        schedule_seed,
    )

    payload["discipline_id"] = 99999

    response = teacher_client.post(
        "/schedules",
        json=payload,
    )

    assert response.status_code == 400


def test_schedule_requires_discipline_in_study_plan(
    teacher_client,
    schedule_seed,
):
    payload = schedule_payload(
        schedule_seed,
    )

    payload["discipline_id"] = (
        schedule_seed["outside_discipline_id"]
    )

    response = teacher_client.post(
        "/schedules",
        json=payload,
    )

    assert response.status_code == 400


@pytest.mark.parametrize(
    "weekday",
    [0, 8],
)
def test_schedule_rejects_invalid_weekday(
    teacher_client,
    schedule_seed,
    weekday,
):
    payload = schedule_payload(
        schedule_seed,
    )

    payload["weekday"] = weekday

    response = teacher_client.post(
        "/schedules",
        json=payload,
    )

    assert response.status_code == 400


def test_schedule_rejects_invalid_time(
    teacher_client,
    schedule_seed,
):
    payload = schedule_payload(
        schedule_seed,
    )

    payload["start_time"] = "invalid"

    response = teacher_client.post(
        "/schedules",
        json=payload,
    )

    assert response.status_code == 400


def test_schedule_rejects_end_before_start(
    teacher_client,
    schedule_seed,
):
    payload = schedule_payload(
        schedule_seed,
    )

    payload["start_time"] = "12:00"
    payload["end_time"] = "10:00"

    response = teacher_client.post(
        "/schedules",
        json=payload,
    )

    assert response.status_code == 400


def test_schedule_detects_conflict(
    teacher_client,
    schedule_seed,
):
    first = schedule_payload(
        schedule_seed,
    )

    response = teacher_client.post(
        "/schedules",
        json=first,
    )

    assert response.status_code == 201

    second = schedule_payload(
        schedule_seed,
    )

    second["start_time"] = "10:00"
    second["end_time"] = "11:00"

    response = teacher_client.post(
        "/schedules",
        json=second,
    )

    assert response.status_code == 400


def test_adjacent_schedule_is_allowed(
    teacher_client,
    schedule_seed,
):
    first = schedule_payload(
        schedule_seed,
    )

    teacher_client.post(
        "/schedules",
        json=first,
    )

    second = schedule_payload(
        schedule_seed,
    )

    second["start_time"] = "10:30"
    second["end_time"] = "12:00"

    response = teacher_client.post(
        "/schedules",
        json=second,
    )

    assert response.status_code == 201


def test_teacher_can_list_schedule(
    teacher_client,
    schedule_seed,
):
    teacher_client.post(
        "/schedules",
        json=schedule_payload(schedule_seed),
    )

    response = teacher_client.get(
        "/schedules",
    )

    assert response.status_code == 200
    assert len(response.get_json()) == 1


def test_teacher_can_update_schedule(
    teacher_client,
    schedule_seed,
):
    create_response = teacher_client.post(
        "/schedules",
        json=schedule_payload(schedule_seed),
    )

    schedule_id = create_response.get_json()["id"]

    payload = schedule_payload(
        schedule_seed,
    )

    payload["room"] = "402"

    response = teacher_client.put(
        f"/schedules/{schedule_id}",
        json=payload,
    )

    assert response.status_code == 200
    assert response.get_json()["room"] == "402"


def test_update_nonexistent_schedule(
    teacher_client,
    schedule_seed,
):
    response = teacher_client.put(
        "/schedules/99999",
        json=schedule_payload(schedule_seed),
    )

    assert response.status_code == 404


def test_teacher_can_delete_schedule(
    teacher_client,
    schedule_seed,
):
    create_response = teacher_client.post(
        "/schedules",
        json=schedule_payload(schedule_seed),
    )

    schedule_id = create_response.get_json()["id"]

    response = teacher_client.delete(
        f"/schedules/{schedule_id}",
    )

    assert response.status_code == 204

    response = teacher_client.get(
        "/schedules",
    )

    assert response.get_json() == []


def test_delete_nonexistent_schedule(
    teacher_client,
):
    response = teacher_client.delete(
        "/schedules/99999",
    )

    assert response.status_code == 404