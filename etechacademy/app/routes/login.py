from flask import Blueprint, render_template, url_for, request, redirect
import uuid, logging
from datetime import datetime, timedelta, timezone

from app.database import get_db_connection

login_bp = Blueprint("login", __name__)

@login_bp.route('/login', methods=['GET', 'POST'])
@login_bp.route('/login.html', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            username = request.form['username']
            password = request.form['password']

            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                f"""
                SELECT user_id, role FROM users WHERE username = '{username}' AND password = '{password}'
                """
            )
            user_info = cur.fetchone()

            if user_info is None:
                logging.info('Incorrect username or password')
                return render_template('login.html', error= "Incorrect username or password")

            user_id, role = user_info
            session_id = uuid.uuid4().hex
            expiration_time = datetime.now(timezone.utc) + timedelta(hours=6)
            
            cur.execute(
                f"""
                INSERT INTO sessions (session_id, user_id, expiration) VALUES ('{session_id}', '{user_id}', '{expiration_time}');
                """
            )
            conn.commit()
            cur.close()

            if user_info[1] == 'admin':
                response = redirect(url_for('admin.admin_dashboard'))
            else:
                response = redirect(url_for('profile.profile'))
            response.set_cookie("session_id", session_id, expires=expiration_time)
            return response
            
        except Exception as e:
            logging.error(f"An error occured: {e}")
            return render_template('login.html', error="An error occured during login.")
       
    return render_template('login.html')
