const express = require('express');
const studentController = require('../controllers/studentController');
const { requireAuth, requireRole } = require('../middleware/authMiddleware');
const upload = require('../middleware/uploadMiddleware');

const router = express.Router();

router.get('/dashboard', requireAuth, requireRole('student'), studentController.dashboard);
router.get('/assignments', requireAuth, requireRole('student'), studentController.assignments);
router.get('/assignment/:id', requireAuth, requireRole('student'), studentController.viewAssignment);
router.post('/assignment/:id/submit', requireAuth, requireRole('student'), upload.single('pdfFile'), studentController.submitAssignment);
router.get('/marks', requireAuth, requireRole('student'), studentController.marks);

module.exports = router;
