# import datetime

from app.extensions import db


class Schedule(db.Model):
    __tablename__ = "schedules"

    id = db.Column(db.Integer, primary_key=True)

    group_id = db.Column(
        db.Integer,
        db.ForeignKey("groups.id"),
        nullable=False,
    )

    discipline_id = db.Column(
        db.Integer,
        db.ForeignKey("disciplines.id"),
        nullable=False,
    )

    weekday = db.Column(
        db.Integer,
        nullable=False,
    )

    start_time = db.Column(
        db.Time,
        nullable=False,
    )

    end_time = db.Column(
        db.Time,
        nullable=False,
    )

    room = db.Column(
        db.String(50),
        nullable=True,
    )

    discipline = db.relationship("Discipline")
    group = db.relationship("Group")

    __table_args__ = (
        db.CheckConstraint(
            "weekday >= 1 AND weekday <= 7",
            name="check_schedule_weekday",
        ),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "group_id": self.group_id,
            "discipline_id": self.discipline_id,
            "weekday": self.weekday,
            "start_time": self.start_time.strftime("%H:%M"),
            "end_time": self.end_time.strftime("%H:%M"),
            "room": self.room,
        }