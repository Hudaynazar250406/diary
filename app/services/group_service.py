from app.extensions import db
from app.models.group import Group


class GroupService:

    @staticmethod
    def create(data):
        group_name = data.get("group_name")
        year = data.get("year")

        if not group_name:
            return None, "group_name is required"
        if not year:
            return None, "year is required"

        group = Group(group_name=group_name, year=year)
        db.session.add(group)
        db.session.commit()

        return group, None

    @staticmethod
    def list_all():
        return Group.query.all()

    @staticmethod
    def get_by_id(group_id):
        return Group.query.get(group_id)

    @staticmethod
    def update(group_id, data):
        group = Group.query.get(group_id)
        if group is None:
            return None, "Group not found"

        group_name = data.get("group_name")
        year = data.get("year")

        if group_name is not None:
            if not group_name:
                return None, "group_name cannot be empty"
            group.group_name = group_name

        if year is not None:
            if not year:
                return None, "year cannot be empty"
            group.year = year

        db.session.commit()
        return group, None

    @staticmethod
    def delete(group_id):
        group = Group.query.get(group_id)
        if group is None:
            return False, "Group not found"

        if group.students:
            return False, "Cannot delete group with existing students"

        db.session.delete(group)
        db.session.commit()
        return True, None
