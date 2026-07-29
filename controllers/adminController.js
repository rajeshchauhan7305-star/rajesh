const db = require('../config/database');

exports.dashboard = async (req, res) => {
  try {
    const [users] = await db.query('SELECT * FROM users');
    const [assignments] = await db.query('SELECT * FROM assignments');
    const [submissions] = await db.query('SELECT * FROM submissions');

    res.render('admin/dashboard', {
      users: users.length,
      assignments: assignments.length,
      submissions: submissions.length,
      usersList: users
    });
  } catch (error) {
    console.error(error);
    res.status(500).render('error', { message: 'Failed to load admin dashboard.' });
  }
};

exports.users = async (req, res) => {
  try {
    const [rows] = await db.query('SELECT * FROM users ORDER BY created_at DESC');
    res.render('admin/users', { users: rows });
  } catch (error) {
    console.error(error);
    res.status(500).render('error', { message: 'Failed to load users.' });
  }
};

exports.createUser = async (req, res) => {
  try {
    const { name, email, password, role } = req.body;
    const bcrypt = require('bcrypt');
    const hashedPassword = await bcrypt.hash(password, 10);

    await db.query('INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)', [name, email, hashedPassword, role]);
    req.session.success = 'User created successfully.';
    res.redirect('/admin/users');
  } catch (error) {
    console.error(error);
    req.session.error = 'Failed to create user.';
    res.redirect('/admin/users');
  }
};

exports.updateUser = async (req, res) => {
  try {
    const userId = req.params.id;
    const { name, email, role } = req.body;
    await db.query('UPDATE users SET name = ?, email = ?, role = ? WHERE user_id = ?', [name, email, role, userId]);
    req.session.success = 'User updated successfully.';
    res.redirect('/admin/users');
  } catch (error) {
    console.error(error);
    req.session.error = 'Failed to update user.';
    res.redirect('/admin/users');
  }
};

exports.deleteUser = async (req, res) => {
  try {
    const userId = req.params.id;
    await db.query('DELETE FROM users WHERE user_id = ?', [userId]);
    req.session.success = 'User deleted successfully.';
    res.redirect('/admin/users');
  } catch (error) {
    console.error(error);
    req.session.error = 'Failed to delete user.';
    res.redirect('/admin/users');
  }
};
