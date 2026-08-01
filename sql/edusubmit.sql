CREATE DATABASE IF NOT EXISTS edusubmit;
USE edusubmit;

CREATE TABLE users (
  user_id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  email VARCHAR(100) NOT NULL UNIQUE,
  password VARCHAR(255) NOT NULL,
  role ENUM('student','teacher','admin') NOT NULL DEFAULT 'student',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE assignments (
  assignment_id INT AUTO_INCREMENT PRIMARY KEY,
  subject_name VARCHAR(100) NOT NULL,
  title VARCHAR(150) NOT NULL,
  description TEXT NOT NULL,
  due_date DATE NOT NULL,
  max_marks INT NOT NULL,
  created_by INT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (created_by) REFERENCES users(user_id)
);

CREATE TABLE submissions (
  submission_id INT AUTO_INCREMENT PRIMARY KEY,
  assignment_id INT NOT NULL,
  student_id INT NOT NULL,
  file_path VARCHAR(255) NOT NULL,
  submission_date DATETIME NOT NULL,
  marks_obtained INT DEFAULT NULL,
  teacher_feedback TEXT DEFAULT NULL,
  status VARCHAR(20) NOT NULL DEFAULT 'Pending',
  FOREIGN KEY (assignment_id) REFERENCES assignments(assignment_id),
  FOREIGN KEY (student_id) REFERENCES users(user_id)
);

INSERT INTO users (name, email, password, role) VALUES
('Admin One', 'admin@example.com', '$2b$10$DLXxhG2h6o6O3jQyngaQqeMjIULnxixfUMiV4lIgyKrwNToWpZCG6', 'admin'),
('Teacher One', 'teacher@example.com', '$2b$10$gQomKKaVq.0eddkdZul2puJJ2nt60i4WliH1Iabmo.zr2kVmDthX.', 'teacher'),
('Student One', 'student@example.com', '$2b$10$BGDqgLJNH.woGHGBL497D.yccu07Ify.uvgbnteu7lt6VTqTudtmS', 'student');

INSERT INTO assignments (subject_name, title, description, due_date, max_marks, created_by) VALUES
('Computer Science', 'DBMS Practical', 'Submit a practical assignment on SQL joins.', '2026-08-01', 50, 1),
('Mathematics', 'Calculus Worksheet', 'Solve the given calculus problems.', '2026-08-10', 40, 1);
