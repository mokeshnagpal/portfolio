from flask import Flask, render_template, request, send_from_directory, redirect, url_for, flash
import json
import os

app = Flask(__name__)
app.secret_key = 'your_secure_secret_key'  # Change this to a secure key

def load_cv_data():
    """Load CV data from a JSON file."""
    with open('static/files/cv_data.json', 'r') as f:
        data = json.load(f)
    return data

# Load CV data once at startup
cv_data = load_cv_data()

@app.route('/')
def home():
    return render_template('index.html', cv=cv_data)

@app.route('/about')
def about():
    return render_template('about.html', cv=cv_data)

@app.route('/experience')
def experience():
    return render_template('experience.html', cv=cv_data)

@app.route('/education')
def education():
    return render_template('education.html', cv=cv_data)

@app.route('/skills')
def skills():
    return render_template('skills.html', cv=cv_data)

@app.route('/projects')
def projects():
    return render_template('projects.html', cv=cv_data)

@app.route('/patents')
def patents():
    return render_template('patents.html', cv=cv_data)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        if not name or not email or not subject or not message:
            flash('All fields are required!', 'danger')
            return redirect(url_for('contact'))
        # Here, you can process the message (store in DB or send an email)
        # For demonstration, we simply flash a success message.
        flash('Your message has been sent successfully!', 'success')
        # Optionally, log the message to a file (or other processing)
        with open("static/files/messages.log", "a") as log:
            log.write(f"From: {name} <{email}>\nSubject: {subject}\nMessage: {message}\n{'-'*40}\n")
        return redirect(url_for('contact'))
    return render_template('contact.html', cv=cv_data)

@app.route('/download_cv')
def download_cv():
    # The downloadable file is stored under static/files/
    return send_from_directory(
        directory=os.path.join(app.root_path, 'static', 'files'),
        path='mokesh nagpal.pdf',
        as_attachment=True
    )

# Route to serve the favicon from the static directory
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'static'),
        'favicon.ico',
        mimetype='logo/favico.icon'
    )
