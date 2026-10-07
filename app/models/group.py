from app.extensions import db


class Group(db.Model):
    __tablename__ = "groups"

    id = db.Column(db.Integer, primary_key=True)
    group_name = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)

    students = db.relationship("Student", back_populates="group")
    study_plans = db.relationship("StudyPlan", back_populates="group")
    schedules = db.relationship("Schedule", back_populates="group")

    __table_args__ = (
        db.UniqueConstraint("group_name", "year", name="uq_group_name_year"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "group_name": self.group_name,
            "year": self.year,
        }
