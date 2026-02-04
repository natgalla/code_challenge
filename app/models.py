from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db


starship_manufacturers = db.Table(
    'starship_manufacturers',
    db.Column('starship_id', db.Integer, db.ForeignKey('starship.id'), primary_key=True),
    db.Column('manufacturer_id', db.Integer, db.ForeignKey('manufacturer.id'), primary_key=True)
)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Manufacturer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), unique=True, nullable=False)
    starships = db.relationship('Starship', secondary=starship_manufacturers, back_populates='manufacturers')


class Starship(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(256), nullable=False)
    model = db.Column(db.String(256))
    cost_in_credits = db.Column(db.String(50))
    length = db.Column(db.String(50))
    max_atmosphering_speed = db.Column(db.String(50))
    crew = db.Column(db.String(50))
    passengers = db.Column(db.String(50))
    cargo_capacity = db.Column(db.String(50))
    consumables = db.Column(db.String(100))
    hyperdrive_rating = db.Column(db.String(20))
    mglt = db.Column(db.String(20))
    starship_class = db.Column(db.String(256))
    url = db.Column(db.String(256))
    manufacturers = db.relationship('Manufacturer', secondary=starship_manufacturers, back_populates='starships')
