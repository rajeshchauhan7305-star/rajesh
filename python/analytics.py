import json
import sys
from collections import Counter


def generate_insights(data):
    assignments = data.get('assignments', [])
    submissions = data.get('submissions', [])
    students = data.get('students', [])

    subject_counts = Counter(a.get('subject_name', 'Unknown') for a in assignments)
    status_counts = Counter(s.get('status', 'Unknown') for s in submissions)
    grade_distribution = Counter()
    for s in submissions:
        marks = s.get('marks_obtained')
        if marks is None:
            continue
        if marks >= 80:
            grade_distribution['A'] += 1
        elif marks >= 60:
            grade_distribution['B'] += 1
        elif marks >= 40:
            grade_distribution['C'] += 1
        else:
            grade_distribution['D'] += 1

    result = {
        'total_assignments': len(assignments),
        'total_students': len(students),
        'total_submissions': len(submissions),
        'subject_counts': dict(subject_counts),
        'status_counts': dict(status_counts),
        'grade_distribution': dict(grade_distribution),
        'completion_rate': round((len(submissions) / len(assignments) * 100), 2) if assignments else 0,
        'recommendation': 'Great pace' if len(submissions) >= len(assignments) // 2 else 'Need more student engagement'
    }
    return result


if __name__ == '__main__':
    try:
        payload = json.loads(sys.argv[1])
    except Exception:
        payload = {}
    print(json.dumps(generate_insights(payload)))
