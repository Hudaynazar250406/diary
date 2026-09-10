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
