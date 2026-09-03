import os
import csv
from flask import Flask, render_template, request
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

app = Flask(__name__)

def read_csv():
    data = []
    if not os.path.exists('data.csv'):
        return data
    with open('data.csv', mode='r', encoding='utf-8-sig') as file:
        reader = csv.reader(file)
        try:
            next(reader)
        except StopIteration:
            return data
            
        for row in reader:
            if len(row) < 3:
                continue
            s_id = row[0].strip()
            c_id = row[1].strip()
            m_val = row[2].strip()
            
            data.append({
                'student_id': s_id,
                'course_id': c_id,
                'marks': int(m_val) if m_val.isdigit() else 0
            })
    return data

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')
    
    id_type = request.form.get('ID')
    id_value = request.form.get('id_value')
    
    if not id_type or not id_value or not id_value.strip():
        return render_template('error.html')
    
    search_val = id_value.strip()
    all_data = read_csv()
    
    if not all_data:
        return render_template('error.html')
        
    if id_type == 'student_id':
        student_records = [row for row in all_data if row['student_id'] == search_val]
        if not student_records:
            return render_template('error.html')
        
        total_marks = sum(row['marks'] for row in student_records)
        return render_template('student_details.html', records=student_records, total_marks=total_marks)
        
    elif id_type == 'course_id':
        course_marks = [row['marks'] for row in all_data if row['course_id'] == search_val]
        if not course_marks:
            return render_template('error.html')
        
        max_marks = max(course_marks)
        avg_marks = sum(course_marks) / len(course_marks)
        
        plt.figure()
        plt.hist(course_marks, bins=10, edgecolor='black')
        plt.xlabel('Marks')
        plt.ylabel('Frequency')
        
        if not os.path.exists('static'):
            os.makedirs('static')
            
        plot_path = os.path.join('static', 'histogram.png')
        plt.savefig(plot_path)
        plt.close()
        
        return render_template('course_details.html', avg_marks=round(avg_marks, 2), max_marks=max_marks)
        
    return render_template('error.html')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)