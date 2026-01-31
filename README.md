# Student Academic Management System (LMS)

A Flask-based Student Learning Management System designed to manage academic activities such as attendance, marks, assignments, fees, and communication between students and teachers in a centralized platform.

---

## 📌 Project Description

In many educational institutions, academic data is managed manually using registers, spreadsheets, and messaging applications. This results in data inconsistency, increased workload for teachers, and limited transparency for students.

The Student Academic Management System solves this problem by providing a role-based web application where:

- **Students** can view their attendance, marks, assignments, notices, and fees.
- **Teachers** can manage student records, post assignments, grade submissions, and communicate with students.

The system improves efficiency, transparency, and communication within the academic environment.

### Key Features

#### Student Features
- View attendance records and marks
- Track assignment deadlines and submissions
- Check fee status and payment history
- Receive notices from teachers
- Communicate with teachers via messaging

#### Teacher Features
- Post notices and announcements
- Create and manage assignments
- Grade student submissions with remarks
- View and manage student attendance and marks
- Direct messaging with students
- Manage fees and payment status

---

## 🛠️ Technologies Used

### Backend
- **Python** with Flask framework
- **Flask-SQLAlchemy** for database ORM
- **Flask-Login** for authentication and session management
- **Werkzeug** for password hashing and file security

### Frontend
- **HTML5** for structure
- **CSS3** for styling
- **Bootstrap 5** for responsive design
- **JavaScript** with AJAX for dynamic interactions

### Database
- **SQLite** for data persistence

---

## ▶️ How to Build and Run the Project

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation Steps

1. **Clone the Repository**
   ```bash
   git clone https://github.com/your-username/Student-academic-expense-manager.git
   cd Student-academic-expense-manager
   ```

2. **Create a Virtual Environment** (Recommended)
   ```bash
   python -m venv venv
   ```

3. **Activate Virtual Environment**
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Initialize the Database**
   ```bash
   python
   >>> from app import app, db
   >>> with app.app_context():
   ...     db.create_all()
   >>> exit()
   ```

6. **Run the Application**
   ```bash
   python app.py
   ```

7. **Access the Application**
   - Open your web browser and navigate to: `http://localhost:5000`
   - The application will redirect you to the login page
   - Login with your student or teacher credentials

---

## 📂 Project Structure

```
Student-academic-expense-manager/
├── app.py                    # Main Flask application with routes
├── models.py                 # Alternative database models structure
├── check_db.py               # Database utility functions
├── requirements.txt          # Project dependencies
├── README.md                 # Project documentation
├── .gitignore                # Git ignore rules
├── instance/                 # Instance-specific configuration files
├── scripts/                  # Utility scripts
│   └── add_notice_column.py  # Database migration scripts
├── static/
│   └── uploads/              # Directory for user file uploads
└── templates/
    ├── login.html            # Login page
    ├── register.html         # User registration page
    ├── dashboard.html        # Student dashboard
    └── teacher_dashboard.html # Teacher dashboard
```

---

## ⚠️ Known Limitations

- **Single Instance Deployment**: The application is designed for single-instance deployment. Concurrent access may require session management improvements.
- **File Upload Size**: No built-in file size limit; should be configured based on server capabilities.
- **Authentication**: No email verification or password reset functionality implemented.
- **Database**: SQLite is suitable for development and small deployment; production should use PostgreSQL or MySQL.
- **Scalability**: Optimized for small to medium-sized institutions; large deployments require caching and optimization.
- **API**: No RESTful API provided; all interactions through web forms and AJAX.
- **Mobile Responsiveness**: Bootstrap provides basic responsiveness; full mobile optimization is limited.

---

## 🚀 Possible Future Improvements

- Email notifications for assignments, grades, and announcements
- Advanced reporting with PDF generation
- Bulk operations for data import and grade management
- Calendar integration for deadline visualization
- Real-time notification dashboard
- Fine-grained role-based permissions
- Advanced search and filtering capabilities
- Mobile applications for iOS and Android
- Payment gateway integration for online fee payment
- Analytics dashboard for performance insights
- Two-factor authentication for enhanced security
- RESTful API for third-party integrations
- Support for multiple databases
- Docker containerization for deployment
- Backup and disaster recovery mechanisms

---

## 📝 Database Models

The application uses the following main models:

- **User**: Stores student and teacher information with role-based access
- **Attendance**: Tracks attendance records for students
- **Score**: Stores subject-wise marks for students
- **Notice**: Contains announcements posted by teachers
- **Fee**: Manages fee information and payment status
- **Assignment**: Stores assignment details created by teachers
- **AssignmentSubmission**: Tracks student submissions with grades
- **Message**: Enables direct communication between students and teachers
- **Course**: Organizes courses and curriculum

---

## 💾 Configuration

The application uses the following default configuration:

- **Secret Key**: Configured for development mode (change for production)
- **Database**: SQLite (`student_manager.db` in project root)
- **Upload Folder**: `static/uploads/` directory
- **Debug Mode**: Enabled for development

---

## 📋 License

This project is submitted as academic coursework and is intended for educational purposes.

---

## 👥 Notes for Evaluators

- The application demonstrates core web development concepts: authentication, database management, and full-stack development
- Code follows Python and Flask best practices for maintainability and readability
- Uses industry-standard libraries suitable for production environments
- Role-based access control separates student and teacher functionalities
- File upload capabilities with secure filename handling
- AJAX integration for improved user experience
