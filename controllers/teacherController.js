const { execFile } = require('child_process');
const path = require('path');
const db = require('../config/database');

function runPythonAnalytics(payload) {
  return new Promise((resolve, reject) => {
    const scriptPath = path.join(__dirname, '../python/analytics.py');
    execFile('python3', [scriptPath, JSON.stringify(payload)], (error, stdout, stderr) => {
      if (error) {
        reject(error);
        return;
      }
      try {
        resolve(JSON.parse(stdout));
      } catch (parseError) {
        reject(parseError);
      }
    });
  });
}

exports.dashboard = async (req, res) => {
  try {
    const [students] = await db.query('SELECT * FROM users WHERE role = "student"');
    const [assignments] = await db.query('SELECT * FROM assignments');
    const [submissions] = await db.query('SELECT * FROM submissions');
    const pendingReviews = submissions.filter((s) => s.status === 'Pending').length;
    const lateSubmissions = submissions.filter((s) => s.status === 'Late').length;

    const analytics = await runPythonAnalytics({
      assignments,
      submissions,
      students
    });

    res.render('teacher/dashboard', {
      students: students.length,
      assignments: assignments.length,
      pendingReviews,
      lateSubmissions,
      submissions: submissions.slice(0, 5),
      analytics
    });
  } catch (error) {
    console.error(error);
    res.status(500).render('error', { message: 'Failed to load dashboard.' });
  }
};

exports.assignments = async (req, res) => {
  try {
    const [rows] = await db.query('SELECT * FROM assignments ORDER BY created_at DESC');
    res.render('teacher/assignments', { assignments: rows });
  } catch (error) {
    console.error(error);
    res.status(500).render('error', { message: 'Failed to load assignments.' });
  }
};

exports.createAssignment = async (req, res) => {
  try {
    const { subject_name, title, description, max_marks, due_date } = req.body;
    await db.query('INSERT INTO assignments (subject_name, title, description, max_marks, due_date, created_by, created_at) VALUES (?, ?, ?, ?, ?, ?, NOW())', [subject_name, title, description, max_marks, due_date, req.session.user.user_id]);
    req.session.success = 'Assignment created successfully.';
    res.redirect('/teacher/assignments');
  } catch (error) {
    console.error(error);
    req.session.error = 'Failed to create assignment.';
    res.redirect('/teacher/assignments');
  }
};

exports.editAssignment = async (req, res) => {
  try {
    const assignmentId = req.params.id;
    const { subject_name, title, description, max_marks, due_date } = req.body;
    await db.query('UPDATE assignments SET subject_name = ?, title = ?, description = ?, max_marks = ?, due_date = ? WHERE assignment_id = ?', [subject_name, title, description, max_marks, due_date, assignmentId]);
    req.session.success = 'Assignment updated successfully.';
    res.redirect('/teacher/assignments');
  } catch (error) {
    console.error(error);
    req.session.error = 'Failed to update assignment.';
    res.redirect('/teacher/assignments');
  }
};

exports.deleteAssignment = async (req, res) => {
  try {
    const assignmentId = req.params.id;
    await db.query('DELETE FROM assignments WHERE assignment_id = ?', [assignmentId]);
    req.session.success = 'Assignment deleted successfully.';
    res.redirect('/teacher/assignments');
  } catch (error) {
    console.error(error);
    req.session.error = 'Failed to delete assignment.';
    res.redirect('/teacher/assignments');
  }
};

exports.submissions = async (req, res) => {
  try {
    const [rows] = await db.query('SELECT s.*, a.title, u.name FROM submissions s JOIN assignments a ON s.assignment_id = a.assignment_id JOIN users u ON s.student_id = u.user_id ORDER BY s.submission_date DESC');
    res.render('teacher/submissions', { submissions: rows });
  } catch (error) {
    console.error(error);
    res.status(500).render('error', { message: 'Failed to load submissions.' });
  }
};

exports.evaluateSubmission = async (req, res) => {
  try {
    const submissionId = req.params.id;
    const { marks_obtained, teacher_feedback } = req.body;
    await db.query('UPDATE submissions SET marks_obtained = ?, teacher_feedback = ?, status = ? WHERE submission_id = ?', [marks_obtained, teacher_feedback, 'Graded', submissionId]);
    req.session.success = 'Submission evaluated successfully.';
    res.redirect('/teacher/submissions');
  } catch (error) {
    console.error(error);
    req.session.error = 'Failed to evaluate submission.';
    res.redirect('/teacher/submissions');
  }
};
