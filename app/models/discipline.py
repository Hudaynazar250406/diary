from app.extensions import db

class Discipline(db.Model):
    __tablename__ = "disciplines"
    id = db.Column(db.Integer, primary_key=True)
    discipline_name = db.Column(db.String(150), nullable=False)

    def to_dict(self):
        return {"id": self.id, "discipline_name": self.discipline_name}