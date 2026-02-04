import json
import requests

from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

SWAPI_BASE_URL = "https://www.swapi.tech/api/"

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


starship_manufacturers = db.Table(
    'starship_manufacturers',
    db.Column('starship_id', db.Integer, db.ForeignKey('starship.id'), primary_key=True),
    db.Column('manufacturer_id', db.Integer, db.ForeignKey('manufacturer.id'), primary_key=True)
)


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


def fetch_starship_data():
    """Fetch all starships and manufacturers from SWAPI and store in DB."""
    endpoint = SWAPI_BASE_URL + 'starships?expanded=true'

    try:
        while endpoint:
            r = requests.get(endpoint)
            if r.status_code == 200:
                r_json = r.json()
                for record in r_json.get('results', []):
                    props = record.get('properties', {})
                    uid = record.get('uid')

                    if Starship.query.filter_by(uid=uid).first():
                        continue

                    starship = Starship(
                        uid=uid,
                        name=props.get('name'),
                        model=props.get('model'),
                        cost_in_credits=props.get('cost_in_credits'),
                        length=props.get('length'),
                        max_atmosphering_speed=props.get('max_atmosphering_speed'),
                        crew=props.get('crew'),
                        passengers=props.get('passengers'),
                        cargo_capacity=props.get('cargo_capacity'),
                        consumables=props.get('consumables'),
                        hyperdrive_rating=props.get('hyperdrive_rating'),
                        mglt=props.get('MGLT'),
                        starship_class=props.get('starship_class'),
                        url=props.get('url')
                    )

                    manufacturer_str = props.get('manufacturer', '')
                    for name in [m.strip() for m in manufacturer_str.split(',')]:
                        if name:
                            manufacturer = Manufacturer.query.filter_by(name=name).first()
                            if not manufacturer:
                                manufacturer = Manufacturer(name=name)
                                db.session.add(manufacturer)
                            starship.manufacturers.append(manufacturer)

                    db.session.add(starship)
                endpoint = r_json.get('next')
            else:
                break
        db.session.commit()
        print(f'Loaded {Starship.query.count()} starships and {Manufacturer.query.count()} manufacturers into DB')
    except Exception as e:
        print(f'An API error occurred: {e}')


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))

        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash('Registration successful')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))

        flash('Invalid username or password')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if request.method == 'POST':
        manufacturer = request.form['manufacturer']
        print(manufacturer)
    manufacturers = Manufacturer.query.order_by(Manufacturer.name).all()
    return render_template('dashboard.html', manufacturers=manufacturers)


with app.app_context():
    db.create_all()
    if Starship.query.count() == 0:
        print('No starships in DB, fetching from SWAPI...')
        fetch_starship_data()


if __name__ == '__main__':
    app.run(debug=True)
