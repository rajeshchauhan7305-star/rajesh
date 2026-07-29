# EduSubmit

EduSubmit is a modern assignment submission portal for students and teachers built with Node.js, Express, MySQL, Bootstrap, and EJS.

## Features
- Student registration/login
- Teacher login and assignment creation
- PDF-only assignment upload
- Submission tracking and status
- Teacher evaluation and feedback
- Responsive UI

## Requirements
- Node.js 18+
- MySQL 8+

## Installation
1. Clone the project
2. Install dependencies:
   ```bash
   npm install
   ```
3. Create a MySQL database and import the SQL file:
   ```bash
   mysql -u root -p < sql/edusubmit.sql
   ```
4. Update the .env file with your MySQL credentials.
5. Start the app:
   ```bash
   npm run dev
   ```

## Default Credentials
- Teacher: teacher@example.com / password123
- Student: student@example.com / password123

## Folder Structure
- app.js
- routes/
- controllers/
- middleware/
- views/
- public/
- uploads/
- sql/

## Future Scope
- Charts and reports
- Search and filters
- Notifications
- Dark mode toggle
