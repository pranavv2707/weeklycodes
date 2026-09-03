import pyhtml as h
from jinja2 import Template
import matplotlib.pyplot as plt
import csv 
import sys

OUTPUT_HTML= "output.html"
CSV_FILE="data.csv"
HIST_IMAGE="histogram.png"
student_text=Template("""<!DOCTYPE HTML>
<html>
<meta charset='utf-8'>

<head>
    <h1>
        Student details
    </h1>
</head>

<body>
    <p>
    <table border="1">
        <tr>
            <th>Student id</th>
            <th>Course id</th>
            <th>Marks</th>
        </tr>
        {%for row in rows%}
        <tr>
            <td>{{row['Student id']}}</td>
            <td>{{row['Course id']}}</td>
            <td>{{row['Marks']}}</td>
        </tr>
        {% endfor %}
        <tr>
            <td colspan="2" align="center">Total marks </td>
            <td>{{something}}</td>
        </tr>
    </table>
    <p>
</body>

</html>""")

coursetext=Template("""<!DOCTYPE html>
<meta charset="utf-8">
<html>
<header>
    <h1>
        Course details
    </h1>
</header>

<body>
    <table border="1">
        <tr>
            <th>Average marks</th>
            <th>Maximum marks</th>
        </tr>
        <tr>
            <td>{{avg}}</td>
            <td>{{maxm}}</td>
        </tr>
    </table>
    <img src="{{image}}">
</body>

</html>""")

errormessage=Template("""<!DOCTYPE HTML>
<html>
<meta charset='utf-8'>

<head>
    <h1>
        Wrong inputs
    </h1>
</head>

<body>
    <p>
        Something went wrong
    <p>
</body> 
</html>""")

def errorfunction():
    with open(OUTPUT_HTML,"w") as f:
        f.write(errormessage.render())

def dataload():
    with open(CSV_FILE, "r") as f:
        reader = csv.DictReader(f)
        return [{k.strip(): v.strip() for k, v in row.items()} for row in reader]
    
def coursefunction(course_id,data):
    marks=[(int(r["Marks"]) ) for r in data if r["Course id"]==course_id]
    if not marks:
        errorfunction()
        return
    avg,maxm=round(sum(marks)/len(marks),2),max(marks)
    
    plt.figure()
    plt.hist(marks,bins=5,rwidth=0.5)
    plt.xlabel("Marks")
    plt.ylabel("Frequency")
    plt.savefig(HIST_IMAGE)
    plt.close()
    html=coursetext.render(avg=avg,maxm=maxm,image=HIST_IMAGE)
    with open(OUTPUT_HTML,"w") as f:
        f.write(html)

def studentfunction(student_id,data):
    rows=[r for r in data if r["Student id"]==student_id]
    if(not rows):
        errorfunction()
        return 
    total=sum(int(r["Marks"]) for r in rows)
    with open(OUTPUT_HTML,"w") as f:
        f.write(student_text.render(rows=rows,something=total))


def main():
    if(len(sys.argv)!=3 or sys.argv[1] not in {"-s","-c"}):
        errorfunction()
        return 
    c_or_s,id=sys.argv[1],sys.argv[2].strip()
    try:
        data = dataload()
    except FileNotFoundError:
        errorfunction()
        return 
    if(c_or_s)=="-c":
        coursefunction(id,data)
    else:
        studentfunction(id,data)

if __name__ == "__main__":
    main()