import datetime

from app.extensions import db


class Grade(db.Model):
    __tablename__ = "grades"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    discipline_id = db.Column(db.Integer, db.ForeignKey("disciplines.id"), nullable=False)
    grade = db.Column(db.Integer, nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.date.today)

    __table_args__ = (
        db.CheckConstraint("grade >= 1 AND grade <= 5", name="check_grade_range"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "discipline_id": self.discipline_id,
            "grade": self.grade,
            "date": self.date.isoformat(),
        }