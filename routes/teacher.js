const express = require('express');
const teacherController = require('../controllers/teacherController');
const { requireAuth, requireRole } = require('../middleware/authMiddleware');

const router = express.Router();

router.get('/dashboard', requireAuth, requireRole('teacher'), teacherController.dashboard);
router.get('/assignments', requireAuth, requireRole('teacher'), teacherController.assignments);
router.post('/assignments/create', requireAuth, requireRole('teacher'), teacherController.createAssignment);
router.post('/assignments/edit/:id', requireAuth, requireRole('teacher'), teacherController.editAssignment);
router.post('/assignments/delete/:id', requireAuth, requireRole('teacher'), teacherController.deleteAssignment);
router.get('/submissions', requireAuth, requireRole('teacher'), teacherController.submissions);
router.post('/submissions/evaluate/:id', requireAuth, requireRole('teacher'), teacherController.evaluateSubmission);

module.exports = router;
