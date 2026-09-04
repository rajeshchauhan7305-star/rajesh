# EduSubmit

EduSubmit is a modern assignment submission portal for students and teachers built with Python, Flask, MySQL, Bootstrap, and Jinja templates.

## Features
- Student registration/login
- Teacher login and assignment creation
- PDF-only assignment upload
- Submission tracking and status
- Teacher evaluation and feedback
- Responsive UI

## Requirements
- Python 3.10+
- MySQL 8+

## Installation
1. Clone the project
2. Install Python dependencies:
   ```bash
   pip install -r python/requirements.txt
   ```
3. Create a MySQL database and import the SQL file:
   ```bash
   mysql -u root -p < sql/edusubmit.sql
   ```
4. Update the .env file with your MySQL credentials.
   - If MySQL is running locally, set `DB_HOST=127.0.0.1` and `DB_PORT=3306`.
   - If you see socket errors, try `DB_HOST=127.0.0.1` instead of `localhost`.
5. Start the Python backend:
   ```bash
   python3 run.py
   ```

The application is available at `http://localhost:3000`. `npm start` also runs the Python backend for environments that use the existing npm start command.

## Default Credentials
- Admin: admin@example.com / password123
- Teacher: teacher@example.com / password123
- Student: student@example.com / password123

## Folder Structure
- app.py
- run.py
- templates/
- public/
- uploads/
- sql/

## Future Scope
- Charts and reports
- Search and filters
- Notifications
- Dark mode toggle
