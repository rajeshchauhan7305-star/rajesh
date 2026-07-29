const express = require('express');
const session = require('express-session');
const path = require('path');
require('dotenv').config();

const authRoutes = require('./routes/auth');
const studentRoutes = require('./routes/student');
const teacherRoutes = require('./routes/teacher');
const adminRoutes = require('./routes/admin');

const app = express();

app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));
app.use(express.static(path.join(__dirname, 'public')));
app.use('/uploads', express.static(path.join(__dirname, 'uploads')));
app.use(express.urlencoded({ extended: true }));
app.use(express.json());

app.use(session({
  secret: process.env.SESSION_SECRET || 'edusubmit-secret-key',
  resave: false,
  saveUninitialized: false,
  cookie: { maxAge: 1000 * 60 * 60 * 8 }
}));

app.use((req, res, next) => {
  res.locals.user = req.session.user || null;
  res.locals.error = req.session.error || null;
  res.locals.success = req.session.success || null;
  delete req.session.error;
  delete req.session.success;
  next();
});

app.get('/', (req, res) => {
  if (!req.session.user) {
    return res.render('home');
  }
  const redirectPath = req.session.user.role === 'teacher' ? '/teacher/dashboard' : '/student/dashboard';
  res.redirect(redirectPath);
});

app.get('/unauthorized', (req, res) => {
  res.render('unauthorized');
});

app.use('/auth', authRoutes);
app.use('/student', studentRoutes);
app.use('/teacher', teacherRoutes);
app.use('/admin', adminRoutes);

app.use((err, req, res, next) => {
  console.error(err);
  res.status(500).render('error', { message: err.message || 'Something went wrong.' });
});

const port = process.env.PORT || 3000;
app.listen(port, () => {
  console.log(`EduSubmit server is running at http://localhost:${port}`);
});
