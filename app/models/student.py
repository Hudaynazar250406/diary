from app.extensions import db

class Student(db.Model):
    __tablename__ = "students"
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    group_id = db.Column(db.Integer, db.ForeignKey("groups.id"), nullable=False)

    def to_dict(self):
        return {"id": self.id, "full_name": self.full_name, "group_id": self.group_id}