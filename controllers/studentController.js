const db = require('../config/database');

exports.dashboard = async (req, res) => {
  try {
    const studentId = req.session.user.user_id;
    const [assignments] = await db.query('SELECT * FROM assignments ORDER BY due_date ASC');
    const [submissions] = await db.query('SELECT * FROM submissions WHERE student_id = ?', [studentId]);

    const totalAssignments = assignments.length;
    const submittedAssignments = submissions.filter((s) => s.status === 'Graded' || s.status === 'Pending').length;
    const pendingAssignments = assignments.length - submittedAssignments;
    const gradedAssignments = submissions.filter((s) => s.status === 'Graded').length;

    res.render('student/dashboard', {
      totalAssignments,
      submittedAssignments,
      pendingAssignments,
      gradedAssignments,
      assignments,
      submissions
    });
  } catch (error) {
    console.error(error);
    res.status(500).render('error', { message: 'Failed to load dashboard.' });
  }
};

exports.assignments = async (req, res) => {
  try {
    const [assignments] = await db.query('SELECT * FROM assignments ORDER BY due_date ASC');
    const [submissions] = await db.query('SELECT * FROM submissions WHERE student_id = ?', [req.session.user.user_id]);
    const submissionMap = new Map(submissions.map((s) => [s.assignment_id, s]));

    res.render('student/assignments', { assignments, submissionMap });
  } catch (error) {
    console.error(error);
    res.status(500).render('error', { message: 'Failed to load assignments.' });
  }
};

exports.viewAssignment = async (req, res) => {
  try {
    const assignmentId = req.params.id;
    const [assignments] = await db.query('SELECT * FROM assignments WHERE assignment_id = ?', [assignmentId]);
    const [submissions] = await db.query('SELECT * FROM submissions WHERE assignment_id = ? AND student_id = ?', [assignmentId, req.session.user.user_id]);

    res.render('student/assignment-detail', { assignment: assignments[0], submission: submissions[0] || null });
  } catch (error) {
    console.error(error);
    res.status(500).render('error', { message: 'Failed to load assignment.' });
  }
};

exports.submitAssignment = async (req, res) => {
  try {
    const assignmentId = req.params.id;
    const filePath = req.file ? `/uploads/${req.file.filename}` : null;

    if (!filePath) {
      req.session.error = 'Please upload a PDF file.';
      return res.redirect(`/student/assignment/${assignmentId}`);
    }

    const [existing] = await db.query('SELECT * FROM submissions WHERE assignment_id = ? AND student_id = ?', [assignmentId, req.session.user.user_id]);
    if (existing.length > 0) {
      req.session.error = 'You have already submitted this assignment.';
      return res.redirect(`/student/assignment/${assignmentId}`);
    }

    const now = new Date();
    const dueDate = new Date((await db.query('SELECT due_date FROM assignments WHERE assignment_id = ?', [assignmentId]))[0][0].due_date);
    const status = now > dueDate ? 'Late' : 'Pending';

    await db.query('INSERT INTO submissions (assignment_id, student_id, file_path, submission_date, status) VALUES (?, ?, ?, ?, ?)', [assignmentId, req.session.user.user_id, filePath, now.toISOString().slice(0, 19).replace('T', ' '), status]);

    req.session.success = 'Assignment submitted successfully.';
    res.redirect('/student/assignments');
  } catch (error) {
    console.error(error);
    req.session.error = error.message || 'Submission failed.';
    res.redirect('/student/assignments');
  }
};

exports.marks = async (req, res) => {
  try {
    const [rows] = await db.query('SELECT s.*, a.title, a.subject_name FROM submissions s JOIN assignments a ON s.assignment_id = a.assignment_id WHERE s.student_id = ? ORDER BY s.submission_date DESC', [req.session.user.user_id]);
    res.render('student/marks', { submissions: rows });
  } catch (error) {
    console.error(error);
    res.status(500).render('error', { message: 'Failed to load marks.' });
  }
};
