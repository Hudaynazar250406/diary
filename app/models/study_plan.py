from app.extensions import db


class StudyPlan(db.Model):
    __tablename__ = "study_plans"

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
    semester = db.Column(db.Integer, nullable=False)

    group = db.relationship("Group", back_populates="study_plans")
    discipline = db.relationship("Discipline", back_populates="study_plans")

    __table_args__ = (
        db.UniqueConstraint(
            "group_id",
            "discipline_id",
            "semester",
            name="uq_study_plan_group_discipline_semester",
        ),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "group_id": self.group_id,
            "discipline_id": self.discipline_id,
            "semester": self.semester,
        }
