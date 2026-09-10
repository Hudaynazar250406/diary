from app.extensions import db

class Group(db.Model):
    __tablename__ = "groups"
    id = db.Column(db.Integer, primary_key=True)
    group_name = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    
    def to_dict(self):
        return {"id": self.id, "group_name": self.group_name, "year": self.year}