# Mokesh Nagpal Portfolio Website

This project is a full-stack, responsive portfolio website built with Flask. It dynamically generates content based on a JSON file containing CV data. The website includes sections for About, Experience, Education, Skills, Projects, Patents, and a Contact form. It is built using Bootstrap for responsive design and AOS for smooth animations.

## Project Structure

portfolio/
├── app.py               # Main Flask application file
├── cv_data.json             # CV data in JSON format (parsed from your PDF content)
├── templates/
│  ├── base.html             # Base template with header, footer, and shared components
│  ├── index.html            # Home page combining sections (About, Experience, Education, etc.)
│  ├── about.html
│  ├── experience.html
│  ├── education.html
│  ├── skills.html
│  ├── projects.html
│  ├── patents.html
│  └── contact.html          # Contact page template with a working contact form
├── static/
│  ├── css/
│  │  ├── bootstrap.min.css      # Bootstrap CSS
│  │  └── styles.css           # Custom styles and animations
│  ├── js/
│  │  ├── bootstrap.bundle.min.js  # Bootstrap JS bundle
│  │  └── main.js            # Custom JavaScript for interactive elements
│  ├── images/               # Profile pictures, project images, patent diagrams, etc.
│  └── files/
│     └── cv_data.json          # Copy of the CV file available for download
└── README.md                # Documentation and deployment instructions
