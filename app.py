from flask import Flask, render_template, request, send_from_directory, redirect, url_for, flash
import json
import os
from dotenv import load_dotenv
import firebase_admin
import requests
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
try:
    firebase_admin.initialize_app(cred)
except Exception as e:
    print(e)
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

@app.route('/work_experiences')
def work_experiences():
    return render_template('work_experiences.html', cv=cv_data)

@app.route('/voluntary_works')
def voluntary_works():
    return render_template('voluntary_works.html', cv=cv_data)

@app.route('/education')
def education():
    return render_template('education.html', cv=cv_data)

@app.route('/skills')
def skills():
    cv_data['tech_skills'] = {
        cat: [skill.strip() for skill in items.split(',')]
        for cat, items in cv_data['technical_skills'].items()
    }
    return render_template('skills.html', cv=cv_data)

CATEGORY_BADGES = {
    "Major Project": "bg-primary",
    "Minor Project": "bg-success",
    "Mini Project":  "bg-secondary",
}

@app.route('/projects')
def projects():
    # read query parameters
    filter_by    = request.args.get('filter')
    filter_value = request.args.get('value')

    # all projects
    all_projects = cv_data.get('projects', [])

    # apply filtering server-side
    if filter_by == 'top':
        projects_list = all_projects[:6]
    elif filter_by == 'category' and filter_value:
        projects_list = [
            p for p in all_projects
            if p.get('project_category') == filter_value
        ]
    elif filter_by == 'type' and filter_value:
        projects_list = [
            p for p in all_projects
            if p.get('project_type') == filter_value
        ]
    else:
        projects_list = all_projects

    # build dropdown options
    categories    = sorted({p['project_category'] for p in all_projects if p.get('project_category')})
    project_types = sorted({p['project_type']     for p in all_projects if p.get('project_type')})
    streams = sorted({p['stream']     for p in all_projects if p.get('stream')})

    return render_template(
        'projects.html',
        cv=cv_data,
        projects=projects_list,
        categories=categories,
        streams  = streams, 
        current_filter=filter_by or 'all',
        current_value=filter_value or '',
        category_badges = CATEGORY_BADGES
    )

@app.route('/patents')
def patents():
    return render_template('patents.html', cv=cv_data)

@app.route('/research_works')
def research_works():
    return render_template('research_works.html', cv=cv_data)

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
    return send_from_directory('static/files', 'mokesh_nagpal.pdf', as_attachment=True)

@app.route('/favicon')
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'static', 'logo'),
        'favicon.ico',
        mimetype='favico.icon'
    )





# Chatbot LangChain logic
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda, RunnableParallel, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint, HuggingFaceEndpointEmbeddings
from langchain_community.vectorstores import FAISS
import re

hugg_str = os.environ.get('HUGGINGFACEHUB_API_TOKEN')

llm = HuggingFaceEndpoint(
    repo_id="deepseek-ai/DeepSeek-R1-0528-Qwen3-8B",
    task="text-generation",
    huggingfacehub_api_token=hugg_str
)
model = ChatHuggingFace(llm=llm)

embedding = HuggingFaceEndpointEmbeddings(
    model="Qwen/Qwen3-Embedding-8B",
    task="feature-extraction",
    huggingfacehub_api_token=hugg_str
)

vectorstore = FAISS.load_local(
    "static/db/faiss_index",
    embeddings=embedding,
    allow_dangerous_deserialization=True
)

prompt = PromptTemplate.from_template(
    """You are a helpful AI assistant that analyzes resumes. 
The following text contains a complete resume extracted from documents:

{resume_text}

Based on this resume, answer the user's question as accurately as possible. 
Be specific and structured. If any relevant data is missing, state that clearly.

Question: {question}
Answer:"""
)

def extractor(output):
    text = re.sub(r"<think>.*?</think>", "", output.content, flags=re.DOTALL)
    first_brace = text.find("{")
    raw_json = text[first_brace:] if first_brace != -1 else text
    return type(output)(**{**output.model_dump(), "content": raw_json})

st_parser = StrOutputParser()
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
combiner = RunnableLambda(lambda docs: {"resume_text": " ".join(d.page_content for d in docs)})
pt = RunnablePassthrough()

chain = RunnableParallel(
    {"resume_text": retriever | combiner, "question": pt}
) | prompt | model | extractor | st_parser

@app.route('/chatbot', methods=['GET', 'POST'])
def chatbot():
    if request.method == 'POST':
        user_question = request.form.get('question')
        if not user_question:
            return render_template('chat.html', response="Please enter a question.")
        
        try:
            response = chain.invoke(user_question)
        except Exception as e:
            print(f"Chatbot error: {e}")
            response = "An error occurred while processing your request."

        return render_template('chat.html', response=response, question=user_question, cv=cv_data)
    return render_template('chat.html', cv=cv_data)


if __name__ == '__main__':
    app.run(debug=True)