from flask import Blueprint, redirect, render_template, render_template_string, url_for, request, flash, current_app, jsonify
import logging, os, pickle, base64
from werkzeug.utils import secure_filename

from .session import get_user
from app.database import get_db_connection

course_bp = Blueprint("courses", __name__)

@course_bp.route("/courses")
@course_bp.route("/courses.html")
def courses():
    user = get_user()
    enrolled_courses = []

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Fetch currently enrolled courses for logged-in users
                if user:
                    cur.execute("SELECT course_id FROM enrollments WHERE student_id = %s", (user.user_id,))
                    enrolled_courses = {row[0] for row in cur.fetchall()}

                # Fetch all courses
                cur.execute("SELECT course_id, title, description, image_path FROM courses")
                all_courses = cur.fetchall()

                # Filter out courses the user is already enrolled in
                if user:
                    courses = [course for course in all_courses if course[0] not in enrolled_courses]
                else:
                    courses = all_courses

    except Exception as e:
        logging.error(f"Error: {e}")
        courses = []

    return render_template('courses.html', user=user, courses=courses)

@course_bp.route('/search_course', methods=['GET'])
def search_course():
    user = get_user()

    search_query = request.args.get('search_query', '')
    
    template = """
    {% extends "base.html" %}
    {% block title %}Course Suggestions{% endblock %}
    {% block content %}
    <div class="container mt-5">
        <h1>Suggest Course</h1>
        <form method="get" action="{{ url_for('courses.search_course') }}">
            <div class="form-group">
                <label for="search_query">Course Topic:</label>
                <input id="search_query" name="search_query" class="form-control" type="text" placeholder="Enter course topic..." value="{{ search_query or '' }}">
            </div>
            <button type="submit" class="btn btn-primary">Search</button>
        </form>
        {% if search_query %}
            <h2 class="mt-5">Suggestion:</h2>
            <p>{{ suggestion }}</p>
        {% endif %}
    </div>
    {% endblock %}
    """
    
    return render_template_string(template, search_query=search_query, suggestion=search_query, user=user)

@course_bp.route("/add_course", methods=['GET', 'POST'])
def add_course():
    user = get_user()

    if user.role not in ['instructor', 'admin']:
        return redirect(url_for('courses.courses'))

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        instructor_id = user.user_id
        image = request.files.get('image')

        if image:
            filename = secure_filename(image.filename)
            upload_folder = current_app.config['UPLOAD_FOLDER']
            
            # Validate file extension
            allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
            if '.' not in filename or filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
                flash('Invalid file type. Please upload an image.', 'danger')
                return redirect(request.url)

            image_path = os.path.join(upload_folder, filename)
            image.save(image_path)
            image_path = os.path.join('images', filename)
        else:
            image_path = None
    
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO courses (title, description, instructor_id, image_path) 
                    VALUES (%s, %s, %s, %s)
                    """,
                    (title, description, instructor_id, image_path)
                )
                conn.commit()
        flash('Course added successfully', 'success')
        return render_template('add_course.html', user=user)
    
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT user_id, username FROM users WHERE role = 'instructor'")
                instructors = cur.fetchall()
    except Exception as e:
        flash(f"An error occured while fetching instructors: {e}", 'danger')
        instructors = []

    return render_template('add_course.html', user=user, instructors=instructors)

@course_bp.route('/load_data', methods=['POST'])
def load_data():
    user = get_user()

    if not user:
        return jsonify({"error": "Authentication required"}), 401

    try:
        data = request.form.get('data')
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # This is a placeholder for a safe data loading mechanism.
        # The original code using pickle is unsafe and has been removed.
        # You should replace this with a safe serialization format like JSON.
        
        # Example of safe data handling with JSON:
        # try:
        #     obj = json.loads(data)
        #     # Process the object
        #     return jsonify({"data": obj}), 200
        # except json.JSONDecodeError:
        #     return jsonify({"error": "Invalid JSON data"}), 400

        return jsonify({"error": "Pickle deserialization is disabled for security reasons."}), 403
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@course_bp.route('/enroll/<int:course_id>')
def enroll(course_id):
    user = get_user()

    if user is None or user.role != 'student':
        return redirect(url_for('courses.courses'))
    
    student_id = user.user_id

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO enrollments (student_id, course_id)
                VALUES (%s, %s)
                """,
                (student_id, course_id)
            )
            conn.commit()

    return redirect(url_for('courses.courses'))

@course_bp.route('/unroll/<int:course_id>')
def unroll(course_id):
    user = get_user()

    student_id = user.user_id

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                DELETE FROM enrollments WHERE student_id = %s AND
                course_id = %s
                """,
                (student_id, course_id)
            )
            conn.commit()

    return redirect(url_for('profile.profile'))

@course_bp.route('/remove_course/<int:course_id>', methods=['GET', 'POST'])
def remove_course(course_id):
    user = get_user()

    if user is None:
        return redirect(url_for('index.index'))
    
    referrer = request.referrer

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM courses WHERE course_id = %s", (course_id,))
            conn.commit()

    if user.is_admin:
        if referrer and 'admin_dashboard' in referrer:
            return redirect(url_for('admin.admin_dashboard'))
        
    return redirect(url_for('courses.courses'))
