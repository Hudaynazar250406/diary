from app.extensions import db


class Discipline(db.Model):
    __tablename__ = "disciplines"

    id = db.Column(db.Integer, primary_key=True)
    discipline_name = db.Column(
        db.String(150),
        nullable=False,
        unique=True,
    )

    grades = db.relationship("Grade", back_populates="discipline")
    study_plans = db.relationship("StudyPlan", back_populates="discipline")
    schedules = db.relationship("Schedule", back_populates="discipline")

    def to_dict(self):
        return {
            "id": self.id,
            "discipline_name": self.discipline_name,
        }
