const express = require('express');
const { body, validationResult } = require('express-validator');
const authController = require('../controllers/authController');

const router = express.Router();

router.get('/login', authController.renderLogin);
router.get('/register', authController.renderRegister);
router.post('/register', [
  body('name').notEmpty().withMessage('Name is required'),
  body('email').isEmail().withMessage('Valid email is required'),
  body('password').isLength({ min: 6 }).withMessage('Password must be at least 6 characters')
], (req, res, next) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    req.session.error = errors.array()[0].msg;
    return res.redirect('/auth/register');
  }
  next();
}, authController.register);
router.post('/login', authController.login);
router.get('/logout', authController.logout);

module.exports = router;
