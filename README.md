## ﻿ADL Title Verification App

A Flask-based web application to verify academic document titles against an Excel database. It features user and admin login, disallowed word filtering, Levenshtein and phonetic similarity checks, and admin tools for managing verification rules.

## Live Demo
🔗 Live App on Render: https://flask-title-checker.onrender.com

## Features
- User and Admin authentication system
- Excel-based title checking
- Similarity checking using Levenshtein ratio
- Disallowed word detection
- Pattern rule handling (prefixes, suffixes, common terms)
- Admin dashboard to manage rules dynamically
- Title submission history saved in the database
- Flask-Session for secure session management

## Project Structure

```
adl-app/
├── app.py
├── templates/
│ ├── start_page.html
│ ├── login.html
│ ├── dashboard.html
│ └── ...
├── static/
├── models.py
├── excel_checker.py
├── requirements.txt
└── README.md
```


## Installation

1. Clone the repository
git clone https://github.com/justdent/flask-title-checker
cd adl-app

2. Create and activate a virtual environment

### Windows
python -m venv venv
venv\Scripts\activate

### macOS/Linux
python3 -m venv venv
source venv/bin/activate

3. Install dependencies
pip install -r requirements.txt

4. Set up the database
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

5. Run the app
flask run

## Environment Variables:
You may need a .env file or environment variables configured:

FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key
SESSION_TYPE=filesystem

## Deployment:
This app can be deployed on platforms like Render, Heroku, or any cloud VM with Python support.

For Render:
- Build: pip install -r requirements.txt
- Start: flask run --host=0.0.0.0 --port=10000
- Set environment variables (SECRET_KEY, FLASK_ENV, etc.) in the Render dashboard

## Contributing:
Pull requests are welcome! For major changes, please open an issue first to discuss your ideas.

## License:
This project is licensed under the MIT License.

## Credits:
Developed by Tanuj, Siddharth, Hariharan

## Using:
Flask, SQLAlchemy, Levenshtein, Fuzzy, OpenPyXL
