const bcrypt = require('bcrypt');
const db = require('../config/database');

exports.renderLogin = (req, res) => {
  const roleHint = req.query.role;
  res.render('login', { roleHint });
};

exports.renderRegister = (req, res) => {
  res.render('register');
};

exports.register = async (req, res) => {
  const { name, email, password, role } = req.body;

  try {
    const [existing] = await db.query('SELECT * FROM users WHERE email = ?', [email]);
    if (existing.length > 0) {
      req.session.error = 'Email already registered.';
      return res.redirect('/auth/register');
    }

    const hashedPassword = await bcrypt.hash(password, 10);
    await db.query('INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)', [name, email, hashedPassword, role || 'student']);

    req.session.success = 'Registration successful. Please login.';
    res.redirect('/auth/login');
  } catch (error) {
    console.error(error);

    if (error.code === 'ECONNREFUSED') {
      req.session.error = 'Database connection failed. Start MySQL and verify your DB credentials.';
      return res.redirect('/auth/register');
    }

    req.session.error = error.message || 'Registration failed.';
    return res.redirect('/auth/register');
  }
};

exports.login = async (req, res) => {
  const { email, password } = req.body;

  try {
    const [rows] = await db.query('SELECT * FROM users WHERE email = ?', [email]);
    if (rows.length === 0) {
      req.session.error = 'Invalid email or password.';
      return res.redirect('/auth/login');
    }

    const user = rows[0];
    const isValidPassword = await bcrypt.compare(password, user.password);
    if (!isValidPassword) {
      req.session.error = 'Invalid email or password.';
      return res.redirect('/auth/login');
    }

    req.session.user = {
      user_id: user.user_id,
      name: user.name,
      email: user.email,
      role: user.role
    };

    if (user.role === 'admin') {
      return res.redirect('/admin/dashboard');
    }
    if (user.role === 'teacher') {
      return res.redirect('/teacher/dashboard');
    }
    res.redirect('/student/dashboard');
  } catch (error) {
    console.error(error);
    req.session.error = error.code === 'ECONNREFUSED'
      ? 'Database connection failed. Please start MySQL and try again.'
      : 'Login failed. Please try again.';
    return res.redirect('/auth/login');
  }
};

exports.logout = (req, res) => {
  req.session.destroy(() => {
    res.redirect('/auth/login');
  });
};
