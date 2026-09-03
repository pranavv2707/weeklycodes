from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///week7_database.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Student(db.Model):
    __tablename__ = 'student'
    student_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    roll_number = db.Column(db.String, unique=True, nullable=False)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String)


class Course(db.Model):
    __tablename__ = 'course'
    course_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_code = db.Column(db.String, unique=True, nullable=False)
    course_name = db.Column(db.String, nullable=False)
    course_description = db.Column(db.String)


class Enrollment(db.Model):
    __tablename__ = 'enrollments'
    enrollment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    estudent_id = db.Column(db.Integer, db.ForeignKey('student.student_id'), nullable=False)
    ecourse_id = db.Column(db.Integer, db.ForeignKey('course.course_id'), nullable=False)


# ---------------------- STUDENT ROUTES ----------------------

@app.route('/')
def index():
    students = Student.query.all()
    return render_template('index.html', students=students)


@app.route('/student/create', methods=['GET'])
def student_create_form():
    return render_template('student_create.html')


@app.route('/student/create', methods=['POST'])
def student_create():
    roll = request.form.get('roll')
    f_name = request.form.get('f_name')
    l_name = request.form.get('l_name')

    existing = Student.query.filter_by(roll_number=roll).first()
    if existing:
        return render_template('student_exists.html')

    student = Student(roll_number=roll, first_name=f_name, last_name=l_name)
    db.session.add(student)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/student/<int:student_id>/update', methods=['GET'])
def student_update_form(student_id):
    student = Student.query.get_or_404(student_id)
    courses = Course.query.all()
    return render_template('student_update.html', student=student, courses=courses)


@app.route('/student/<int:student_id>/update', methods=['POST'])
def student_update(student_id):
    student = Student.query.get_or_404(student_id)
    student.first_name = request.form.get('f_name')
    student.last_name = request.form.get('l_name')

    course_id = request.form.get('course')
    if course_id:
        existing_enrollment = Enrollment.query.filter_by(
            estudent_id=student_id, ecourse_id=course_id
        ).first()
        if not existing_enrollment:
            enrollment = Enrollment(estudent_id=student_id, ecourse_id=course_id)
            db.session.add(enrollment)

    db.session.commit()
    return redirect(url_for('index'))


@app.route('/student/<int:student_id>/delete', methods=['GET'])
def student_delete(student_id):
    student = Student.query.get_or_404(student_id)
    Enrollment.query.filter_by(estudent_id=student_id).delete()
    db.session.delete(student)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/student/<int:student_id>', methods=['GET'])
def student_detail(student_id):
    student = Student.query.get_or_404(student_id)
    enrollments = db.session.query(Enrollment, Course).join(
        Course, Enrollment.ecourse_id == Course.course_id
    ).filter(Enrollment.estudent_id == student_id).all()
    return render_template('student_detail.html', student=student, enrollments=enrollments)


@app.route('/student/<int:student_id>/withdraw/<int:course_id>', methods=['GET'])
def student_withdraw(student_id, course_id):
    Enrollment.query.filter_by(estudent_id=student_id, ecourse_id=course_id).delete()
    db.session.commit()
    return redirect(url_for('index'))


# ---------------------- COURSE ROUTES ----------------------

@app.route('/courses', methods=['GET'])
def courses_index():
    courses = Course.query.all()
    return render_template('courses.html', courses=courses)


@app.route('/course/create', methods=['GET'])
def course_create_form():
    return render_template('course_create.html')


@app.route('/course/create', methods=['POST'])
def course_create():
    code = request.form.get('code')
    c_name = request.form.get('c_name')
    desc = request.form.get('desc')

    existing = Course.query.filter_by(course_code=code).first()
    if existing:
        return render_template('course_exists.html')

    course = Course(course_code=code, course_name=c_name, course_description=desc)
    db.session.add(course)
    db.session.commit()
    return redirect(url_for('courses_index'))


@app.route('/course/<int:course_id>/update', methods=['GET'])
def course_update_form(course_id):
    course = Course.query.get_or_404(course_id)
    return render_template('course_update.html', course=course)


@app.route('/course/<int:course_id>/update', methods=['POST'])
def course_update(course_id):
    course = Course.query.get_or_404(course_id)
    course.course_name = request.form.get('c_name')
    course.course_description = request.form.get('desc')
    db.session.commit()
    return redirect(url_for('courses_index'))


@app.route('/course/<int:course_id>/delete', methods=['GET'])
def course_delete(course_id):
    course = Course.query.get_or_404(course_id)
    Enrollment.query.filter_by(ecourse_id=course_id).delete()
    db.session.delete(course)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/course/<int:course_id>', methods=['GET'])
def course_detail(course_id):
    course = Course.query.get_or_404(course_id)
    students = db.session.query(Enrollment, Student).join(
        Student, Enrollment.estudent_id == Student.student_id
    ).filter(Enrollment.ecourse_id == course_id).all()
    return render_template('course_detail.html', course=course, students=students)


if __name__ == '__main__':
    app.run(debug=True)
