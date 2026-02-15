from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import fitz  # PyMuPDF
import os
import re
import json
import uuid
import unicodedata
from datetime import datetime

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Database config: use DATABASE_URL (PostgreSQL on Railway) or fallback to SQLite
database_url = os.environ.get('DATABASE_URL', 'sqlite:///withdrawals.db')
# Railway PostgreSQL uses postgres:// but SQLAlchemy needs postgresql://
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Admin password (set via env var in production)
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')

# Fixed college name
COLLEGE_NAME = 'كلية الحاسبات وتقنية المعلومات'

db = SQLAlchemy(app)

ALLOWED_EXTENSIONS = {'pdf', 'faces'}


# ============ Database Models ============

class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(20), unique=True, nullable=False)
    student_name = db.Column(db.String(200))
    major = db.Column(db.String(100))  # علوم الحاسب / تقنية المعلومات / هندسة الحاسب
    degree = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    requests = db.relationship('WithdrawalRequest', backref='student', lazy=True)


class WithdrawalRequest(db.Model):
    __tablename__ = 'withdrawal_requests'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    course_code = db.Column(db.String(50), nullable=False)
    course_name = db.Column(db.String(200))
    semester = db.Column(db.String(50))
    year = db.Column(db.String(20))
    reason_type = db.Column(db.String(50))  # صحية / عائلية / أكاديمية / etc.
    reason = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')  # pending / approved / rejected
    eligible = db.Column(db.Boolean, default=False)
    errors = db.Column(db.Text, default='[]')  # JSON list
    warnings = db.Column(db.Text, default='[]')  # JSON list
    rules_checked = db.Column(db.Text, default='[]')  # JSON list of rule check results
    transcript_file = db.Column(db.String(300))  # stored PDF filename
    supporting_doc = db.Column(db.String(300))  # stored supporting document filename
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Unique constraint: one request per student per course per semester/year
    __table_args__ = (
        db.UniqueConstraint('student_id', 'course_code', 'semester', 'year',
                            name='uq_student_course_semester_year'),
    )

    def get_errors(self):
        try:
            return json.loads(self.errors)
        except (json.JSONDecodeError, TypeError):
            return []

    def get_warnings(self):
        try:
            return json.loads(self.warnings)
        except (json.JSONDecodeError, TypeError):
            return []

    def get_rules_checked(self):
        try:
            return json.loads(self.rules_checked)
        except (json.JSONDecodeError, TypeError):
            return []


# ============ Helper Functions ============

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_or_create_student(student_id_str, student_name, major, degree):
    """Get existing student or create a new one."""
    student = Student.query.filter_by(student_id=student_id_str).first()
    if student:
        if student_name:
            student.student_name = student_name
        if major:
            student.major = major
        if degree:
            student.degree = degree
        db.session.commit()
    else:
        student = Student(
            student_id=student_id_str,
            student_name=student_name,
            major=major,
            degree=degree
        )
        db.session.add(student)
        db.session.commit()
    return student


def get_db_withdrawal_count(student_db_id):
    """Count total past withdrawal requests from the database."""
    return WithdrawalRequest.query.filter_by(
        student_id=student_db_id
    ).count()


def check_duplicate_request(student_db_id, course_code, semester, year):
    """Check if this exact request already exists."""
    return WithdrawalRequest.query.filter_by(
        student_id=student_db_id,
        course_code=course_code,
        semester=semester,
        year=year
    ).first()


# ============ Transcript Parsing ============

def parse_transcript(filepath):
    """Parse a University of Tabuk transcript PDF and extract relevant data."""
    doc = fitz.open(filepath)
    full_text = ""
    for page in doc:
        full_text += page.get_text() + "\n"
    doc.close()

    # Normalize Arabic Presentation Forms (U+FE70-U+FEFF) to standard Arabic
    full_text = unicodedata.normalize('NFKC', full_text)

    data = {
        'student_name': '',
        'student_id': '',
        'college': '',
        'department': '',
        'degree': '',
        'gpa': 0.0,
        'total_credits_completed': 0,
        'total_credits_plan': 0,
        'remaining_credits': 0,
        'current_semester_courses': [],
        'withdrawal_count': 0,
        'withdrawn_courses': [],
        'semesters_count': 0,
        'is_first_year': False,
        'expected_graduate': False,
        'all_courses': [],
        'raw_text': full_text
    }

    lines = full_text.split('\n')
    lines = [l.strip() for l in lines if l.strip()]

    # Track course codes and their corresponding grades for withdrawal detection
    course_codes = []
    grades_list = []

    for i, line in enumerate(lines):
        # Student name: "الاسم : ..." or "اسم الطالب : ..." or "...name: الاسم" (RTL)
        if ('الاسم' in line and ':' in line) or 'اسم الطالب' in line:
            # Format 1: "الاسم : نواف بن سلطان..."
            name_match = re.search(r'(?:الاسم|اسم الطالب|اسم الطالبة)\s*:\s*(.+)', line)
            if name_match:
                name_val = name_match.group(1).strip()
                if name_val and name_val != 'الاسم':
                    data['student_name'] = name_val
            else:
                # Format 2 (RTL): "معاذ بن عبدالمجيد...: الاسم"
                name_match2 = re.search(r'^(.+?):\s*(?:الاسم|اسم الطالب)', line)
                if name_match2:
                    data['student_name'] = name_match2.group(1).strip()

        # Student ID: "451007699 : الرقم الأكاديمي" or "الرقم الجامعي : 451007699"
        if 'الرقم الأكاديمي' in line or 'الرقم الجامعي' in line or 'رقم الطالب' in line:
            id_match = re.search(r'(\d{7,10})', line)
            if id_match:
                data['student_id'] = id_match.group(1)
            elif i + 1 < len(lines):
                id_match = re.search(r'(\d{7,10})', lines[i + 1])
                if id_match:
                    data['student_id'] = id_match.group(1)

        # College: "الكلية :كلية الحاسبات..."
        if 'الكلية' in line and ':' in line:
            college_match = re.search(r'الكلية\s*:\s*(.+)', line)
            if college_match:
                data['college'] = college_match.group(1).strip()

        # Major/Department: "التخصص  :هندسة الحاسب1131225656 :   السجل المدني"
        # Also standalone: "هندسة الحاسب" or "علوم الحاسب" or "تقنية المعلومات"
        if 'التخصص' in line and ':' in line:
            dept_match = re.search(r'التخصص\s*:\s*(.+)', line)
            if dept_match:
                dept_val = dept_match.group(1).strip()
                # Remove civil ID number and anything after it
                dept_val = re.sub(r'\d{7,}.*', '', dept_val).strip()
                if dept_val and dept_val != 'التخصص':
                    data['department'] = dept_val

        # GPA: look for cumulative GPA values (تراكمي section)
        if 'المعدل التراكمي' in line or 'التراكمي' in line:
            gpa_match = re.search(r'(\d+\.\d+)', line)
            if gpa_match:
                data['gpa'] = float(gpa_match.group(1))

        # Degree: "البكالوريوس" or "بكالوريوس"
        if 'بكالوريوس' in line or 'البكالوريوس' in line:
            data['degree'] = 'بكالوريوس'
        elif 'دبلوم متوسط' in line:
            data['degree'] = 'دبلوم متوسط'
        elif 'دبلوم مشارك' in line:
            data['degree'] = 'دبلوم مشارك'

        # Collect course codes (like "CSC 1201", "MATH 1102")
        course_match = re.match(r'^([A-Z]{2,5}\s+\d{3,4})$', line)
        if course_match:
            course_codes.append(course_match.group(1).strip())

    # Count withdrawals: grade "ع" appears as a standalone line
    # The grades appear in a block after course codes, in the same order
    # A standalone "ع" line is a withdrawal grade
    for line in lines:
        if line == 'ع':
            data['withdrawal_count'] += 1

    # Also check for ع in lines with course codes (older format)
    withdrawal_pattern = re.compile(r'\bع\b')
    for line in lines:
        if withdrawal_pattern.search(line) and line != 'ع':
            if any(char.isdigit() for char in line) and re.search(r'[A-Z]', line):
                data['withdrawal_count'] += 1
                data['withdrawn_courses'].append(line.strip())

    # Extract credits info
    for line in lines:
        credits_match = re.search(r'(?:مجموع الساعات|إجمالي الساعات|ساعات الخطة)[:\s]*(\d+)', line)
        if credits_match:
            data['total_credits_plan'] = int(credits_match.group(1))

        completed_match = re.search(r'(?:الساعات المكتسبة|الساعات المجتازة|مكتسبة)[:\s]*(\d+)', line)
        if completed_match:
            data['total_credits_completed'] = int(completed_match.group(1))

        remaining_match = re.search(r'(?:الساعات المتبقية)[:\s]*(\d+)', line)
        if remaining_match:
            data['remaining_credits'] = int(remaining_match.group(1))

    # Count semesters: "هـ1445 الفصل الأول", "هـ1446 الفصل الثاني", etc.
    semester_pattern = re.compile(r'هـ\d{4}(?:/\d{4})?\s+الفصل\s+(?:الأول|الثاني|الصيفي)')
    semesters = set(semester_pattern.findall(full_text))
    data['semesters_count'] = len(semesters) if semesters else 0

    # Fallback: also count generic semester mentions
    if data['semesters_count'] == 0:
        fallback_pattern = re.compile(r'(?:الفصل الأول|الفصل الثاني|الفصل الصيفي)')
        fallback_semesters = fallback_pattern.findall(full_text)
        data['semesters_count'] = len(set(fallback_semesters))

    # First year check
    if data['semesters_count'] <= 2:
        data['is_first_year'] = True
    if data['student_id'] and len(data['student_id']) >= 3:
        try:
            admission_year = int(data['student_id'][:2])
            current_year = 47  # 1447
            if current_year - admission_year <= 1:
                data['is_first_year'] = True
        except ValueError:
            pass

    # Expected graduate check
    if data['remaining_credits'] > 0 and data['remaining_credits'] <= 18:
        data['expected_graduate'] = True

    # Extract cumulative GPA (last تراكمي GPA value)
    # The GPA values appear as standalone decimal numbers near تراكمي labels
    if data['gpa'] == 0.0:
        # Find all GPA-like values (X.XX format between 0 and 5)
        gpa_candidates = []
        in_cumulative = False
        for line in lines:
            if 'تراكمي' in line:
                in_cumulative = True
            if in_cumulative:
                gpa_match = re.match(r'^(\d+\.\d{2})$', line)
                if gpa_match:
                    val = float(gpa_match.group(1))
                    if 0 < val <= 5.0:
                        gpa_candidates.append(val)
        if gpa_candidates:
            data['gpa'] = gpa_candidates[-1]  # Last cumulative GPA

    if not data['degree']:
        data['degree'] = 'بكالوريوس'

    return data


# ============ Validation Logic ============

def validate_withdrawal(transcript_data, course_code, course_name, semester, year, reason):
    """Validate the course withdrawal request against university rules."""
    errors = []
    warnings = []
    rules_checked = []

    degree = transcript_data.get('degree', 'بكالوريوس')
    withdrawal_count = transcript_data.get('withdrawal_count', 0)
    is_first_year = transcript_data.get('is_first_year', False)
    expected_graduate = transcript_data.get('expected_graduate', False)
    remaining_credits = transcript_data.get('remaining_credits', 0)

    # Rule 1: Max withdrawal limits based on degree
    if degree == 'بكالوريوس':
        max_withdrawals = 6
        rules_checked.append({
            'rule': f'الحد الأقصى للاعتذار عن مقررات (بكالوريوس - نظام فصلي): {max_withdrawals} مقررات',
            'status': 'pass' if withdrawal_count < max_withdrawals else 'fail',
            'detail': f'عدد مرات الاعتذار السابقة: {withdrawal_count} من أصل {max_withdrawals}'
        })
        if withdrawal_count >= max_withdrawals:
            errors.append(f'تجاوزت الحد الأقصى للاعتذار عن المقررات ({max_withdrawals} مقررات للبكالوريوس). عدد مرات الاعتذار السابقة: {withdrawal_count}')

    elif degree == 'دبلوم متوسط':
        max_withdrawals = 3
        rules_checked.append({
            'rule': f'الحد الأقصى للاعتذار عن مقررات (دبلوم متوسط): {max_withdrawals} مقررات',
            'status': 'pass' if withdrawal_count < max_withdrawals else 'fail',
            'detail': f'عدد مرات الاعتذار السابقة: {withdrawal_count} من أصل {max_withdrawals}'
        })
        if withdrawal_count >= max_withdrawals:
            errors.append(f'تجاوزت الحد الأقصى للاعتذار عن المقررات ({max_withdrawals} مقررات للدبلوم المتوسط). عدد مرات الاعتذار السابقة: {withdrawal_count}')

    elif degree == 'دبلوم مشارك':
        max_withdrawals = 2
        rules_checked.append({
            'rule': f'الحد الأقصى للاعتذار عن مقررات (دبلوم مشارك): {max_withdrawals} مقررات',
            'status': 'pass' if withdrawal_count < max_withdrawals else 'fail',
            'detail': f'عدد مرات الاعتذار السابقة: {withdrawal_count} من أصل {max_withdrawals}'
        })
        if withdrawal_count >= max_withdrawals:
            errors.append(f'تجاوزت الحد الأقصى للاعتذار عن المقررات ({max_withdrawals} مقررات للدبلوم المشارك). عدد مرات الاعتذار السابقة: {withdrawal_count}')

    # Rule 2: Cannot be from first year courses
    if is_first_year:
        rules_checked.append({
            'rule': 'ألا يكون المقرر من مقررات السنة الدراسية الأولى',
            'status': 'fail',
            'detail': 'الطالب في السنة الأولى - لا يسمح بالاعتذار عن مقررات السنة الأولى'
        })
        errors.append('لا يسمح بالاعتذار عن مقررات السنة الدراسية الأولى')
    else:
        rules_checked.append({
            'rule': 'ألا يكون المقرر من مقررات السنة الدراسية الأولى',
            'status': 'pass',
            'detail': 'الطالب ليس في السنة الأولى'
        })

    # Rule 3: Expected graduates cannot withdraw
    if expected_graduate:
        rules_checked.append({
            'rule': 'لا يسمح للطالب المتوقع تخرجه الانسحاب من أي مقرر',
            'status': 'fail',
            'detail': f'الطالب متوقع تخرجه (الساعات المتبقية: {remaining_credits})'
        })
        errors.append('لا يسمح للطالب المتوقع تخرجه بالاعتذار عن أي مقرر مسجل في الفصل الدراسي')
    else:
        rules_checked.append({
            'rule': 'لا يسمح للطالب المتوقع تخرجه الانسحاب من أي مقرر',
            'status': 'pass',
            'detail': 'الطالب غير متوقع تخرجه'
        })

    # Rule 4: Check if course was previously withdrawn
    withdrawn_courses = transcript_data.get('withdrawn_courses', [])
    previously_withdrawn = False
    if course_code:
        for wc in withdrawn_courses:
            if course_code in wc:
                previously_withdrawn = True
                break

    if previously_withdrawn:
        rules_checked.append({
            'rule': 'ألا يكون المقرر قد سبق الانسحاب منه سابقاً',
            'status': 'fail',
            'detail': f'المقرر {course_code} تم الاعتذار عنه مسبقاً'
        })
        errors.append(f'المقرر {course_code} سبق الاعتذار عنه سابقاً')
    else:
        rules_checked.append({
            'rule': 'ألا يكون المقرر قد سبق الانسحاب منه سابقاً',
            'status': 'pass',
            'detail': 'لم يتم الاعتذار عن هذا المقرر مسبقاً'
        })

    # Rule 5: Summer semester check
    if semester and 'صيفي' in semester:
        rules_checked.append({
            'rule': 'ألا يكون المقرر مسجلاً في الفصل الصيفي',
            'status': 'fail',
            'detail': 'لا يسمح بالاعتذار عن مقررات الفصل الصيفي'
        })
        errors.append('لا يسمح بالاعتذار عن مقرر مسجل في الفصل الصيفي')
    else:
        rules_checked.append({
            'rule': 'ألا يكون المقرر مسجلاً في الفصل الصيفي',
            'status': 'pass',
            'detail': 'المقرر ليس في الفصل الصيفي'
        })

    # Rule 6: Remaining time must be sufficient
    rules_checked.append({
        'rule': 'أن تكون المدة النظامية المتبقية كافية لإنهاء متطلبات التخرج',
        'status': 'warning',
        'detail': 'يرجى التأكد من أن المدة النظامية المتبقية كافية لإنهاء متطلبات التخرج'
    })
    warnings.append('يرجى التأكد من أن المدة النظامية المتبقية كافية لإنهاء متطلبات التخرج')

    # Rule 7: Only 1 course per semester
    rules_checked.append({
        'rule': 'يسمح بالانسحاب من مقرر واحد فقط خلال الفصل الدراسي',
        'status': 'warning',
        'detail': 'تأكد من عدم تقديم طلب اعتذار آخر في نفس الفصل'
    })

    # Rule 8: Must not be only registered course
    rules_checked.append({
        'rule': 'ألا يكون المقرر الوحيد المسجل للطالب',
        'status': 'warning',
        'detail': 'تأكد من وجود مقررات أخرى مسجلة في الفصل الدراسي'
    })

    # Rule 9: Co-requisite check
    rules_checked.append({
        'rule': 'ألا يكون المقرر متزامناً مع مقرر آخر',
        'status': 'warning',
        'detail': 'تأكد من أن المقرر ليس متطلباً متزامناً مع مقرر آخر مسجل'
    })

    is_eligible = len(errors) == 0

    return {
        'eligible': is_eligible,
        'errors': errors,
        'warnings': warnings,
        'rules_checked': rules_checked,
        'transcript_data': {
            'student_name': transcript_data.get('student_name', ''),
            'student_id': transcript_data.get('student_id', ''),
            'major': transcript_data.get('major', ''),
            'department': transcript_data.get('department', ''),
            'degree': transcript_data.get('degree', ''),
            'gpa': transcript_data.get('gpa', 0),
            'withdrawal_count': withdrawal_count,
            'remaining_credits': remaining_credits,
            'is_first_year': is_first_year,
            'expected_graduate': expected_graduate
        }
    }


# ============ Routes ============

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/validate', methods=['POST'])
def validate():
    # Check if transcript file was uploaded
    if 'transcript' not in request.files:
        return jsonify({'error': 'لم يتم رفع السجل الأكاديمي'}), 400

    file = request.files['transcript']
    if file.filename == '':
        return jsonify({'error': 'لم يتم اختيار ملف'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'يرجى رفع ملف بصيغة PDF فقط'}), 400

    # Check supporting document
    if 'supporting_doc' not in request.files or request.files['supporting_doc'].filename == '':
        return jsonify({'error': 'يرجى رفع المستند الداعم لسبب الاعتذار'}), 400

    supporting_file = request.files['supporting_doc']
    if not allowed_file(supporting_file.filename):
        return jsonify({'error': 'يرجى رفع المستند الداعم بصيغة PDF فقط'}), 400

    # Save files with unique names
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    unique_filename = f"{uuid.uuid4().hex}.pdf"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
    file.save(filepath)

    supporting_doc_filename = f"{uuid.uuid4().hex}.pdf"
    supporting_doc_path = os.path.join(app.config['UPLOAD_FOLDER'], supporting_doc_filename)
    supporting_file.save(supporting_doc_path)

    try:
        # Parse transcript
        transcript_data = parse_transcript(filepath)

        # Get form data
        course_code = request.form.get('course_code', '').strip()
        course_name = request.form.get('course_name', '').strip()
        semester = request.form.get('semester', '').strip()
        year = request.form.get('year', '').strip()
        reason_type = request.form.get('reason_type', '').strip()
        reason = request.form.get('reason', '').strip()

        # Get selected major from form
        selected_major = request.form.get('major', '').strip()

        # Override with form data if provided
        if request.form.get('student_name'):
            transcript_data['student_name'] = request.form.get('student_name')
        if request.form.get('student_id'):
            transcript_data['student_id'] = request.form.get('student_id')
        if request.form.get('degree'):
            transcript_data['degree'] = request.form.get('degree')

        # Use selected major from form (major is just for identifying the student's department)
        transcript_data['major'] = selected_major

        # Get or create student in DB
        student_id_str = transcript_data.get('student_id', '')
        if not student_id_str:
            student_id_str = request.form.get('student_id', 'unknown')

        student = get_or_create_student(
            student_id_str,
            transcript_data.get('student_name', ''),
            transcript_data.get('major', ''),
            transcript_data.get('degree', '')
        )

        # Check for duplicate request
        existing = check_duplicate_request(student.id, course_code, semester, year)
        if existing:
            os.remove(filepath)
            os.remove(supporting_doc_path)
            return jsonify({
                'error': f'تم تقديم طلب اعتذار لنفس المقرر ({course_code}) في نفس الفصل مسبقاً. رقم الطلب: {existing.id}',
                'duplicate': True,
                'request_id': existing.id
            }), 409

        # Validate
        result = validate_withdrawal(transcript_data, course_code, course_name, semester, year, reason)

        # Save request to DB
        withdrawal_req = WithdrawalRequest(
            student_id=student.id,
            course_code=course_code,
            course_name=course_name,
            semester=semester,
            year=year,
            reason_type=reason_type,
            reason=reason,
            status='pending',
            eligible=result['eligible'],
            errors=json.dumps(result['errors'], ensure_ascii=False),
            warnings=json.dumps(result['warnings'], ensure_ascii=False),
            rules_checked=json.dumps(result['rules_checked'], ensure_ascii=False),
            transcript_file=unique_filename,
            supporting_doc=supporting_doc_filename
        )
        db.session.add(withdrawal_req)
        db.session.commit()

        result['request_id'] = withdrawal_req.id
        return jsonify(result)

    except Exception as e:
        db.session.rollback()
        # Clean up files on error
        if os.path.exists(filepath):
            os.remove(filepath)
        if os.path.exists(supporting_doc_path):
            os.remove(supporting_doc_path)
        return jsonify({'error': f'حدث خطأ أثناء معالجة الملف: {str(e)}'}), 500


@app.route('/request/<int:request_id>')
def get_request_status(request_id):
    """Get the status of a specific withdrawal request."""
    req = WithdrawalRequest.query.get_or_404(request_id)
    return jsonify({
        'id': req.id,
        'course_code': req.course_code,
        'course_name': req.course_name,
        'semester': req.semester,
        'year': req.year,
        'status': req.status,
        'eligible': req.eligible,
        'created_at': req.created_at.isoformat() if req.created_at else None
    })


@app.route('/admin/supporting-doc/<int:request_id>')
def view_supporting_doc(request_id):
    """View/download the supporting document for a withdrawal request."""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'غير مصرح'}), 403

    req = WithdrawalRequest.query.get_or_404(request_id)
    if not req.supporting_doc:
        return jsonify({'error': 'لا يوجد مستند داعم'}), 404

    upload_dir = os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER'])
    return send_from_directory(
        upload_dir,
        req.supporting_doc,
        as_attachment=False,
        download_name=f"supporting_{req.student.student_id}_{req.course_code}.pdf"
    )


@app.route('/admin/transcript/<int:request_id>')
def view_transcript(request_id):
    """View/download the transcript PDF for a withdrawal request."""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'غير مصرح'}), 403

    req = WithdrawalRequest.query.get_or_404(request_id)
    if not req.transcript_file:
        return jsonify({'error': 'لا يوجد ملف مرفق'}), 404

    upload_dir = os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER'])
    return send_from_directory(
        upload_dir,
        req.transcript_file,
        as_attachment=False,
        download_name=f"transcript_{req.student.student_id}_{req.course_code}.pdf"
    )


# ============ Admin Routes ============

@app.route('/admin')
def admin():
    if not session.get('admin_logged_in'):
        return render_template('admin.html', logged_in=False)

    # Get filter params
    status_filter = request.args.get('status', '')
    major_filter = request.args.get('major', '')
    search = request.args.get('search', '')

    query = WithdrawalRequest.query.join(Student)

    if status_filter:
        query = query.filter(WithdrawalRequest.status == status_filter)
    if major_filter:
        query = query.filter(Student.major == major_filter)
    if search:
        query = query.filter(
            db.or_(
                Student.student_id.contains(search),
                Student.student_name.contains(search),
                WithdrawalRequest.course_code.contains(search)
            )
        )

    requests_list = query.order_by(WithdrawalRequest.created_at.desc()).all()

    # Stats
    total = WithdrawalRequest.query.count()
    pending = WithdrawalRequest.query.filter_by(status='pending').count()
    approved = WithdrawalRequest.query.filter_by(status='approved').count()
    rejected = WithdrawalRequest.query.filter_by(status='rejected').count()

    stats = {
        'total': total,
        'pending': pending,
        'approved': approved,
        'rejected': rejected
    }

    return render_template('admin.html',
                           logged_in=True,
                           requests=requests_list,
                           stats=stats,
                           status_filter=status_filter,
                           major_filter=major_filter,
                           search=search)


@app.route('/admin/login', methods=['POST'])
def admin_login():
    password = request.form.get('password', '')
    if password == ADMIN_PASSWORD:
        session['admin_logged_in'] = True
        return redirect(url_for('admin'), code=303)
    return render_template('admin.html', logged_in=False, error='كلمة المرور غير صحيحة')


@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin'))


@app.route('/admin/request/<int:request_id>')
def admin_request_detail(request_id):
    """Detailed view of a single withdrawal request."""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin'))

    req = WithdrawalRequest.query.get_or_404(request_id)
    return render_template('admin_detail.html',
                           logged_in=True,
                           req=req,
                           rules=req.get_rules_checked(),
                           errors=req.get_errors(),
                           warnings=req.get_warnings())


@app.route('/admin/update/<int:request_id>', methods=['POST'])
def admin_update_request(request_id):
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'غير مصرح'}), 403

    req = WithdrawalRequest.query.get_or_404(request_id)
    new_status = request.form.get('status')

    if new_status in ('approved', 'rejected', 'pending'):
        req.status = new_status
        db.session.commit()
        # Redirect back to detail page if came from there
        if request.form.get('from_detail'):
            return redirect(url_for('admin_request_detail', request_id=request_id), code=303)
        return redirect(url_for('admin'), code=303)

    return jsonify({'error': 'حالة غير صالحة'}), 400


# ============ App Startup ============

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    os.makedirs('uploads', exist_ok=True)
    app.run(debug=True, port=5000)
