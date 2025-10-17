from flask import Blueprint, render_template_string, render_template, request
from .session import get_user
from app.database import get_db_connection

index_bp = Blueprint("index", __name__)

@index_bp.route('/', methods=['GET', 'POST'])
@index_bp.route('/index', methods=['GET', 'POST'])
@index_bp.route('/index.html', methods=['GET', 'POST'])
def index():
    user = get_user()
    search_results = []
    search_query = ''

    if request.method == 'POST':
        search_query = request.form.get('search_query', '')

        if search_query:
            try:
                with get_db_connection() as conn:
                    with conn.cursor() as cur:
                        cur.execute(
                            """
                            SELECT course_id, title, description FROM courses WHERE title LIKE %s
                            """,
                            (search_query + '%',)
                        )
                        search_results = cur.fetchall()
            except Exception as e:
                print("Error:", e)
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT c.title, c.description, c.image_path, COUNT(e.student_id) as enrollment_count
                    FROM courses c
                    LEFT JOIN enrollments e ON c.course_id = e.course_id
                    GROUP BY c.course_id
                    ORDER BY enrollment_count DESC
                    LIMIT 3
                    """
                )
                top_courses = cur.fetchall()

    except Exception as e:
        print("Error:", e)  # Debug print
        top_courses = []

    return render_template('index.html', user=user, search_results=search_results, search_query=search_query, courses=top_courses)