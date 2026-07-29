const express = require('express');
const adminController = require('../controllers/adminController');
const { requireAuth, requireRole } = require('../middleware/authMiddleware');

const router = express.Router();

router.get('/dashboard', requireAuth, requireRole('admin'), adminController.dashboard);
router.get('/users', requireAuth, requireRole('admin'), adminController.users);
router.post('/users/create', requireAuth, requireRole('admin'), adminController.createUser);
router.post('/users/update/:id', requireAuth, requireRole('admin'), adminController.updateUser);
router.post('/users/delete/:id', requireAuth, requireRole('admin'), adminController.deleteUser);

module.exports = router;
