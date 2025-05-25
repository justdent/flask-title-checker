from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_session import Session
from models import db, User, SubmittedTitle, Admin, Prefix, Suffix, DisallowedWord 
from datetime import datetime, timedelta
from excel_checker import ExcelTitleChecker
import os
import json

app = Flask(__name__)  

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './flask_sessions'

# Initialize extensions
Session(app)
db.init_app(app)
migrate = Migrate(app, db)

# Excel database configuration
def get_title_checker():
    EXCEL_PATHS = [
        os.path.join('data', fname)
        for fname in os.listdir('data')
        if fname.endswith('.xls')
    ]
    
    # Fetch prefixes, suffixes, and disallowed words from the database
    prefixes = [prefix.value for prefix in Prefix.query.all()]
    suffixes = [suffix.value for suffix in Suffix.query.all()]
    disallowed_words = [word.word for word in DisallowedWord.query.all()]
    return ExcelTitleChecker(EXCEL_PATHS, prefixes, suffixes, disallowed_words)

DISALLOWED_WORDS = ["hack", "fraud", "scam", "cheat"]

# HOME PAGE
@app.route('/')
@app.route('/start_page')
def start_page():
    return render_template('start_page.html')

# USER SIGNUP
@app.route('/user_signup', methods=['GET', 'POST'])
def user_signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        reconfirm_password = request.form.get('reconfirm_password')

        if password != reconfirm_password:
            flash("Passwords do not match", "danger")
            return render_template('user_signup.html')

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists", "danger")
            return render_template('user_signup.html')
        
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash("Email already exists", "danger")
            return render_template('user_signup.html')

        try:
            new_user = User(username=username, email=email)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            flash("Signup successful! Please log in.", "success")
            return redirect(url_for('user_login'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error: {str(e)}", "danger")
            return render_template('user_signup.html')

    return render_template('user_signup.html')

# USER LOGIN
@app.route('/user_login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        email = request.form.get('email')  
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if not user:
            flash("No user found with that email", "danger")  
            return render_template('user_login.html')  

        if user.is_locked:
            if user.lockout_until and datetime.utcnow() >= user.lockout_until:
                user.unlock_account()
            else:
                flash("Account locked due to too many failed attempts. Try again later.", "danger")
                return render_template('user_login.html')

        if not user.check_password(password):  
            user.failed_attempts += 1
            if user.failed_attempts >= 5:
                user.lock_account()
                flash("Account locked due to too many failed attempts. Try again later.", "danger")
            else:
                db.session.commit()
                flash(f"Incorrect password! {5 - user.failed_attempts} attempts left.", "danger")
            return render_template('user_login.html')

        user.failed_attempts = 0
        user.is_locked = False
        user.lockout_until = None
        db.session.commit()

        session['user_id'] = user.id  
        flash('Login successful!', 'success')  
        return redirect(url_for('title_verification'))  

    return render_template('user_login.html')

# ADMIN SIGNUP
@app.route('/admin_signup', methods=['GET', 'POST'])
def admin_signup():
    if request.method == 'POST':
        email = request.form.get('admin_email')
        username = request.form.get('admin_username')
        password = request.form.get('admin_password')
        reconfirm_password = request.form.get('reconfirm_admin_password')

        if password != reconfirm_password:
            flash("Passwords do not match", "danger")
            return render_template('admin_signup.html')

        existing_admin_by_username = Admin.query.filter_by(username=username).first()
        if existing_admin_by_username:
            flash("Username already exists", "danger")
            return render_template('admin_signup.html')

        existing_admin_by_email = Admin.query.filter_by(email=email).first()
        if existing_admin_by_email:
            flash("Email already exists", "danger")
            return render_template('admin_signup.html')

        new_admin = Admin(email=email, username=username)
        new_admin.set_password(password)
        db.session.add(new_admin)
        db.session.commit()

        flash("Admin account created successfully! Please log in.", "success")
        return redirect(url_for('admin_login'))

    return render_template('admin_signup.html')

# ADMIN LOGIN
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form.get('admin_email')
        password = request.form.get('admin_password')

        admin = Admin.query.filter_by(email=email).first()
        if not admin:
            flash("No admin found with that email", "danger")
            return render_template('admin_login.html')

        if admin.is_locked:
            if admin.lockout_until and datetime.utcnow() >= admin.lockout_until:
                admin.unlock_account()
            else:
                flash("Admin account locked due to too many failed attempts. Try again later.", "danger")
                return render_template('admin_login.html')

        if not admin.check_password(password):
            admin.failed_attempts += 1
            if admin.failed_attempts >= 5:
                admin.lock_account()
                flash("Admin account locked due to too many failed attempts. Try again later.", "danger")
            else:
                db.session.commit()
                flash(f"Incorrect password! {5 - admin.failed_attempts} attempts left.", "danger")
            return render_template('admin_login.html')

        admin.failed_attempts = 0
        admin.is_locked = False
        admin.lockout_until = None
        db.session.commit()

        session['admin_id'] = admin.id
        flash('Admin login successful!', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('admin_login.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'admin_id' not in session:
        flash("Please log in as admin first", "danger")
        return redirect(url_for('admin_login'))

    return render_template('admin_dashboard.html')

# ADMIN MANAGEMENT ROUTES
@app.route('/manage_suffixes', methods=['GET', 'POST'])
def manage_suffixes():
    if 'admin_id' not in session:
        flash("Please log in as admin first", "danger")
        return redirect(url_for('admin_login'))

    if request.method == 'POST':
        action = request.form.get('action')
        value = request.form.get('value')
        type_ = request.form.get('type')

        if value:
            value = value.strip().lower()

        if action == 'add':
            if not value or not type_:
                flash("Value and type are required.", "danger")
                return redirect(url_for('manage_suffixes'))
            
            if type_ == 'prefix':
                existing_prefix = Prefix.query.filter_by(value=value).first()
                if existing_prefix:
                    flash(f"Prefix '{value}' already exists.", "warning")
                else:
                    new_prefix = Prefix(value=value)
                    db.session.add(new_prefix)
                    db.session.commit()
                    flash(f"Prefix '{value}' added.", "success")
            elif type_ == 'suffix':
                existing_suffix = Suffix.query.filter_by(value=value).first()
                if existing_suffix:
                    flash(f"Suffix '{value}' already exists.", "warning")
                else:
                    new_suffix = Suffix(value=value)
                    db.session.add(new_suffix)
                    db.session.commit()
                    flash(f"Suffix '{value}' added.", "success")
            else:
                flash("Invalid type specified.", "danger")

        elif action == 'remove':
            remove_value = request.form.get('remove_id')
            if not remove_value:
                flash("Select a prefix or suffix to remove.", "danger")
                return redirect(url_for('manage_suffixes'))
            remove_value = remove_value.strip().lower()

            prefix = Prefix.query.filter_by(value=remove_value).first()
            if prefix:
                db.session.delete(prefix)
                db.session.commit()
                flash(f"Prefix '{remove_value}' removed.", "success")
            else:
                suffix = Suffix.query.filter_by(value=remove_value).first()
                if suffix:
                    db.session.delete(suffix)
                    db.session.commit()
                    flash(f"Suffix '{remove_value}' removed.", "success")
                else:
                    flash(f"Value '{remove_value}' not found.", "danger")

        else:
            flash("Unknown action.", "danger")

        return redirect(url_for('manage_suffixes'))

    prefixes = Prefix.query.order_by(Prefix.value).all()
    suffixes = Suffix.query.order_by(Suffix.value).all()
    return render_template('manage_suffixes.html', prefixes=prefixes, suffixes=suffixes)


@app.route('/manage_disallowed', methods=['GET', 'POST'])
def manage_disallowed():
    if 'admin_id' not in session:
        flash("Please log in as admin first", "danger")
        return redirect(url_for('admin_login'))

    if request.method == 'POST':
        action = request.form.get('action')
        word = request.form.get('word')

        if word:
            word = word.lower().strip()
        else:
            flash("Word field is required.", "danger")
            return redirect(url_for('manage_disallowed'))

        if action == 'add':
            existing_word = DisallowedWord.query.filter_by(word=word).first()
            if existing_word:
                flash(f"Word '{word}' is already disallowed", "warning")
            else:
                new_word = DisallowedWord(word=word)
                db.session.add(new_word)
                db.session.commit()
                flash(f"Disallowed word '{word}' added successfully", "success")

        elif action == 'remove':
            existing_word = DisallowedWord.query.filter_by(word=word).first()
            if existing_word:
                db.session.delete(existing_word)
                db.session.commit()
                flash(f"Disallowed word '{word}' removed successfully", "success")
            else:
                flash(f"Word '{word}' not found in disallowed list", "warning")

        else:
            flash("Unknown action.", "danger")

        return redirect(url_for('manage_disallowed'))

    disallowed_words = DisallowedWord.query.order_by(DisallowedWord.word).all()
    return render_template('manage_disallowed.html', disallowed_words=disallowed_words)

# USER LOGOUT
@app.route('/user_logout')
def user_logout():
    session.pop('user_id', None)
    flash("You have been logged out.", "success")
    return redirect(url_for('user_login'))

# ADMIN LOGOUT
@app.route('/admin_logout')
def admin_logout():
    session.pop('admin_id', None)
    flash("Admin logged out successfully.", "success")
    return redirect(url_for('admin_login'))

# Existing user routes...

@app.route('/title_verification', methods=['GET', 'POST'])
def title_verification():
    if 'user_id' not in session:
        flash("Please log in first", "danger")
        return redirect(url_for('user_login'))

    if request.method == 'POST':
        title_text = request.form.get('title')
        user_id = session['user_id']

        if not title_text:
            flash("Title cannot be empty", "danger")
            return render_template('title_verification.html')

        new_title = SubmittedTitle(title_text=title_text, user_id=user_id)
        db.session.add(new_title)
        db.session.commit()

        return redirect(url_for('verification_results'))  

    return render_template('title_verification.html')


@app.route('/verification_results')
def verification_results():
    if 'user_id' not in session:
        flash("Please log in first", "danger")
        return redirect(url_for('user_login'))

    title_checker = get_title_checker()
    user_id = session['user_id']
    latest_title = SubmittedTitle.query.filter_by(user_id=user_id).order_by(SubmittedTitle.timestamp.desc()).first()

    if not latest_title:
        flash("No title submitted yet", "warning")
        return redirect(url_for('title_verification'))

    analysis = title_checker.check_similarity(latest_title.title_text)

    latest_title.similarity_score = analysis['similarity_score']
    latest_title.matched_title = analysis['matched_title']
    latest_title.matched_source = analysis['matched_source']
    latest_title.disallowed_words = ','.join(analysis['disallowed_words'])
    latest_title.common_patterns = json.dumps(analysis['common_patterns'])

    similarity_score = analysis['similarity_score']
    num_disallowed = len(analysis['disallowed_words'])

    verification_probability = max(0, 100 - similarity_score - (num_disallowed * 10))
    verification_probability = min(verification_probability, 100)

    latest_title.verification_probability = verification_probability

    db.session.commit()

    return render_template(
        'verification_results.html',
        title=latest_title,
        similarity=similarity_score,
        matched_title=latest_title.matched_title,
        matched_source=latest_title.matched_source,
        disallowed_words_found=analysis['disallowed_words'],
        common_patterns=analysis['common_patterns'],
        verification_probability=verification_probability
    )

@app.route('/detailed_analysis/<int:title_id>')
def detailed_analysis(title_id):
    if 'user_id' not in session:
        flash("Please log in first", "danger")
        return redirect(url_for('user_login'))

    title = SubmittedTitle.query.filter_by(id=title_id, user_id=session['user_id']).first()
    
    if not title:
        flash("Title not found", "danger")
        return redirect(url_for('title_verification'))

    disallowed_words = title.disallowed_words.split(',') if title.disallowed_words else []
    common_patterns = json.loads(title.common_patterns) if title.common_patterns else []

    return render_template('detailed_analysis.html',
        title=title,
        similarity=title.similarity_score,
        matched_title=title.matched_title,
        matched_source=title.matched_source,
        disallowed_words_found=disallowed_words,
        common_patterns=common_patterns,
        verification_probability=title.verification_probability or 0.0
    )

@app.route('/disallowed_words')
def disallowed_words():
    if 'user_id' not in session:
        flash("Please log in first", "danger")
        return redirect(url_for('user_login'))

    # Fetch disallowed words from the database
    disallowed_words_list = [word.word for word in DisallowedWord.query.order_by(DisallowedWord.word).all()]
    
    user_id = session['user_id']
    title = SubmittedTitle.query.filter_by(user_id=user_id)\
        .order_by(SubmittedTitle.timestamp.desc()).first()

    return render_template('disallowed_words.html', disallowed_words=disallowed_words_list, title=title)

@app.route('/common_patterns')
def common_patterns():
    if 'user_id' not in session:
        flash("Please log in first", "danger")
        return redirect(url_for('user_login'))

    title = None
    if 'user_id' in session:
        title = SubmittedTitle.query.filter_by(user_id=session['user_id'])\
            .order_by(SubmittedTitle.timestamp.desc()).first()

    prefixes = [prefix.value for prefix in Prefix.query.order_by(Prefix.value).all()]
    suffixes = [suffix.value for suffix in Suffix.query.order_by(Suffix.value).all()]
    
    return render_template(
        'common_prefixes_and_suffixes.html',
        prefixes=prefixes,
        suffixes=suffixes,
        title=title
    )

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/faq')
def faq():
    return render_template('faq.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

# Run app
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
