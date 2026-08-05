from flask import Flask,jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource, reqparse


app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///api_database.sqlite3'
db=SQLAlchemy(app)
api=Api(app)


class Course(db.Model):
    course_id=db.Column(db.Integer,primary_key=True)
    course_name=db.Column(db.String(50),nullable=False)
    course_code=db.Column(db.String(50),unique=True,nullable=False)
    course_description=db.Column(db.String(50))

class Student(db.Model):
    student_id=db.Column(db.Integer,primary_key=True)
    roll_number=db.Column(db.String(50),unique=True,nullable=True)
    first_name=db.Column(db.String(50),nullable=False)
    last_name=db.Column(db.String(50))

class Enrollment(db.Model):
    enrollment_id=db.Column(db.Integer, primary_key=True)
    student_id=db.Column(db.Integer,db.ForeignKey('student.student_id'), nullable=False)
    course_id=db.Column(db.Integer,db.ForeignKey('course.course_id'), nullable=False)


def course_to_dict(c):
    return {
        'course_id': c.course_id,
        'course_name': c.course_name,
        'course_code': c.course_code,
        'course_description': c.course_description
    }

def student_to_dict(s):
    return {
        'student_id': s.student_id,
        'roll_number': s.roll_number,
        'first_name': s.first_name,
        'last_name': s.last_name
    }

def enrollment_to_dict(e):
    return {
        'enrollment_id': e.enrollment_id,
        'student_id': e.student_id,
        'course_id': e.course_id
    }


course_parser = reqparse.RequestParser()
course_parser.add_argument('course_name', type=str)
course_parser.add_argument('course_code', type=str)
course_parser.add_argument('course_description', type=str)


class CourseAPI(Resource):
    def get(self, course_id):
        course = Course.query.get(course_id)
        if not course:
            return {'error_code': 'COURSE404', 'error_message': 'Course not found'}, 404
        return course_to_dict(course), 200

    def put(self, course_id):
        course = Course.query.get(course_id)
        if not course:
            return {'error_code': 'COURSE404', 'error_message': 'Course not found'}, 404

        args = course_parser.parse_args()
        if args['course_name'] is not None and args['course_name'].strip() == '':
            return {'error_code': 'COURSE001', 'error_message': 'Course Name is required'}, 400
        if args['course_code'] is not None and args['course_code'].strip() == '':
            return {'error_code': 'COURSE002', 'error_message': 'Course Code is required'}, 400

        if args['course_name'] is not None:
            course.course_name = args['course_name']
        if args['course_code'] is not None:
            course.course_code = args['course_code']
        if args['course_description'] is not None:
            course.course_description = args['course_description']

        db.session.commit()
        return course_to_dict(course), 200

    def delete(self, course_id):
        course = Course.query.get(course_id)
        if not course:
            return {'error_code': 'COURSE404', 'error_message': 'Course not found'}, 404
        db.session.delete(course)
        db.session.commit()
        return '', 200


class CourseListAPI(Resource):
    def post(self):
        args = course_parser.parse_args()
        if not args['course_name']:
            return {'error_code': 'COURSE001', 'error_message': 'Course Name is required'}, 400
        if not args['course_code']:
            return {'error_code': 'COURSE002', 'error_message': 'Course Code is required'}, 400

        existing = Course.query.filter_by(course_code=args['course_code']).first()
        if existing:
            return {'error_code': 'COURSE409', 'error_message': 'course_code already exists'}, 409

        course = Course(
            course_name=args['course_name'],
            course_code=args['course_code'],
            course_description=args['course_description']
        )
        db.session.add(course)
        db.session.commit()
        return course_to_dict(course), 201



student_parser = reqparse.RequestParser()
student_parser.add_argument('first_name', type=str)
student_parser.add_argument('last_name', type=str)
student_parser.add_argument('roll_number', type=str)


class StudentAPI(Resource):
    def get(self, student_id):
        student = Student.query.get(student_id)
        if not student:
            return {'error_code': 'STUDENT404', 'error_message': 'Student not found'}, 404
        return student_to_dict(student), 200

    def put(self, student_id):
        student = Student.query.get(student_id)
        if not student:
            return {'error_code': 'STUDENT404', 'error_message': 'Student not found'}, 404

        args = student_parser.parse_args()
        if args['roll_number'] is not None and args['roll_number'].strip() == '':
            return {'error_code': 'STUDENT001', 'error_message': 'Roll Number required'}, 400
        if args['first_name'] is not None and args['first_name'].strip() == '':
            return {'error_code': 'STUDENT002', 'error_message': 'First Name is required'}, 400

        if args['roll_number'] is not None:
            student.roll_number = args['roll_number']
        if args['first_name'] is not None:
            student.first_name = args['first_name']
        if args['last_name'] is not None:
            student.last_name = args['last_name']

        db.session.commit()
        return student_to_dict(student), 200

    def delete(self, student_id):
        student = Student.query.get(student_id)
        if not student:
            return {'error_code': 'STUDENT404', 'error_message': 'Student not found'}, 404
        db.session.delete(student)
        db.session.commit()
        return '', 200


class StudentListAPI(Resource):
    def post(self):
        args = student_parser.parse_args()
        if not args['roll_number']:
            return {'error_code': 'STUDENT001', 'error_message': 'Roll Number required'}, 400
        if not args['first_name']:
            return {'error_code': 'STUDENT002', 'error_message': 'First Name is required'}, 400

        existing = Student.query.filter_by(roll_number=args['roll_number']).first()
        if existing:
            return {'error_code': 'STUDENT409', 'error_message': 'Student already exists'}, 409

        student = Student(
            roll_number=args['roll_number'],
            first_name=args['first_name'],
            last_name=args['last_name']
        )
        db.session.add(student)
        db.session.commit()
        return student_to_dict(student), 201

enrollment_parser = reqparse.RequestParser()
enrollment_parser.add_argument('course_id', type=int)


class EnrollmentListAPI(Resource):
    def get(self, student_id):
        student = Student.query.get(student_id)
        if not student:
            return {'error_code': 'ENROLLMENT002', 'error_message': 'Student does not exist.'}, 400

        enrollments = Enrollment.query.filter_by(student_id=student_id).all()
        if not enrollments:
            return {'error_message': 'Student is not enrolled in any course'}, 404

        return [enrollment_to_dict(e) for e in enrollments], 200

    def post(self, student_id):
        student = Student.query.get(student_id)
        if not student:
            return {'error_code': 'STUDENT404', 'error_message': 'Student not found'}, 404

        args = enrollment_parser.parse_args()
        course_id = args['course_id']
        if not course_id:
            return {'error_code': 'ENROLLMENT001', 'error_message': 'Course does not exist'}, 400

        course = Course.query.get(course_id)
        if not course:
            return {'error_code': 'ENROLLMENT001', 'error_message': 'Course does not exist'}, 400

        enrollment = Enrollment(student_id=student_id, course_id=course_id)
        db.session.add(enrollment)
        db.session.commit()

        enrollments = Enrollment.query.filter_by(student_id=student_id).all()
        return [enrollment_to_dict(e) for e in enrollments], 201


class EnrollmentAPI(Resource):
    def delete(self, student_id, course_id):
        student = Student.query.get(student_id)
        if not student:
            return {'error_code': 'ENROLLMENT002', 'error_message': 'Student does not exist.'}, 400
        course = Course.query.get(course_id)
        if not course:
            return {'error_code': 'ENROLLMENT001', 'error_message': 'Course does not exist'}, 400

        enrollment = Enrollment.query.filter_by(student_id=student_id, course_id=course_id).first()
        if not enrollment:
            return {'error_message': 'Enrollment for the student not found'}, 404

        db.session.delete(enrollment)
        db.session.commit()
        return '', 200


api.add_resource(CourseListAPI, '/api/course')
api.add_resource(CourseAPI, '/api/course/<int:course_id>')
api.add_resource(StudentListAPI, '/api/student')
api.add_resource(StudentAPI, '/api/student/<int:student_id>')
api.add_resource(EnrollmentListAPI, '/api/student/<int:student_id>/course')
api.add_resource(EnrollmentAPI, '/api/student/<int:student_id>/course/<int:course_id>')


if __name__ == '__main__':
    app.run(debug=True)

