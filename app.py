from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from database import db, init_db, User, Medication, Reminder, Dose
from datetime import datetime, timedelta
from functools import wraps
import os

app = Flask(__name__)

# Configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance', 'medication_reminder.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'medication-reminder-secret-key-12345'

# Create instance folder if it doesn't exist
os.makedirs(os.path.join(basedir, 'instance'), exist_ok=True)

# Initialize database
db.init_app(app)
init_db(app)


def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in first!', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Register a new user"""
    if 'user_id' in session:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if not username or not email or not password:
            flash('All fields are required!', 'error')
            return redirect(url_for('register'))
        
        if len(username) < 3:
            flash('Username must be at least 3 characters!', 'error')
            return redirect(url_for('register'))
        
        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return redirect(url_for('register'))
        
        if len(password) < 6:
            flash('Password must be at least 6 characters!', 'error')
            return redirect(url_for('register'))
        
        # Check if user exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists!', 'error')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered!', 'error')
            return redirect(url_for('register'))
        
        # Create new user
        user = User(username=username, email=email)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # Auto-login the new user
        session['user_id'] = user.id
        session['username'] = user.username
        
        flash(f'Welcome {username}! Your account has been created successfully.', 'success')
        return redirect(url_for('index'))
    
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login user"""
    if 'user_id' in session:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username_or_email = request.form.get('username')
        password = request.form.get('password')
        
        if not username_or_email or not password:
            flash('Username and password are required!', 'error')
            return redirect(url_for('login'))
        
        # Find user by username or email
        user = User.query.filter(
            (User.username == username_or_email) | (User.email == username_or_email)
        ).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username/email or password!', 'error')
            return redirect(url_for('login'))
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    flash('You have been logged out!', 'success')
    return redirect(url_for('login'))


@app.route('/profile')
@login_required
def profile():
    """View user profile"""
    user_id = session.get('user_id')
    current_user = User.query.get(user_id)
    
    # Get user statistics
    medications = Medication.query.filter_by(user_id=user_id).all()
    medications_count = len(medications)
    
    reminders_count = 0
    for med in medications:
        reminders_count += len(med.reminders)
    
    # Get doses today
    today = datetime.now().date()
    doses_today = 0
    total_doses = 0
    
    for med in medications:
        for dose in med.doses:
            total_doses += 1
            if dose.taken_at.date() == today:
                doses_today += 1
    
    return render_template('profile.html',
                         current_user=current_user,
                         medications_count=medications_count,
                         reminders_count=reminders_count,
                         doses_today=doses_today,
                         total_doses=total_doses)


@app.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    """Update user profile"""
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    
    email = request.form.get('email')
    
    if not email:
        flash('Email is required!', 'error')
        return redirect(url_for('profile'))
    
    # Check if email is already used by another user
    existing_user = User.query.filter_by(email=email).first()
    if existing_user and existing_user.id != user_id:
        flash('Email already registered by another account!', 'error')
        return redirect(url_for('profile'))
    
    user.email = email
    db.session.commit()
    
    flash('Profile updated successfully!', 'success')
    return redirect(url_for('profile'))


@app.route('/profile/change-password', methods=['POST'])
@login_required
def change_password():
    """Change user password"""
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    if not current_password or not new_password or not confirm_password:
        flash('All fields are required!', 'error')
        return redirect(url_for('profile'))
    
    if not user.check_password(current_password):
        flash('Current password is incorrect!', 'error')
        return redirect(url_for('profile'))
    
    if new_password != confirm_password:
        flash('New passwords do not match!', 'error')
        return redirect(url_for('profile'))
    
    if len(new_password) < 6:
        flash('Password must be at least 6 characters!', 'error')
        return redirect(url_for('profile'))
    
    user.set_password(new_password)
    db.session.commit()
    
    flash('Password changed successfully!', 'success')
    return redirect(url_for('profile'))


@app.route('/profile/delete', methods=['POST'])
@login_required
def delete_account():
    """Delete user account and all data"""
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    
    # Delete all user data
    db.session.delete(user)
    db.session.commit()
    
    # Clear session
    session.clear()
    
    flash('Your account has been deleted permanently.', 'success')
    return redirect(url_for('login'))


@app.route('/')
@login_required
def index():
    """Dashboard - show upcoming reminders and quick actions"""
    user_id = session.get('user_id')
    medications = Medication.query.filter_by(user_id=user_id).all()
    
    # Get upcoming reminders
    today = datetime.now().date()
    upcoming_reminders = []
    
    for med in medications:
        for reminder in med.reminders:
            if reminder.is_active:
                upcoming_reminders.append({
                    'medication': med,
                    'reminder': reminder,
                    'time': reminder.reminder_time
                })
    
    # Sort by time
    upcoming_reminders.sort(key=lambda x: x['time'])
    
    # Get recent doses
    recent_doses = Dose.query.order_by(Dose.taken_at.desc()).limit(10).all()
    
    return render_template('index.html', 
                         medications=medications,
                         upcoming_reminders=upcoming_reminders,
                         recent_doses=recent_doses)


@app.route('/medication/add', methods=['GET', 'POST'])
@login_required
def add_medication():
    """Add a new medication"""
    user_id = session.get('user_id')
    if request.method == 'POST':
        name = request.form.get('name')
        dosage = request.form.get('dosage')
        description = request.form.get('description')
        
        if not name or not dosage:
            flash('Medication name and dosage are required!', 'error')
            return redirect(url_for('add_medication'))
        
        medication = Medication(
            user_id=user_id,
            name=name,
            dosage=dosage,
            description=description
        )
        
        db.session.add(medication)
        db.session.commit()
        
        flash(f'Medication "{name}" added successfully!', 'success')
        return redirect(url_for('add_reminder', med_id=medication.id))
    
    return render_template('add_medication.html')


@app.route('/reminder/add/<int:med_id>', methods=['GET', 'POST'])
@login_required
def add_reminder(med_id):
    """Add a reminder for a medication"""
    user_id = session.get('user_id')
    medication = Medication.query.filter_by(id=med_id, user_id=user_id).first_or_404()
    
    if request.method == 'POST':
        reminder_time = request.form.get('reminder_time')
        frequency = request.form.get('frequency')
        days_of_week = request.form.get('days_of_week', '')
        
        if not reminder_time or not frequency:
            flash('Reminder time and frequency are required!', 'error')
            return redirect(url_for('add_reminder', med_id=med_id))
        
        reminder = Reminder(
            medication_id=med_id,
            reminder_time=reminder_time,
            frequency=frequency,
            days_of_week=days_of_week
        )
        
        db.session.add(reminder)
        db.session.commit()
        
        flash(f'Reminder set for {reminder_time}!', 'success')
        return redirect(url_for('index'))
    
    return render_template('add_reminder.html', medication=medication)


@app.route('/medications')
@login_required
def view_medications():
    """View all medications"""
    user_id = session.get('user_id')
    medications = Medication.query.filter_by(user_id=user_id).all()
    return render_template('view_medications.html', medications=medications)


@app.route('/medication/<int:med_id>')
@login_required
def view_medication(med_id):
    """View details of a specific medication"""
    user_id = session.get('user_id')
    medication = Medication.query.filter_by(id=med_id, user_id=user_id).first_or_404()
    doses = Dose.query.filter_by(medication_id=med_id).order_by(Dose.taken_at.desc()).all()
    
    return render_template('medication_detail.html', medication=medication, doses=doses)


@app.route('/medication/<int:med_id>/delete', methods=['POST'])
@login_required
def delete_medication(med_id):
    """Delete a medication and all associated data"""
    user_id = session.get('user_id')
    medication = Medication.query.filter_by(id=med_id, user_id=user_id).first_or_404()
    name = medication.name
    
    db.session.delete(medication)
    db.session.commit()
    
    flash(f'Medication "{name}" deleted!', 'success')
    return redirect(url_for('view_medications'))


@app.route('/dose/log/<int:med_id>', methods=['POST'])
@login_required
def log_dose(med_id):
    """Log a dose for a medication"""
    user_id = session.get('user_id')
    medication = Medication.query.filter_by(id=med_id, user_id=user_id).first_or_404()
    notes = request.form.get('notes', '')
    
    dose = Dose(
        medication_id=med_id,
        notes=notes
    )
    
    db.session.add(dose)
    db.session.commit()
    
    flash(f'Dose logged for {medication.name}!', 'success')
    return redirect(url_for('index'))


@app.route('/api/upcoming-reminders')
@login_required
def api_upcoming_reminders():
    """API endpoint to get upcoming reminders (for notifications)"""
    user_id = session.get('user_id')
    medications = Medication.query.filter_by(user_id=user_id).all()
    current_time = datetime.now().strftime('%H:%M')
    
    reminders = []
    for med in medications:
        for reminder in med.reminders:
            if reminder.is_active:
                reminders.append({
                    'id': reminder.id,
                    'medication_name': med.name,
                    'dosage': med.dosage,
                    'time': reminder.reminder_time,
                    'medication_id': med.id
                })
    
    return jsonify(reminders)


@app.route('/api/dose/<int:med_id>', methods=['POST'])
@login_required
def api_log_dose(med_id):
    """API endpoint to log a dose (for notifications)"""
    user_id = session.get('user_id')
    medication = Medication.query.filter_by(id=med_id, user_id=user_id).first_or_404()
    
    dose = Dose(medication_id=med_id)
    db.session.add(dose)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'Dose logged for {medication.name}'
    })


@app.route('/history')
@login_required
def medication_history():
    """View medication history"""
    user_id = session.get('user_id')
    page = request.args.get('page', 1, type=int)
    user_medications = Medication.query.filter_by(user_id=user_id).all()
    med_ids = [med.id for med in user_medications]
    
    doses = Dose.query.filter(Dose.medication_id.in_(med_ids)).order_by(Dose.taken_at.desc()).paginate(page=page, per_page=20)
    
    return render_template('medication_history.html', doses=doses)


@app.template_filter('time_ago')
def time_ago(dt):
    """Filter to display time in 'X minutes ago' format"""
    now = datetime.utcnow()
    diff = now - dt
    
    if diff.seconds < 60:
        return f'{diff.seconds}s ago'
    elif diff.seconds < 3600:
        return f'{diff.seconds // 60}m ago'
    elif diff.seconds < 86400:
        return f'{diff.seconds // 3600}h ago'
    else:
        return f'{diff.days}d ago'


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return render_template('error.html', message='Page not found'), 404


@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    return render_template('error.html', message='Server error'), 500


if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=5000)
