from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user

from app import db
from models import User
from . import auth
from .forms import LoginForm, RegistrationForm


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('juegos'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            flash(f'Bienvenido, {user.username}', 'success')
            next_page = request.args.get('next')
            if next_page is None or not next_page.startswith('/') or next_page.startswith('//'):
                next_page = url_for('juegos')
            return redirect(next_page)
        flash('Usuario o contraseña incorrectos', 'danger')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Cerraste sesión', 'info')
    return redirect(url_for('auth.login'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Usuario registrado, ya puedes ingresar', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)
