from app.extensions import db
from app.models.student import Student
from app.models.group import Group


class StudentService:

    @staticmethod
    def create(data):
        full_name = data.get("full_name")
        group_id = data.get("group_id")
        email = data.get("email")

        if not full_name:
            return None, "full_name is required"
        if not group_id:
            return None, "group_id is required"

        group = Group.query.get(group_id)
        if group is None:
            return None, f"Group with id {group_id} does not exist"

        student = Student(full_name=full_name, group_id=group_id, email=email)
        db.session.add(student)
        db.session.commit()

        return student, None

    @staticmethod
    def list_all(group_id=None):
        query = Student.query
        if group_id is not None:
            query = query.filter_by(group_id=group_id)
        return query.all()

    @staticmethod
    def get_by_id(student_id):
        return Student.query.get(student_id)

    @staticmethod
    def update(student_id, data):
        student = Student.query.get(student_id)
        if student is None:
            return None, "Student not found"

        full_name = data.get("full_name")
        group_id = data.get("group_id")
        email = data.get("email")

        if full_name is not None:
            if not full_name:
                return None, "full_name cannot be empty"
            student.full_name = full_name

        if group_id is not None:
            group = Group.query.get(group_id)
            if group is None:
                return None, f"Group with id {group_id} does not exist"
            student.group_id = group_id

        if email is not None:
            student.email = email

        db.session.commit()
        return student, None

    @staticmethod
    def delete(student_id):
        student = Student.query.get(student_id)
        if student is None:
            return False, "Student not found"

        db.session.delete(student)
        db.session.commit()
        return True, None
