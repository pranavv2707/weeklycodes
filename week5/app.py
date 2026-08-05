from flask import Flask,render_template,request,redirect
from models import db,student,course,enrollments

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite3'
db.init_app(app)

@app.route("/")
def homepage():
    studentdata=student.query.all()
    return render_template("homepage.html", data=studentdata)

@app.route("/student/create",methods=["GET","POST"])
def create():
    if(request.method=="GET"):
        return render_template("addstudent.html")
    if(request.method=="POST"):
        fname,lname,rollnum,courses=request.form.get('f_name'),request.form.get('l_name'),request.form.get('roll'),request.form.getlist('courses')
        print("RECEIVED FROM FORM:", courses)
        existing=student.query.filter_by(roll_number=rollnum).first()
        if(existing): 
            return render_template("already_exists.html",s=existing)
        newstudent=student(roll_number=rollnum,first_name=fname,last_name=lname)
        db.session.add(newstudent)
        db.session.commit()
        db.session.flush()
        d={("course_" + str(i)): i for i in range(1,5)}
        for c in courses:
            if c in d:
                newenrollment = enrollments(
                estudent_id=newstudent.student_id, 
                ecourse_id=d[c]
                )
                db.session.add(newenrollment)
        db.session.commit()
    return redirect("/")

@app.route("/student/<int:student_id>/update",methods=["GET","POST"])
def update(student_id):
    s=student.query.filter_by(student_id=student_id).first()
    if(request.method=="GET"):
        enrolled=enrollments.query.filter_by(estudent_id=student_id).all()
        ids=[i.ecourse_id for i in enrolled]
        return render_template("update.html",s=s,ids=ids)
    if(request.method=="POST"):
        s.first_name,s.last_name=request.form.get('f_name'),request.form.get('l_name')
        courses=request.form.getlist('courses')
        enrollments.query.filter_by(estudent_id=student_id).delete()
        d={("course_" + str(i)): i for i in range(1,5)}
        for c in courses:
            if c in d:
                newenrollment = enrollments(
                estudent_id=s.student_id, 
                ecourse_id=d[c]
                )
                db.session.add(newenrollment)
        db.session.commit()
        return redirect("/")

@app.route("/student/<int:student_id>/delete")
def delete(student_id):
    delstudent=student.query.filter_by(student_id=student_id).first()
    if(delstudent):
        enrollments.query.filter_by(estudent_id=student_id).delete()
        db.session.delete(delstudent)
        db.session.commit()
    return redirect("/")

@app.route("/student/<int:student_id>")
def studentinfo(student_id):
    s=student.query.filter_by(student_id=student_id).first()
    usercourses=(
    db.session.query(course)
    .join(enrollments, course.course_id==enrollments.ecourse_id)
    .filter(enrollments.estudent_id==student_id)
    .all()
)   
    return render_template("student_details.html",s=s,c=usercourses)
if __name__ == "__main__":
    app.run(debug=True)