from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, UserMixin, login_user,
    login_required, logout_user, current_user
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import date
import os

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
    student_id = db.Column(db.Integer)
    teacher_id = db.Column(db.Integer)


class AssignmentSubmission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer)
    student_id = db.Column(db.Integer)
    file = db.Column(db.String(200))
    submitted_on = db.Column(db.Date, default=date.today)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer)
    receiver_id = db.Column(db.Integer)
    text = db.Column(db.Text)
    sent_on = db.Column(db.Date, default=date.today)

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

    return render_template(
        'dashboard.html',
        attendance=Attendance.query.filter_by(user_id=current_user.id).all(),
        scores=Score.query.filter_by(user_id=current_user.id).all(),
        notices=Notice.query.all(),
        fees=Fee.query.filter_by(student_id=current_user.id).all(),
        assignments=Assignment.query.filter_by(student_id=current_user.id).all(),
        submissions=AssignmentSubmission.query.filter_by(student_id=current_user.id).all(),
        messages=Message.query.filter_by(receiver_id=current_user.id).all()
    )

# ===================== TEACHER =====================

@app.route('/teacher-dashboard')
@login_required
def teacher_dashboard():
    if current_user.role != 'teacher':
        return "Access denied"

    return render_template(
        'teacher_dashboard.html',
        students=User.query.filter_by(role='student').all(),
        attendance=Attendance.query.all(),
        scores=Score.query.all(),
        notices=Notice.query.all(),
        fees=Fee.query.all(),
        assignments=Assignment.query.all(),
        messages=Message.query.filter_by(receiver_id=current_user.id).all()
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
    return redirect(url_for('teacher_dashboard'))


@app.route('/add-fee', methods=['POST'])
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


@app.route('/send-message', methods=['POST'])
@login_required
def send_message():
    msg = Message(
        sender_id=current_user.id,
        receiver_id=int(request.form['student_id']),
        text=request.form['message']
    )
    db.session.add(msg)
    db.session.commit()
    return redirect(url_for('teacher_dashboard'))

# ===================== RUN =====================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
