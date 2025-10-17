from flask import Blueprint, render_template, url_for, request, redirect
from app.database import get_db_connection
import logging

register_bp = Blueprint("register", __name__)

@register_bp.route("/register", methods=['GET', 'POST'])
@register_bp.route("/register.html", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                """
                SELECT COUNT(*) FROM users WHERE username = %s
                """, (username,)
            )
            count = cur.fetchone()[0]

            if count:
                return render_template(
                    "register.html", error=f"'{username}' already taken"
                )
            
            cur.execute(
                f"""
                INSERT INTO users (username, password, role) VALUES (%s, %s, %s)
                """, (username, password, role)
            )
            conn.commit()
            cur.close()
            conn.close()

            return render_template('register.html', success="User successfully created!")
        except Exception as e:
            logging.error(e)
            return render_template('register.html', error=e)
        
    return render_template('register.html')
