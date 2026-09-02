import json
import os
import subprocess
from datetime import datetime
from functools import wraps
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request, send_from_directory, session, url_for
from flask_session import Session
from werkzeug.utils import secure_filename

load_dotenv()

from config.database import db_execute, db_fetch_all, db_fetch_one

ROOT = Path(__file__).resolve().parent
UPLOAD_FOLDER = ROOT / 'uploads'
UPLOAD_FOLDER.mkdir(exist_ok=True)


def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='public')
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'edusubmit-secret-key')
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_FILE_DIR'] = str(ROOT / '.flask_session')
    app.config['SESSION_PERMANENT'] = False
    app.config['UPLOAD_FOLDER'] = str(UPLOAD_FOLDER)
    app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024
    Session(app)

    @app.route('/')
    def home():
        if 'user' not in session:
            return render_template('home.html')
        user = session['user']
        if user['role'] == 'teacher':
            return redirect(url_for('teacher_dashboard'))
        return redirect(url_for('student_dashboard'))

    @app.route('/unauthorized')
    def unauthorized():
        return render_template('unauthorized.html')

    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    @app.context_processor
    def inject_global_messages():
        error = session.pop('error', None)
        success = session.pop('success', None)
        return {'error': error, 'success': success, 'user': session.get('user')}

    def login_required(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if 'user' not in session:
                return redirect(url_for('auth_login'))
            return f(*args, **kwargs)
        return wrapper

    def role_required(role):
        def decorator(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                if 'user' not in session:
                    return redirect(url_for('auth_login'))
                if session['user']['role'] != role:
                    return redirect(url_for('unauthorized'))
                return f(*args, **kwargs)
            return wrapper
        return decorator

    @app.route('/auth/login', methods=['GET', 'POST'])
    def auth_login():
        if request.method == 'POST':
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '')
            try:
                user = db_fetch_one('SELECT * FROM users WHERE email = %s', (email,))
            except Exception:
                session['error'] = 'Database connection failed. Please start MySQL and try again.'
                return redirect(url_for('auth_login'))

            if not user or not __import__('bcrypt').checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
                session['error'] = 'Invalid email or password.'
                return redirect(url_for('auth_login'))

            session['user'] = {
                'user_id': user['user_id'],
                'name': user['name'],
                'email': user['email'],
                'role': user['role']
            }
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            if user['role'] == 'teacher':
                return redirect(url_for('teacher_dashboard'))
            return redirect(url_for('student_dashboard'))

        role_hint = request.args.get('role')
        return render_template('login.html', roleHint=role_hint)

    @app.route('/auth/register', methods=['GET', 'POST'])
    def auth_register():
        if request.method == 'POST':
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '')
            role = request.form.get('role', 'student')

            if not name or not email or len(password) < 6:
                session['error'] = 'Please enter valid details and password length must be at least 6 characters.'
                return redirect(url_for('auth_register'))

            existing = db_fetch_one('SELECT * FROM users WHERE email = %s', (email,))
            if existing:
                session['error'] = 'Email already registered.'
                return redirect(url_for('auth_register'))

            hashed = __import__('bcrypt').hashpw(password.encode('utf-8'), __import__('bcrypt').gensalt()).decode('utf-8')
            db_execute('INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)', (name, email, hashed, role))
            session['success'] = 'Registration successful. Please login.'
            return redirect(url_for('auth_login'))

        return render_template('register.html')

    @app.route('/auth/logout')
    def auth_logout():
        session.clear()
        return redirect(url_for('auth_login'))

    @app.route('/student/dashboard')
    @login_required
    @role_required('student')
    def student_dashboard():
        student_id = session['user']['user_id']
        assignments = db_fetch_all('SELECT * FROM assignments ORDER BY due_date ASC')
        submissions = db_fetch_all('SELECT * FROM submissions WHERE student_id = %s', (student_id,))

        total_assignments = len(assignments)
        submitted_assignments = sum(1 for s in submissions if s['status'] in ('Graded', 'Pending', 'Late'))
        pending_assignments = max(total_assignments - submitted_assignments, 0)
        graded_assignments = sum(1 for s in submissions if s['status'] == 'Graded')

        return render_template('student/dashboard.html', totalAssignments=total_assignments, submittedAssignments=submitted_assignments, pendingAssignments=pending_assignments, gradedAssignments=graded_assignments, assignments=assignments, submissions=submissions)

    @app.route('/student/assignments')
    @login_required
    @role_required('student')
    def student_assignments():
        assignments = db_fetch_all('SELECT * FROM assignments ORDER BY due_date ASC')
        submissions = db_fetch_all('SELECT * FROM submissions WHERE student_id = %s', (session['user']['user_id'],))
        submission_map = {s['assignment_id']: s for s in submissions}
        return render_template('student/assignments.html', assignments=assignments, submissionMap=submission_map)

    @app.route('/student/assignment/<int:assignment_id>')
    @login_required
    @role_required('student')
    def student_assignment_detail(assignment_id):
        assignment = db_fetch_one('SELECT * FROM assignments WHERE assignment_id = %s', (assignment_id,))
        submission = db_fetch_one('SELECT * FROM submissions WHERE assignment_id = %s AND student_id = %s', (assignment_id, session['user']['user_id']))
        return render_template('student/assignment-detail.html', assignment=assignment, submission=submission)

    @app.route('/student/assignment/<int:assignment_id>/submit', methods=['POST'])
    @login_required
    @role_required('student')
    def submit_assignment(assignment_id):
        file = request.files.get('pdfFile')
        if not file or not file.filename:
            session['error'] = 'Please upload a PDF file.'
            return redirect(url_for('student_assignment_detail', assignment_id=assignment_id))

        if file.mimetype != 'application/pdf':
            session['error'] = 'Only PDF files are allowed.'
            return redirect(url_for('student_assignment_detail', assignment_id=assignment_id))

        existing = db_fetch_one('SELECT * FROM submissions WHERE assignment_id = %s AND student_id = %s', (assignment_id, session['user']['user_id']))
        if existing:
            session['error'] = 'You have already submitted this assignment.'
            return redirect(url_for('student_assignment_detail', assignment_id=assignment_id))

        assignment = db_fetch_one('SELECT * FROM assignments WHERE assignment_id = %s', (assignment_id,))
        if not assignment:
            session['error'] = 'Assignment not found.'
            return redirect(url_for('student_assignments'))

        filename = secure_filename(file.filename)
        unique_name = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{__import__('uuid').uuid4().hex}{Path(filename).suffix}"
        save_path = UPLOAD_FOLDER / unique_name
        file.save(save_path)

        status = 'Late' if datetime.utcnow().date() > datetime.strptime(str(assignment['due_date']), '%Y-%m-%d').date() else 'Pending'
        submission_date = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        db_execute('INSERT INTO submissions (assignment_id, student_id, file_path, submission_date, status) VALUES (%s, %s, %s, %s, %s)', (assignment_id, session['user']['user_id'], f'/uploads/{unique_name}', submission_date, status))

        session['success'] = 'Assignment submitted successfully.'
        return redirect(url_for('student_assignments'))

    @app.route('/student/marks')
    @login_required
    @role_required('student')
    def student_marks():
        rows = db_fetch_all('SELECT s.*, a.title, a.subject_name FROM submissions s JOIN assignments a ON s.assignment_id = a.assignment_id WHERE s.student_id = %s ORDER BY s.submission_date DESC', (session['user']['user_id'],))
        return render_template('student/marks.html', submissions=rows)

    @app.route('/teacher/dashboard')
    @login_required
    @role_required('teacher')
    def teacher_dashboard():
        students = db_fetch_all('SELECT * FROM users WHERE role = %s', ('student',))
        assignments = db_fetch_all('SELECT * FROM assignments')
        submissions = db_fetch_all('SELECT * FROM submissions')
        pending_reviews = sum(1 for s in submissions if s['status'] == 'Pending')
        late_submissions = sum(1 for s in submissions if s['status'] == 'Late')

        payload = {'assignments': assignments, 'submissions': submissions, 'students': students}
        script = ROOT / 'python' / 'analytics.py'
        result = subprocess.run(['python3', str(script), json.dumps(payload)], capture_output=True, text=True, check=False)
        analytics = json.loads(result.stdout) if result.stdout.strip() else {
            'completion_rate': 0,
            'recommendation': 'Need more student engagement',
            'status_counts': {},
            'grade_distribution': {}
        }

        return render_template('teacher/dashboard.html', students=len(students), assignments=len(assignments), pendingReviews=pending_reviews, lateSubmissions=late_submissions, submissions=submissions[:5], analytics=analytics)

    @app.route('/teacher/assignments', methods=['GET', 'POST'])
    @login_required
    @role_required('teacher')
    def teacher_assignments():
        if request.method == 'POST':
            subject_name = request.form.get('subject_name')
            title = request.form.get('title')
            description = request.form.get('description')
            max_marks = request.form.get('max_marks')
            due_date = request.form.get('due_date')
            db_execute('INSERT INTO assignments (subject_name, title, description, max_marks, due_date, created_by, created_at) VALUES (%s, %s, %s, %s, %s, %s, NOW())', (subject_name, title, description, max_marks, due_date, session['user']['user_id']))
            session['success'] = 'Assignment created successfully.'
            return redirect(url_for('teacher_assignments'))

        rows = db_fetch_all('SELECT * FROM assignments ORDER BY created_at DESC')
        return render_template('teacher/assignments.html', assignments=rows)

    @app.route('/teacher/assignments/edit/<int:assignment_id>', methods=['POST'])
    @login_required
    @role_required('teacher')
    def teacher_edit_assignment(assignment_id):
        subject_name = request.form.get('subject_name')
        title = request.form.get('title')
        description = request.form.get('description')
        max_marks = request.form.get('max_marks')
        due_date = request.form.get('due_date')
        db_execute('UPDATE assignments SET subject_name = %s, title = %s, description = %s, max_marks = %s, due_date = %s WHERE assignment_id = %s', (subject_name, title, description, max_marks, due_date, assignment_id))
        session['success'] = 'Assignment updated successfully.'
        return redirect(url_for('teacher_assignments'))

    @app.route('/teacher/assignments/delete/<int:assignment_id>', methods=['POST'])
    @login_required
    @role_required('teacher')
    def teacher_delete_assignment(assignment_id):
        db_execute('DELETE FROM assignments WHERE assignment_id = %s', (assignment_id,))
        session['success'] = 'Assignment deleted successfully.'
        return redirect(url_for('teacher_assignments'))

    @app.route('/teacher/submissions')
    @login_required
    @role_required('teacher')
    def teacher_submissions():
        rows = db_fetch_all('SELECT s.*, a.title, u.name FROM submissions s JOIN assignments a ON s.assignment_id = a.assignment_id JOIN users u ON s.student_id = u.user_id ORDER BY s.submission_date DESC')
        return render_template('teacher/submissions.html', submissions=rows)

    @app.route('/teacher/submissions/evaluate/<int:submission_id>', methods=['POST'])
    @login_required
    @role_required('teacher')
    def teacher_evaluate_submission(submission_id):
        marks_obtained = request.form.get('marks_obtained')
        feedback = request.form.get('teacher_feedback', '')
        db_execute('UPDATE submissions SET marks_obtained = %s, teacher_feedback = %s, status = %s WHERE submission_id = %s', (marks_obtained, feedback, 'Graded', submission_id))
        session['success'] = 'Submission evaluated successfully.'
        return redirect(url_for('teacher_submissions'))

    @app.route('/admin/dashboard')
    @login_required
    @role_required('admin')
    def admin_dashboard():
        users = db_fetch_all('SELECT * FROM users')
        assignments = db_fetch_all('SELECT * FROM assignments')
        submissions = db_fetch_all('SELECT * FROM submissions')
        return render_template('admin/dashboard.html', users=len(users), assignments=len(assignments), submissions=len(submissions), usersList=users)

    @app.route('/admin/users')
    @login_required
    @role_required('admin')
    def admin_users():
        rows = db_fetch_all('SELECT * FROM users ORDER BY created_at DESC')
        return render_template('admin/users.html', users=rows)

    @app.route('/admin/users/create', methods=['POST'])
    @login_required
    @role_required('admin')
    def admin_create_user():
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')
        hashed = __import__('bcrypt').hashpw(password.encode('utf-8'), __import__('bcrypt').gensalt()).decode('utf-8')
        db_execute('INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)', (name, email, hashed, role))
        session['success'] = 'User created successfully.'
        return redirect(url_for('admin_users'))

    @app.route('/admin/users/update/<int:user_id>', methods=['POST'])
    @login_required
    @role_required('admin')
    def admin_update_user(user_id):
        name = request.form.get('name')
        email = request.form.get('email')
        role = request.form.get('role')
        db_execute('UPDATE users SET name = %s, email = %s, role = %s WHERE user_id = %s', (name, email, role, user_id))
        session['success'] = 'User updated successfully.'
        return redirect(url_for('admin_users'))

    @app.route('/admin/users/delete/<int:user_id>', methods=['POST'])
    @login_required
    @role_required('admin')
    def admin_delete_user(user_id):
        db_execute('DELETE FROM users WHERE user_id = %s', (user_id,))
        session['success'] = 'User deleted successfully.'
        return redirect(url_for('admin_users'))

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('error.html', message='Page not found.'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('error.html', message='Something went wrong.'), 500

    return app


app = create_app()


if __name__ == '__main__':
    app.run(host=os.getenv('HOST', '0.0.0.0'), port=int(os.getenv('PORT', '3000')), debug=True)
