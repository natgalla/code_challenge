from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required

from app.extensions import db
from app.models import User, Manufacturer, Starship

bp = Blueprint('routes', __name__)


@bp.route('/')
def index():
    return render_template('index.html')


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if db.session.execute(db.select(User).filter_by(username=username)).scalar_one_or_none():
            flash('Username already exists')
            return redirect(url_for('routes.register'))

        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash('Registration successful')
        return redirect(url_for('routes.login'))

    return render_template('register.html')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = db.session.execute(db.select(User).filter_by(username=username)).scalar_one_or_none()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('routes.dashboard'))

        flash('Invalid username or password')

    return render_template('login.html')


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('routes.index'))


@bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    selected_manufacturer = 'all'

    if request.method == 'POST':
        selected_manufacturer = request.form['manufacturer']

    # return all starships or filter by manufacturer if provided
    if selected_manufacturer == 'all':
        starships = db.session.execute(db.select(Starship).order_by(Starship.name)).scalars().all()
    else:
        manufacturer = db.session.execute(
            db.select(Manufacturer).filter_by(name=selected_manufacturer)
        ).scalar_one_or_none()
        starships = manufacturer.starships if manufacturer else []

    manufacturers = db.session.execute(db.select(Manufacturer).order_by(Manufacturer.name)).scalars().all()
    return render_template('dashboard.html', manufacturers=manufacturers, starships=starships, selected_manufacturer=selected_manufacturer)
