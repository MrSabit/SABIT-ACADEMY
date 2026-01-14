from flask import render_template, redirect, url_for, flash, request, current_app
from urllib.parse import urlparse
from flask_login import login_user, logout_user, current_user
from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm, ChangeProfilePicForm
from app.models import User
import os
from werkzeug.utils import secure_filename

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('student.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('student.dashboard')
        return redirect(next_page)
    return render_template('auth/login.html', title='Sign In', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('student.dashboard'))
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            user = User(username=form.username.data, email=form.email.data, role=form.role.data.lower())
            user.set_password(form.password.data)
            if form.profile_pic.data:
                file = form.profile_pic.data
                filename = secure_filename(file.filename)
                upload_folder = current_app.config['UPLOAD_FOLDER']
                os.makedirs(upload_folder, exist_ok=True)
                file_path = os.path.join(upload_folder, filename)
                try:
                    file.save(file_path)
                    user.profile_pic = filename
                    flash('Profile picture uploaded successfully!')
                except Exception as e:
                    flash(f'Error uploading profile picture: {str(e)}')
            db.session.add(user)
            db.session.commit()
            flash('Congratulations, you are now a registered user!')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            if 'UNIQUE constraint failed: user.email' in str(e):
                flash('Email address is already registered. Please use a different email.')
            elif 'UNIQUE constraint failed: user.username' in str(e):
                flash('Username is already taken. Please choose a different username.')
            else:
                flash(f'An error occurred during registration: {str(e)}')
    return render_template('auth/register.html', title='Register', form=form)

@bp.route('/change_profile_pic', methods=['GET', 'POST'])
def change_profile_pic():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    form = ChangeProfilePicForm()
    if form.validate_on_submit():
        if form.profile_pic.data:
            file = form.profile_pic.data
            filename = secure_filename(file.filename)
            upload_folder = current_app.config['UPLOAD_FOLDER']
            os.makedirs(upload_folder, exist_ok=True)
            file_path = os.path.join(upload_folder, filename)
            try:
                file.save(file_path)
                current_user.profile_pic = filename
                db.session.commit()
                flash('Profile picture updated successfully!')
                return redirect(url_for('student.dashboard'))
            except Exception as e:
                flash(f'Error uploading profile picture: {str(e)}')
        else:
            flash('No file selected.')
    return render_template('auth/change_profile_pic.html', title='Change Profile Picture', form=form)