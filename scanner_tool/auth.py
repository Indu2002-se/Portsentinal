from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from supabase import create_client, Client
import os
from functools import wraps

auth = Blueprint('auth', __name__)

# Supabase setup
url: str = "https://rcaleqoorgrhnjknlavj.supabase.co"
key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJjYWxlcW9vcmdyaG5qa25sYXZqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTAzNzQ0MDUsImV4cCI6MjA2NTk1MDQwNX0.ZVtoEMGEybG25wFJ0524x8q-Mhfi-aXXVyypQdk58QE"
supabase: Client = create_client(url, key)

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        privacy_agree = request.form.get('privacy_agree')

        if not all([username, email, password]):
            flash('All fields are required', 'error')
            return redirect(url_for('auth.signup'))
        
        if not privacy_agree:
            flash('You must agree to the Privacy Policy', 'error')
            return redirect(url_for('auth.signup'))

        try:
            # Check if username already exists in the old system for backward compatibility
            res = supabase.table('users').select("id").eq('username', username).execute()
            if res.data:
                flash('Username already exists', 'error')
                return redirect(url_for('auth.signup'))

            # Sign up the user with Supabase Auth
            auth_response = supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "username": username
                    },
                    "email_redirect_to": url_for('auth.login', _external=True)
                }
            })

            # The user is signed up but needs to confirm their email
            # Supabase sends the confirmation email automatically
            flash('Registration successful! Please check your email to confirm your account.', 'success')
            return redirect(url_for('auth.login'))

        except Exception as e:
            # Supabase client raises an error for existing email, so we can catch it
            flash(f'An error occurred: {e}', 'error')
            return redirect(url_for('auth.signup'))
            
    return render_template('auth/signup.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Please fill in all fields', 'error')
            return redirect(url_for('auth.login'))
            
        try:
            data = supabase.auth.sign_in_with_password({"email": email, "password": password})
            session['user_id'] = data.user.id
            session['username'] = data.user.user_metadata.get('username', 'N/A')
            flash('Welcome back!', 'success')
            return redirect(url_for('dashboard'))
        
        except Exception as e:
            flash('Invalid email or password, or email not confirmed.', 'error')
            return redirect(url_for('auth.login'))
            
    return render_template('auth/login.html')

@auth.route('/privacy-policy')
def privacy_policy():
    return render_template('auth/privacy_policy.html')
    
@auth.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('index')) 