from flask import Flask, render_template, request, flash, redirect, url_for
import os
from werkzeug.utils import secure_filename
from utils import extract_text, evaluate_similarity

app = Flask(__name__)
app.secret_key = "secret_key"
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html', score=None, feedback=None)

@app.route('/evaluate', methods=['POST'])
def evaluate():
    all_results = []
    correct_text = ""

    # Handle Correct Answer (Key)
    if 'correct_file' in request.files and request.files['correct_file'].filename != '':
        correct_file = request.files['correct_file']
        if allowed_file(correct_file.filename):
            correct_filename = secure_filename(correct_file.filename)
            correct_path = os.path.join(app.config['UPLOAD_FOLDER'], correct_filename)
            correct_file.save(correct_path)
            correct_text = extract_text(correct_path)
        else:
            flash('Correct key file type not supported.')
            return redirect(url_for('index'))
    elif 'correct_text' in request.form and request.form['correct_text'].strip():
        correct_text = request.form['correct_text'].strip()

    if not correct_text:
        flash('Please provide the correct answer key.')
        return redirect(url_for('index'))

    # Handle Student Answers (Individual Batch Processing)
    student_files = request.files.getlist('student_file')
    if student_files and any(f.filename != '' for f in student_files):
        for student_file in student_files:
            if student_file and allowed_file(student_file.filename):
                student_filename = secure_filename(student_file.filename)
                student_path = os.path.join(app.config['UPLOAD_FOLDER'], student_filename)
                student_file.save(student_path)
                
                # Process individual file
                student_text = extract_text(student_path)
                if student_text:
                    score, feedback = evaluate_similarity(student_text, correct_text)
                    all_results.append({
                        'filename': student_filename,
                        'score': score,
                        'feedback': feedback
                    })
    elif 'student_text' in request.form and request.form['student_text'].strip():
        student_text = request.form['student_text'].strip()
        score, feedback = evaluate_similarity(student_text, correct_text)
        all_results.append({
            'filename': 'Direct Text Input',
            'score': score,
            'feedback': feedback
        })

    if not all_results:
        flash('No valid student answers provided.')
        return redirect(url_for('index'))

    return render_template('index.html', results=all_results)

if __name__ == '__main__':
    # Using port 8000 to avoid common Windows port conflicts (Port 5000 is often occupied)
    app.run(debug=True, port=8000)
