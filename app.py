from flask import Flask, render_template, request, send_from_directory, redirect, url_for, flash
import json
import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'fallback_secret_key')

# Load Firebase credentials from the environment variable
firebase_credentials_str = os.environ.get('FIREBASE_CREDENTIALS')
if not firebase_credentials_str:
    raise ValueError("FIREBASE_CREDENTIALS environment variable not set.")

firebase_credentials_dict = json.loads(firebase_credentials_str)

# Replace literal '\\n' with actual newline characters in the private key
if 'private_key' in firebase_credentials_dict:
    firebase_credentials_dict['private_key'] = firebase_credentials_dict['private_key'].replace('\\n', '\n')

# Initialize Firebase Admin with the credentials dictionary
cred = credentials.Certificate(firebase_credentials_dict)
firebase_admin.initialize_app(cred)
db = firestore.client()

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
        # Save the message to Firebase Firestore
        try:
            doc_ref = db.collection('messages').document()  # Auto-generated document ID
            doc_ref.set({
                'name': name,
                'email': email,
                'subject': subject,
                'message': message,
                'timestamp': firestore.SERVER_TIMESTAMP,
            })
            flash('Your message has been sent successfully!', 'success')
        except Exception as e:
            flash('An error occurred while sending your message. Please try again later.', 'danger')
            print(f"Error saving message to Firebase: {e}")
        # Optionally, also log the message to a local file
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

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'static'),
        'favicon.ico',
        mimetype='logo/favico.icon'
    )
