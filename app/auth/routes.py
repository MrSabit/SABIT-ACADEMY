from flask import render_template, redirect, url_for, flash, request, current_app
from urllib.parse import urlparse
from flask_login import login_user, logout_user, current_user
from app import db, mail
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm, ChangeProfilePicForm, EditProfileForm, ForgotPasswordForm, ResetPasswordForm
from app.models import User
import os
from werkzeug.utils import secure_filename
from flask_mail import Message

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('student.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
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
                # Truncate filename if too long (keep extension)
                if len(filename) > 200:
                    name, ext = os.path.splitext(filename)
                    filename = name[:200-len(ext)] + ext
                upload_folder = current_app.config['UPLOAD_FOLDER']
                os.makedirs(upload_folder, exist_ok=True)
                file_path = os.path.join(upload_folder, filename)
                try:
                    file.save(file_path)
                    user.profile_pic = filename
                    flash('Profile picture uploaded successfully!', 'success')
                except Exception as e:
                    flash(f'Error uploading profile picture: {str(e)}', 'warning')
            db.session.add(user)
            db.session.commit()
            flash('Congratulations, you are now a registered user!', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            if 'UNIQUE constraint failed: user.email' in str(e):
                flash('Email address is already registered. Please use a different email.', 'danger')
            elif 'UNIQUE constraint failed: user.username' in str(e):
                flash('Username is already taken. Please choose a different username.', 'danger')
            else:
                flash(f'An error occurred during registration: {str(e)}', 'danger')
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
            # Truncate filename if too long (keep extension)
            if len(filename) > 200:
                name, ext = os.path.splitext(filename)
                filename = name[:200-len(ext)] + ext
            upload_folder = current_app.config['UPLOAD_FOLDER']
            os.makedirs(upload_folder, exist_ok=True)
            file_path = os.path.join(upload_folder, filename)
            try:
                file.save(file_path)
                current_user.profile_pic = filename
                db.session.commit()
                flash('Profile picture updated successfully!', 'success')
                return redirect(url_for('student.dashboard'))
            except Exception as e:
                flash(f'Error uploading profile picture: {str(e)}', 'warning')
        else:
            flash('No file selected.', 'warning')
    return render_template('auth/change_profile_pic.html', title='Change Profile Picture', form=form)

@bp.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    form = EditProfileForm()
    if form.validate_on_submit():
        try:
            # Update username and email
            current_user.username = form.username.data
            current_user.email = form.email.data
            
            # Update password if provided
            if form.new_password.data:
                current_user.set_password(form.new_password.data)
            
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('student.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred while updating your profile: {str(e)}', 'danger')
    elif request.method == 'GET':
        # Pre-fill form with current user data
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('auth/edit_profile.html', title='Edit Profile', form=form)

def send_password_reset_email(user):
    token = user.generate_reset_token()
    reset_url = url_for('auth.reset_password', token=token, _external=True)
    
    # Show reset link in console only in development mode
    if current_app.config.get('MAIL_SUPPRESS_SEND'):
        print(f"\n{'='*60}")
        print(f"PASSWORD RESET LINK FOR {user.email}:")
        print(f"{reset_url}")
        print(f"{'='*60}\n")
    
    msg = Message('Password Reset Request',
                  sender=current_app.config['MAIL_DEFAULT_SENDER'],
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{reset_url}

If you did not make this request, simply ignore this email and no changes will be made.
'''
    
    try:
        mail.send(msg)
        current_app.logger.info(f"Password reset email sent to {user.email}")
    except Exception as e:
        # If email fails, log the reset URL for development
        current_app.logger.info(f"Password reset link for {user.email}: {reset_url}")
        current_app.logger.warning(f"Email sending failed: {str(e)}")
        # For development, we can still proceed
        pass

@bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('student.dashboard'))
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
            # Check if email is configured
            if current_app.config.get('MAIL_SUPPRESS_SEND'):
                flash('Email is not configured. Check the console for the reset link.', 'info')
            else:
                flash('Check your email for instructions to reset your password.', 'info')
        else:
            # Don't reveal if email exists or not for security
            flash('If an account with that email exists, a reset link has been sent.', 'info')
        return redirect(url_for('auth.login'))
    return render_template('auth/forgot_password.html', title='Forgot Password', form=form)

@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('student.dashboard'))
    user = User.query.filter_by(reset_token=token).first()
    if not user or not user.verify_reset_token(token):
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('auth.forgot_password'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        user.clear_reset_token()
        flash('Your password has been reset.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', title='Reset Password', form=form)