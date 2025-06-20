from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from supabase import create_client, Client
import os
from functools import wraps
import re

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
        
        if not username or not email or not password:
            flash('All fields are required', 'error')
            return redirect(url_for('auth.signup'))
            
        try:
            # Check if username already exists
            res = supabase.table('users').select("id").eq('username', username).execute()
            if res.data:
                flash('Username already exists', 'error')
                return redirect(url_for('auth.signup'))

            # Check if email already exists
            res = supabase.table('users').select("id").eq('email', email).execute()
            if res.data:
                flash('Email already exists', 'error')
                return redirect(url_for('auth.signup'))

            hashed_password = generate_password_hash(password)
            
            user = supabase.table('users').insert({
                "username": username,
                "email": email,
                "password": hashed_password
            }).execute()

            if user.data:
                flash('Registration successful! Please log in.', 'success')
                return redirect(url_for('auth.login'))
            else:
                flash('An error occurred during registration. Please try again.', 'error')
                return redirect(url_for('auth.signup'))

        except Exception as e:
            flash(f'An error occurred during registration: {e}', 'error')
            return redirect(url_for('auth.signup'))
            
    return render_template('auth/signup.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Please fill in all fields', 'error')
            return redirect(url_for('auth.login'))
            
        try:
            res = supabase.table('users').select("*").eq('username', username).execute()
            if res.data:
                user = res.data[0]
                if check_password_hash(user['password'], password):
                    session['user_id'] = user['id']
                    session['username'] = user['username']
                    flash('Welcome back!', 'success')
                    return redirect(url_for('dashboard'))
                    
            flash('Invalid username or password', 'error')
            
        except Exception as e:
            flash(f'An error occurred during login: {e}', 'error')
            
    return render_template('auth/login.html')

@auth.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('index')) 