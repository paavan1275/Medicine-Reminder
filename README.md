# Medicine Reminder App 💊

A comprehensive Flask-based medication reminder application that helps users never miss a dose. The app provides user authentication, medication management, reminder scheduling, and multi-channel notifications.

## Features

- **User Authentication**: Register and login with secure password hashing
- **Medication Management**: Add, view, edit, and delete medications with dosage information
- **Reminder Scheduling**: Set reminders with specific times and frequencies
- **Dose Logging**: Track when medications were taken with timestamps
- **Multi-Channel Notifications**: 
  - Browser notifications
  - Popup alerts with action buttons
  - Audio alerts
  - Toast notifications
- **User Profile**: View account statistics and manage account settings
- **Medication History**: View complete history of logged doses with pagination
- **Data Isolation**: Each user sees only their own medications and reminders
- **Smart Notification Timing**: Checks every 10 seconds with second-level precision

## Tech Stack

- **Backend**: Flask 2.3.3 with Flask-SQLAlchemy
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: Jinja2 templates, vanilla JavaScript
- **Authentication**: werkzeug.security for password hashing (PBKDF2)
- **Notifications**: Browser Notification API, Web Audio API

## Project Structure

```
.
├── app.py                 # Main Flask application with 20+ routes
├── database.py            # SQLAlchemy models (User, Medication, Reminder, Dose)
├── requirements.txt       # Python dependencies
├── .gitignore            # Git ignore file
├── templates/            # HTML templates
│   ├── base.html        # Master template with navigation
│   ├── index.html       # Home/dashboard page
│   ├── login.html       # Login page
│   ├── register.html    # Registration with password validation
│   ├── profile.html     # User profile with account management
│   ├── add_medication.html
│   ├── view_medications.html
│   ├── medication_detail.html
│   ├── add_reminder.html
│   ├── medication_history.html
│   └── error.html
├── static/
│   ├── css/
│   │   └── style.css    # Styling with notification popups and animations
│   └── js/
│       └── script.js    # Client-side notification logic (10s check interval)
└── instance/            # Database instance folder
    └── medication_reminder.db
```

## Installation

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/paavan1275/Medicine-Reminder.git
   cd Medicine-Reminder
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the application**
   - Open your browser and navigate to `http://localhost:5000`

## Usage

### Registration and Login
- Create a new account with username, email, and password
- Login with your username or email
- After registration, you'll be automatically logged in and taken to the home page

### Managing Medications
- Click "Add Medication" to register a new medication
- Specify medication name, dosage, and description
- View all your medications on the "View Medications" page
- Edit or delete medications as needed

### Setting Reminders
- Click "Set Reminder" on any medication to schedule reminders
- Choose reminder time (HH:MM format) and frequency (daily, weekly, etc.)
- Set which days of the week the reminder should trigger

### Logging Doses
- Click "Log Dose" to record when you took a medication
- Timestamps are automatically recorded
- Add optional notes about the dose

### Notifications
- Reminders are checked every 10 seconds
- When a reminder time arrives, you'll receive:
  - A popup notification with "Mark as Taken" button
  - A browser notification (if permitted)
  - An audio alert

### Profile Management
- Click your username in the top-right corner to access your profile
- View account statistics (medications count, reminders, total doses)
- Update your email address
- Change your password with verification
- Delete your account if needed

## API Endpoints

- `GET /` - Home page (login required)
- `POST /register` - User registration
- `POST /login` - User login
- `GET /logout` - User logout
- `GET /profile` - User profile page
- `POST /profile/update` - Update email
- `POST /profile/change-password` - Change password
- `POST /profile/delete` - Delete account
- `GET /medications` - List all medications
- `POST /medication/add` - Add new medication
- `GET /medication/<id>` - View medication details
- `POST /medication/<id>/delete` - Delete medication
- `GET /reminder/add/<med_id>` - Add reminder form
- `POST /reminder/add/<med_id>` - Save reminder
- `POST /dose/log/<med_id>` - Log a dose
- `GET /api/upcoming-reminders` - Get upcoming reminders (API)
- `POST /api/dose/<med_id>` - Log dose via API
- `GET /history` - Medication history with pagination

## Features in Detail

### Smart Notifications
- Checks for reminders every 10 seconds
- Second-level precision timing (within the minute)
- Prevents duplicate notifications with sessionStorage deduplication
- Supports multiple notification channels simultaneously

### Security
- Password hashing using PBKDF2 (werkzeug.security)
- Session-based authentication
- User data isolation (users only see their own data)
- Protected routes with @login_required decorator
- No sensitive data stored in plain text

### User Experience
- Auto-login after registration
- Responsive design with gradient backgrounds
- Smooth animations and transitions
- Toast notifications for user feedback
- Pagination for medication history
- Clean and intuitive navigation

## Future Enhancements

- Email notifications
- SMS notifications (Twilio integration)
- Database migrations (Alembic)
- Mobile app version
- Multi-user family accounts
- Medication refill reminders
- Doctor appointment tracking
- Export medication history to PDF

## Database Models

### User
- id, username, email, password_hash, created_at
- Relationships: medications, reminders, doses

### Medication
- id, user_id, name, dosage, description, created_at
- Relationships: reminders, doses

### Reminder
- id, medication_id, reminder_time, frequency, days_of_week, is_active, created_at

### Dose
- id, medication_id, taken_at, notes

## License

MIT License

## Author

paavan1275

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues, questions, or suggestions, please open an issue on the GitHub repository.

### Tables:
- **medications**: Stores medication information
- **reminders**: Stores reminder schedules
- **doses**: Tracks when medications were taken

## Future Enhancements

- Email/SMS notifications
- Mobile app support
- Multi-user support
- Export reports
- Medication interactions checker
- Refill reminders

## License

MIT License

## Support

For issues or suggestions, please contact the development team.
