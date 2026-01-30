from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, UserMixin, login_user,
    login_required, logout_user, current_user
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import date
import os
from sqlalchemy import or_

# ===================== APP SETUP =====================

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app.config['SECRET_KEY'] = 'dev-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///student_manager.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

# ===================== MODELS =====================

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)


class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    status = db.Column(db.String(10))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(100))
    marks = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Notice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text)
    file = db.Column(db.String(200))


class Fee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150))
    amount = db.Column(db.Integer)
    due_date = db.Column(db.Date)
    student_id = db.Column(db.Integer)
    status = db.Column(db.String(20), default='Pending')


class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    subject = db.Column(db.String(100))
    deadline = db.Column(db.Date)
    file = db.Column(db.String(200))
    teacher_id = db.Column(db.Integer)


class AssignmentSubmission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer)
    student_id = db.Column(db.Integer)
    file = db.Column(db.String(200))
    submitted_on = db.Column(db.Date, default=date.today)
    marks = db.Column(db.Integer)
    remarks = db.Column(db.Text)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer)
    receiver_id = db.Column(db.Integer)
    text = db.Column(db.Text)
    sent_on = db.Column(db.Date, default=date.today)


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    code = db.Column(db.String(50))
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class StudentProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    full_name = db.Column(db.String(200))
    school = db.Column(db.String(200))
    course = db.Column(db.String(100))
    semester = db.Column(db.String(50))
    student_id = db.Column(db.String(100))
    profile_image = db.Column(db.String(200))

# ===================== LOGIN =====================

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


with app.app_context():
    db.create_all()

# ===================== AUTH =====================

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(
            username=request.form['username'],
            role=request.form['role']
        ).first()

        if user and check_password_hash(user.password, request.form['password']):
            login_user(user)
            return redirect(
                url_for('teacher_dashboard')
                if user.role == 'teacher'
                else url_for('dashboard')
            )

        return "Invalid credentials"

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if User.query.filter_by(username=request.form['username']).first():
            return "User already exists"

        user = User(
            username=request.form['username'],
            password=generate_password_hash(request.form['password']),
            role=request.form['role']
        )

        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# ===================== STUDENT =====================

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'student':
        return "Access denied"

    profile = StudentProfile.query.filter_by(user_id=current_user.id).first()

    submissions = db.session.query(
        AssignmentSubmission,
        Assignment.title.label('assignment_title'),
        Assignment.subject.label('assignment_subject')
    ).join(Assignment, AssignmentSubmission.assignment_id == Assignment.id)\
     .filter(AssignmentSubmission.student_id == current_user.id)\
     .all()
    # messages with sender info - both sent and received
    messages = db.session.query(
        Message,
        User.username.label('sender_name'),
        User.role.label('sender_role')
    ).join(User, Message.sender_id == User.id)\
     .filter(or_(Message.receiver_id == current_user.id, Message.sender_id == current_user.id))\
     .order_by(Message.sent_on.asc())\
     .all()

    teachers = User.query.filter_by(role='teacher').all()

    return render_template(
        'dashboard.html',
        profile=profile,
        courses=Course.query.all(),
        attendance=Attendance.query.filter_by(user_id=current_user.id).all(),
        scores=Score.query.filter_by(user_id=current_user.id).all(),
        notices=Notice.query.all(),
        fees=Fee.query.filter_by(student_id=current_user.id).all(),
        assignments=Assignment.query.all(),
        submissions=submissions,
        messages=messages,
        teachers=teachers,
        current_user_id=current_user.id
    )

# ===================== TEACHER =====================

@app.route('/teacher-dashboard')
@login_required
def teacher_dashboard():
    if current_user.role != 'teacher':
        return "Access denied"

    submissions = db.session.query(
        AssignmentSubmission,
        User.username.label('student_name'),
        Assignment.title.label('assignment_title')
    ).join(User, AssignmentSubmission.student_id == User.id)\
     .join(Assignment, AssignmentSubmission.assignment_id == Assignment.id)\
     .all()
    # messages with sender info - both sent and received
    messages = db.session.query(
        Message,
        User.username.label('sender_name'),
        User.role.label('sender_role')
    ).join(User, Message.sender_id == User.id)\
     .filter(or_(Message.receiver_id == current_user.id, Message.sender_id == current_user.id))\
     .order_by(Message.sent_on.asc())\
     .all()

    return render_template(
        'teacher_dashboard.html',
        students=User.query.filter_by(role='student').all(),
        courses=Course.query.all(),
        attendance=Attendance.query.all(),
        scores=Score.query.all(),
        notices=Notice.query.all(),
        fees=Fee.query.all(),
        assignments=Assignment.query.all(),
        submissions=submissions,
        messages=messages,
        current_user_id=current_user.id
    )


@app.route('/add-attendance', methods=['POST'])
@login_required
def add_attendance():
    db.session.add(Attendance(
        user_id=request.form['user_id'],
        date=date.fromisoformat(request.form['date']),
        status=request.form['status']
    ))
    db.session.commit()
    return redirect(url_for('teacher_dashboard'))


@app.route('/add-score', methods=['POST'])
@login_required
def add_score():
    db.session.add(Score(
        user_id=request.form['user_id'],
        subject=request.form['subject'],
        marks=request.form['marks']
    ))
    db.session.commit()
    return redirect(url_for('teacher_dashboard') + '#posted')


@app.route('/add-course', methods=['POST'])
@login_required
def add_course():
    if current_user.role != 'teacher':
        return "Access denied"
    
    course = Course(
        name=request.form['name'],
        code=request.form.get('code', ''),
        teacher_id=current_user.id
    )
    db.session.add(course)
    db.session.commit()
    flash('Course added successfully!', 'success')
    return redirect(url_for('teacher_dashboard') + '#courses')


@app.route('/fee', methods=['POST'])
@login_required
def add_fee():
    db.session.add(Fee(
        title=request.form['title'],
        amount=request.form['amount'],
        due_date=date.fromisoformat(request.form['due_date']),
        student_id=request.form['student_id']
    ))
    db.session.commit()
    return redirect(url_for('teacher_dashboard'))


@app.route('/add-assignment', methods=['POST'])
@login_required
def add_assignment():
    if current_user.role != 'teacher':
        return "Access denied"
    
    filename = None
    if 'file' in request.files:
        file = request.files['file']
        if file.filename != '':
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    
    db.session.add(Assignment(
        title=request.form['title'],
        subject=request.form['subject'],
        deadline=date.fromisoformat(request.form['deadline']),
        file=filename,
        teacher_id=current_user.id
    ))
    db.session.commit()
    flash('Assignment posted successfully!', 'success')
    return redirect(url_for('teacher_dashboard') + '#assignments')


@app.route('/send-message', methods=['POST'])
@login_required
def send_message():
    receiver_id = int(request.form.get('receiver_id') or request.form.get('student_id') or request.form.get('teacher_id'))
    message_text = request.form.get('message')
    
    # Validate sender and receiver are different
    if receiver_id == current_user.id:
        return jsonify({'success': False, 'message': 'Cannot send message to yourself'}), 400
    
    # Validate receiver exists
    receiver = User.query.get(receiver_id)
    if not receiver:
        return jsonify({'success': False, 'message': 'Invalid receiver'}), 400
    
    # Validate message text
    if not message_text or message_text.strip() == '':
        return jsonify({'success': False, 'message': 'Message cannot be empty'}), 400
    
    msg = Message(
        sender_id=current_user.id,
        receiver_id=receiver_id,
        text=message_text
    )
    db.session.add(msg)
    db.session.commit()
    # Return JSON response instead of redirecting
    return jsonify({'success': True, 'message': 'Message sent successfully!'})


@app.route('/api/messages')
@login_required
def api_messages():
    """API endpoint to fetch messages (for live refresh)"""
    messages = db.session.query(
        Message,
        User.username.label('sender_name'),
        User.role.label('sender_role'),
        User.id.label('sender_user_id')
    ).join(User, Message.sender_id == User.id)\
     .filter(or_(Message.receiver_id == current_user.id, Message.sender_id == current_user.id))\
     .order_by(Message.sent_on.asc())\
     .all()
    
    result = []
    for msg, sender_name, sender_role, sender_user_id in messages:
        result.append({
            'id': msg.id,
            'sender_id': msg.sender_id,
            'sender_name': sender_name,
            'sender_role': sender_role,
            'sender_user_id': sender_user_id,
            'text': msg.text,
            'sent_on': str(msg.sent_on),
            'is_sent': msg.sender_id == current_user.id
        })
    
    return jsonify(result)


@app.route('/grade-assignment', methods=['POST'])
@login_required
def grade_assignment():
    if current_user.role != 'teacher':
        return "Access denied"
    
    submission = AssignmentSubmission.query.get(request.form['submission_id'])
    if submission:
        submission.marks = request.form['marks']
        submission.remarks = request.form.get('remarks', '')
        db.session.commit()
    return redirect(url_for('teacher_dashboard'))


@app.route('/submit-assignment', methods=['POST'])
@login_required
def submit_assignment():
    if current_user.role != 'student':
        return "Access denied"
    
    filename = None
    if 'file' in request.files:
        file = request.files['file']
        if file.filename != '':
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    
    # Check if already submitted
    existing = AssignmentSubmission.query.filter_by(
        assignment_id=request.form['assignment_id'],
        student_id=current_user.id
    ).first()
    if existing:
        # Update
        existing.file = filename
        existing.submitted_on = date.today()
    else:
        db.session.add(AssignmentSubmission(
            assignment_id=request.form['assignment_id'],
            student_id=current_user.id,
            file=filename
        ))
    db.session.commit()
    return redirect(url_for('dashboard'))


@app.route('/update-profile', methods=['POST'])
@login_required
def update_profile():
    if current_user.role != 'student':
        return "Access denied"
    
    # Get or create profile
    profile = StudentProfile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        profile = StudentProfile(user_id=current_user.id)
        db.session.add(profile)
    
    # Update profile fields
    profile.full_name = request.form.get('full_name')
    profile.school = request.form.get('school')
    profile.course = request.form.get('course')
    profile.semester = request.form.get('semester')
    profile.student_id = request.form.get('student_id')
    
    # Handle profile image upload
    if 'profile_image' in request.files:
        file = request.files['profile_image']
        if file.filename != '':
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            profile.profile_image = filename
    
    db.session.commit()
    flash('Profile updated successfully!', 'success')
    return redirect(url_for('dashboard'))


# ===================== RUN =====================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
