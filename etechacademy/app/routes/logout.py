from flask import Blueprint, redirect, url_for

logout_bp = Blueprint("logout", __name__)

@logout_bp.route('/logout')
@logout_bp.route('/logout.html')
def logout():
    response = redirect(url_for('login.login'))
    response.set_cookie("session_id", "", expires=0)

    return response
