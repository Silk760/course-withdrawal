"""Generate the white paper PDF for the Course Withdrawal Validation System."""
import os
from fpdf import FPDF

# Fonts
FONT_REG = r'C:\Windows\Fonts\arial.ttf'
FONT_BOLD = r'C:\Windows\Fonts\arialbd.ttf'
FONT_ITALIC = r'C:\Windows\Fonts\ariali.ttf'

# Colors
GREEN = (26, 86, 50)
GOLD = (184, 157, 92)
DARK = (33, 33, 33)
GRAY = (120, 120, 120)
WHITE = (255, 255, 255)
LIGHT_GREEN = (232, 245, 233)
LIGHT_RED = (255, 235, 238)
LIGHT_YELLOW = (255, 249, 196)
TABLE_HEADER = (26, 86, 50)
TABLE_HEADER_TEXT = (255, 255, 255)
TABLE_ROW_ALT = (245, 250, 245)


class WhitePaperPDF(FPDF):
    def __init__(self):
        super().__init__('P', 'mm', 'A4')
        self.add_font('ar', '', FONT_REG)
        self.add_font('ar', 'B', FONT_BOLD)
        self.add_font('ar', 'I', FONT_ITALIC)
        self.set_text_shaping(True)
        self.set_auto_page_break(auto=True, margin=25)

    def header(self):
        if self.page_no() <= 1:
            return
        self.set_font('ar', '', 8)
        self.set_text_color(*GRAY)
        self.cell(0, 6, 'نظام الاعتذار عن المقررات', align='L')
        self.cell(0, 6, 'جامعة تبوك — كلية الحاسبات وتقنية المعلومات', align='R', new_x='LEFT', new_y='NEXT')
        self.set_draw_color(*GREEN)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def footer(self):
        self.set_y(-20)
        self.set_draw_color(*GOLD)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(3)
        self.set_font('ar', '', 8)
        self.set_text_color(*GRAY)
        self.cell(0, 5, f'{self.page_no()}', align='C')

    def section_title(self, num, title):
        self.ln(6)
        self.set_font('ar', 'B', 16)
        self.set_text_color(*GREEN)
        self.cell(0, 10, f'{num}. {title}', align='R', new_x='LEFT', new_y='NEXT')
        self.set_draw_color(*GOLD)
        self.set_line_width(0.6)
        self.line(10, self.get_y(), 200, self.get_y())
        self.set_line_width(0.2)
        self.ln(4)

    def subsection_title(self, title):
        self.ln(3)
        self.set_font('ar', 'B', 13)
        self.set_text_color(26, 86, 50)
        self.cell(0, 8, title, align='R', new_x='LEFT', new_y='NEXT')
        self.ln(2)

    def body_text(self, text):
        self.set_font('ar', '', 11)
        self.set_text_color(*DARK)
        self.multi_cell(0, 7, text, align='R')
        self.ln(2)

    def bullet_item(self, text, bold_prefix=''):
        self.set_font('ar', '', 11)
        self.set_text_color(*DARK)
        if bold_prefix:
            full_text = f'●  {bold_prefix}{text}'
        else:
            full_text = f'●  {text}'
        self.cell(0, 7, full_text, align='R', new_x='LEFT', new_y='NEXT')

    def numbered_item(self, num, text):
        self.set_font('ar', '', 11)
        self.set_text_color(*DARK)
        self.cell(0, 7, f'  {num}. {text}', align='R', new_x='LEFT', new_y='NEXT')

    def table_header(self, cols):
        """cols: list of (text, width)"""
        self.set_font('ar', 'B', 10)
        self.set_fill_color(*TABLE_HEADER)
        self.set_text_color(*TABLE_HEADER_TEXT)
        for text, w in cols:
            self.cell(w, 8, text, border=1, align='C', fill=True)
        self.ln()

    def table_row(self, cols, alt=False, cell_colors=None):
        """cols: list of (text, width)"""
        self.set_font('ar', '', 9.5)
        self.set_text_color(*DARK)
        if alt:
            self.set_fill_color(*TABLE_ROW_ALT)
        else:
            self.set_fill_color(*WHITE)

        for i, (text, w) in enumerate(cols):
            if cell_colors and i in cell_colors:
                self.set_fill_color(*cell_colors[i])
                self.cell(w, 7, text, border=1, align='C', fill=True)
                if alt:
                    self.set_fill_color(*TABLE_ROW_ALT)
                else:
                    self.set_fill_color(*WHITE)
            else:
                self.cell(w, 7, text, border=1, align='C', fill=alt)
        self.ln()


def generate():
    pdf = WhitePaperPDF()

    # ===== Title Page =====
    pdf.add_page()
    pdf.ln(25)

    pdf.set_font('ar', '', 14)
    pdf.set_text_color(*DARK)
    pdf.cell(0, 8, 'المملكة العربية السعودية', align='C', new_x='LEFT', new_y='NEXT')
    pdf.cell(0, 8, 'وزارة التعليم', align='C', new_x='LEFT', new_y='NEXT')
    pdf.ln(5)

    pdf.set_font('ar', 'B', 24)
    pdf.set_text_color(*GREEN)
    pdf.cell(0, 12, 'جامعة تبوك', align='C', new_x='LEFT', new_y='NEXT')
    pdf.set_font('ar', '', 14)
    pdf.set_text_color(*DARK)
    pdf.cell(0, 8, 'كلية الحاسبات وتقنية المعلومات', align='C', new_x='LEFT', new_y='NEXT')
    pdf.ln(10)

    # Gold line
    pdf.set_draw_color(*GOLD)
    pdf.set_line_width(1.0)
    pdf.line(30, pdf.get_y(), 180, pdf.get_y())
    pdf.ln(12)

    pdf.set_font('ar', 'B', 28)
    pdf.set_text_color(*GREEN)
    pdf.cell(0, 14, 'ورقة بيضاء', align='C', new_x='LEFT', new_y='NEXT')
    pdf.ln(3)

    pdf.set_font('ar', 'B', 16)
    pdf.set_text_color(*DARK)
    pdf.cell(0, 10, 'نظام التحقق من أهلية الاعتذار عن المقررات الدراسية', align='C', new_x='LEFT', new_y='NEXT')
    pdf.set_font('ar', 'I', 13)
    pdf.set_text_color(*GRAY)
    pdf.cell(0, 8, 'Course Withdrawal Eligibility Validation System', align='C', new_x='LEFT', new_y='NEXT')
    pdf.ln(10)

    # Gold line
    pdf.set_draw_color(*GOLD)
    pdf.line(30, pdf.get_y(), 180, pdf.get_y())
    pdf.ln(20)

    # Metadata table
    meta = [
        ('الإصدار:', '1.1'),
        ('التاريخ:', '19 فبراير 2026م'),
        ('الجهة:', 'كلية الحاسبات وتقنية المعلومات'),
        ('الحالة:', 'نسخة نهائية'),
    ]
    for label, value in meta:
        pdf.set_font('ar', 'B', 12)
        pdf.set_text_color(*DARK)
        pdf.cell(90, 8, value, align='R')
        pdf.cell(80, 8, label, align='R', new_x='LEFT', new_y='NEXT')

    pdf.ln(30)
    pdf.set_font('ar', '', 9)
    pdf.set_text_color(*GRAY)
    pdf.cell(0, 6, 'جميع الحقوق محفوظة © 2025-2026 — جامعة تبوك', align='C')

    # ===== Table of Contents =====
    pdf.add_page()
    pdf.set_font('ar', 'B', 20)
    pdf.set_text_color(*GREEN)
    pdf.cell(0, 12, 'فهرس المحتويات', align='C', new_x='LEFT', new_y='NEXT')
    pdf.ln(8)

    toc = [
        ('1', 'الملخص التنفيذي'),
        ('2', 'الخلفية والسياق'),
        ('3', 'ضوابط الاعتذار عن المقررات'),
        ('4', 'البنية التقنية للنظام'),
        ('5', 'سير العمل'),
        ('6', 'تحليل السجل الأكاديمي'),
        ('7', 'الأمن والخصوصية'),
        ('8', 'النشر والاستضافة'),
        ('9', 'الاختبار والتحقق'),
        ('10', 'التطوير المستقبلي'),
        ('11', 'الخلاصة'),
    ]
    for num, title in toc:
        pdf.set_font('ar', '', 12)
        pdf.set_text_color(*DARK)
        pdf.cell(15, 9, num, align='C')
        dots = '.' * 60
        pdf.cell(0, 9, f'{title}  {dots}', align='R', new_x='LEFT', new_y='NEXT')

    # ===== Section 1: Executive Summary =====
    pdf.add_page()
    pdf.section_title('1', 'الملخص التنفيذي')

    pdf.body_text(
        'يقدم هذا المستند وصفاً شاملاً لنظام التحقق من أهلية الاعتذار عن المقررات الدراسية، '
        'المصمم خصيصاً لكلية الحاسبات وتقنية المعلومات بجامعة تبوك. يهدف النظام إلى أتمتة '
        'عملية فحص طلبات الاعتذار عن المقررات وفقاً للضوابط واللوائح الأكاديمية المعتمدة بالجامعة.'
    )

    pdf.subsection_title('أهداف النظام')
    for prefix, text in [
        ('الأتمتة: ', 'التحقق الآلي من استيفاء الطالب لشروط الاعتذار عن المقرر.'),
        ('الدقة: ', 'تقليل الأخطاء البشرية في مراجعة الطلبات عبر تحليل السجل الأكاديمي إلكترونياً.'),
        ('الكفاءة: ', 'تسريع عملية معالجة الطلبات وتقليل العبء الإداري على أقسام الكلية.'),
        ('التتبع: ', 'حفظ جميع الطلبات في قاعدة بيانات مركزية لمتابعة الحالة والإحصائيات.'),
        ('الشفافية: ', 'تزويد الطالب بتقرير فوري يوضح نتائج فحص كل ضابط من ضوابط الاعتذار.'),
    ]:
        pdf.bullet_item(text, prefix)

    pdf.subsection_title('نطاق العمل')
    pdf.body_text(
        'يغطي النظام طلبات الاعتذار المقدمة من طلاب وطالبات كلية الحاسبات وتقنية المعلومات في التخصصات الثلاثة:'
    )
    pdf.numbered_item('1', 'علوم الحاسب (Computer Science)')
    pdf.numbered_item('2', 'تقنية المعلومات (Information Technology)')
    pdf.numbered_item('3', 'هندسة الحاسب (Computer Engineering)')

    # ===== Section 2: Background =====
    pdf.section_title('2', 'الخلفية والسياق')

    pdf.subsection_title('مشكلة العمل')
    pdf.body_text(
        'تتطلب عملية الاعتذار عن المقررات في الوضع الحالي مراجعة يدوية للسجل الأكاديمي '
        'للطالب من قبل المرشد الأكاديمي أو رئيس القسم، وذلك للتحقق من عدة شروط وضوابط. '
        'هذه العملية اليدوية تعاني من:'
    )
    pdf.bullet_item('استهلاك وقت كبير في مراجعة كل طلب على حدة.')
    pdf.bullet_item('احتمالية الخطأ البشري في حساب عدد مرات الاعتذار السابقة.')
    pdf.bullet_item('صعوبة تتبع الطلبات المتعددة والتحقق من عدم التكرار.')
    pdf.bullet_item('عدم وجود قاعدة بيانات مركزية لحفظ تاريخ الطلبات.')

    pdf.subsection_title('الحل المقترح')
    pdf.body_text('نظام ويب (Web Application) متكامل يقوم بـ:')
    pdf.numbered_item('1', 'استقبال طلب الاعتذار إلكترونياً مع السجل الأكاديمي بصيغة PDF.')
    pdf.numbered_item('2', 'تحليل السجل الأكاديمي آلياً واستخراج البيانات الأكاديمية.')
    pdf.numbered_item('3', 'فحص الطلب مقابل 9 ضوابط أكاديمية وإصدار تقرير فوري.')
    pdf.numbered_item('4', 'حفظ الطلب في قاعدة بيانات مع إمكانية المتابعة.')
    pdf.numbered_item('5', 'لوحة إدارة لرؤساء الأقسام لمراجعة الطلبات واتخاذ القرار.')

    # ===== Section 3: Withdrawal Rules =====
    pdf.add_page()
    pdf.section_title('3', 'ضوابط الاعتذار عن المقررات')

    pdf.body_text('يطبق النظام الضوابط التالية المستندة إلى اللائحة الأكاديمية لجامعة تبوك:')

    pdf.subsection_title('الضوابط المطبقة')

    rules_cols = [('النتيجة', 25), ('التفاصيل', 55), ('الضابط', 80), ('#', 10)]
    pdf.table_header(rules_cols)

    rules_data = [
        ('1', 'الحد الأقصى للاعتذار حسب الدرجة', 'بكالوريوس: 6، دبلوم متوسط: 3، دبلوم مشارك: 2', 'نجاح/رسوب'),
        ('2', 'ألا يكون من مقررات السنة الأولى', 'فحص عدد الفصول وسنة القبول', 'نجاح/رسوب'),
        ('3', 'ألا يكون الطالب متوقع تخرجه', 'فحص الساعات المتبقية (أقل من 18)', 'نجاح/رسوب'),
        ('4', 'عدم تكرار الاعتذار عن نفس المقرر', 'البحث عن تقدير "ع" في السجل', 'نجاح/رسوب'),
        ('5', 'ألا يكون المقرر في الفصل الصيفي', 'فحص نوع الفصل الدراسي', 'نجاح/رسوب'),
        ('6', 'كفاية المدة النظامية المتبقية', 'التأكد من كفاية الوقت للتخرج', 'تنبيه'),
        ('7', 'مقرر واحد فقط في الفصل', 'عدم وجود طلب آخر في نفس الفصل', 'تنبيه'),
        ('8', 'ألا يكون المقرر الوحيد المسجل', 'وجود مقررات أخرى مسجلة', 'تنبيه'),
        ('9', 'فحص المتطلبات المتزامنة', 'عدم وجود مقرر متزامن يعتمد عليه', 'تنبيه'),
    ]
    for i, (num, rule, detail, result) in enumerate(rules_data):
        pdf.table_row([(result, 25), (detail, 55), (rule, 80), (num, 10)], alt=i % 2 == 1)

    pdf.ln(4)
    pdf.set_font('ar', 'B', 10)
    pdf.set_text_color(*DARK)
    pdf.multi_cell(0, 6,
        'ملاحظة: الضوابط ذات النتيجة "نجاح/رسوب" توقف أهلية الطلب فوراً عند عدم استيفائها. '
        'أما ضوابط "تنبيه" فتُعرض كملاحظات تحتاج مراجعة يدوية.',
        align='R'
    )

    pdf.subsection_title('آلية تحديد الأهلية')
    pdf.bullet_item('إذا نجح الطالب في جميع ضوابط "نجاح/رسوب" ← مؤهل ✓')
    pdf.bullet_item('إذا رسب في أي ضابط واحد ← غير مؤهل ✗ مع بيان الأسباب')

    # ===== Section 4: Architecture =====
    pdf.add_page()
    pdf.section_title('4', 'البنية التقنية للنظام')

    pdf.subsection_title('التقنيات المستخدمة')

    tech_cols = [('الوصف', 70), ('التقنية', 35), ('المكون', 45)]
    pdf.table_header(tech_cols)
    tech_data = [
        ('Backend Framework', 'Flask 3.1', 'إطار عمل ويب بلغة Python'),
        ('قاعدة البيانات', 'PostgreSQL', 'قاعدة بيانات علائقية (إنتاج)'),
        ('ORM', 'Flask-SQLAlchemy', 'واجهة التعامل مع قاعدة البيانات'),
        ('تحليل الـ PDF', 'PyMuPDF (fitz)', 'استخراج النصوص من ملفات PDF العربية'),
        ('خادم الإنتاج', 'Gunicorn', 'خادم WSGI للإنتاج'),
        ('الاستضافة', 'Railway', 'منصة استضافة سحابية'),
        ('الواجهة الأمامية', 'HTML/CSS/JS', 'واجهة مستخدم عربية (RTL)'),
    ]
    for i, (comp, tech, desc) in enumerate(tech_data):
        pdf.table_row([(desc, 70), (tech, 35), (comp, 45)], alt=i % 2 == 1)

    pdf.subsection_title('نموذج البيانات')
    pdf.body_text('يتكون النظام من جدولين رئيسيين في قاعدة البيانات:')

    # Students table
    pdf.set_font('ar', 'B', 11)
    pdf.set_text_color(*GREEN)
    pdf.cell(0, 8, 'جدول الطلاب (students)', align='R', new_x='LEFT', new_y='NEXT')
    pdf.ln(2)

    s_cols = [('الوصف', 70), ('النوع', 45), ('الحقل', 45)]
    pdf.table_header(s_cols)
    s_data = [
        ('id', 'Integer (PK)', 'المعرف التسلسلي'),
        ('student_id', 'String (Unique)', 'الرقم الجامعي'),
        ('student_name', 'String', 'اسم الطالب'),
        ('major', 'String', 'التخصص'),
        ('degree', 'String', 'الدرجة العلمية'),
    ]
    for i, (field, ftype, desc) in enumerate(s_data):
        pdf.table_row([(desc, 70), (ftype, 45), (field, 45)], alt=i % 2 == 1)

    pdf.ln(4)

    # Withdrawal requests table
    pdf.set_font('ar', 'B', 11)
    pdf.set_text_color(*GREEN)
    pdf.cell(0, 8, 'جدول طلبات الاعتذار (withdrawal_requests)', align='R', new_x='LEFT', new_y='NEXT')
    pdf.ln(2)

    w_cols = [('الوصف', 70), ('النوع', 45), ('الحقل', 45)]
    pdf.table_header(w_cols)
    w_data = [
        ('id', 'Integer (PK)', 'معرف الطلب'),
        ('student_id', 'FK → students', 'مرجع الطالب'),
        ('course_code', 'String', 'رمز المقرر'),
        ('course_name', 'String', 'اسم المقرر'),
        ('semester', 'String', 'الفصل الدراسي'),
        ('year', 'String', 'العام الدراسي'),
        ('reason_type', 'String', 'نوع سبب الاعتذار'),
        ('reason', 'Text', 'تفاصيل إضافية'),
        ('status', 'String', 'الحالة (انتظار / مقبول / مرفوض)'),
        ('eligible', 'Boolean', 'نتيجة فحص الأهلية'),
        ('rules_checked', 'JSON', 'تفاصيل فحص كل ضابط'),
        ('transcript_file', 'String', 'مسار ملف السجل الأكاديمي'),
        ('supporting_doc', 'String', 'مسار المستند الداعم'),
        ('created_at', 'DateTime', 'تاريخ تقديم الطلب'),
    ]
    for i, (field, ftype, desc) in enumerate(w_data):
        pdf.table_row([(desc, 70), (ftype, 45), (field, 45)], alt=i % 2 == 1)

    pdf.ln(4)
    pdf.set_font('ar', 'B', 10)
    pdf.set_text_color(*DARK)
    pdf.multi_cell(0, 6,
        'قيد التفرد: يُطبق قيد فريد (Unique Constraint) على مجموعة الحقول '
        '(student_id, course_code, semester, year) لمنع تكرار الطلب لنفس المقرر في نفس الفصل.',
        align='R'
    )

    # ===== Section 5: Workflow =====
    pdf.add_page()
    pdf.section_title('5', 'سير العمل')

    pdf.subsection_title('مسار تقديم الطلب (الطالب)')
    steps = [
        'الخطوة 1 — رفع السجل الأكاديمي: يدخل الطالب إلى الصفحة الرئيسية ويرفع السجل الأكاديمي (Transcript) بصيغة PDF.',
        'التحليل التلقائي: يحلل النظام ملف PDF فوراً ويستخرج اسم الطالب، رقمه الجامعي، كليته، تخصصه، معدله التراكمي، والفصل الدراسي الحالي.',
        'الخطوة 2 — مراجعة البيانات: تُعرض البيانات المستخرجة للطالب مع قائمة مقرراته المسجلة في الفصل الحالي للتأكد.',
        'اختيار المقرر: يختار الطالب المقرر المراد الاعتذار عنه من قائمة مقرراته الحالية.',
        'سبب الاعتذار: يختار نوع السبب ويُضيف تفاصيل إضافية اختياريًا.',
        'رفع المستند الداعم: يرفع مستندًا يدعم سببه (تقرير طبي، خطاب رسمي، إلخ) بصيغة PDF.',
        'الإقرار والتعهد: يوافق على بنود الإقرار الكاملة قبل التقديم.',
        'التقديم: يضغط زر "التحقق وتقديم الطلب".',
        'النتيجة الفورية: يتلقى تقريرًا فوريًا يوضح حالة الأهلية، نتائج فحص كل ضابط، والتنبيهات، ورقم الطلب للمتابعة.',
    ]
    for i, s in enumerate(steps, 1):
        pdf.numbered_item(i, s)

    pdf.subsection_title('أسباب الاعتذار المتاحة')
    reasons_cols = [('الوصف', 90), ('السبب', 45), ('#', 15)]
    pdf.table_header(reasons_cols)
    reasons_data = [
        ('1', 'صحية', 'حالة مرضية أو إصابة تمنع من متابعة الدراسة'),
        ('2', 'عائلية', 'ظروف عائلية طارئة (وفاة، مرض قريب، سفر اضطراري)'),
        ('3', 'أكاديمية', 'تعارض في الجدول أو صعوبة أكاديمية'),
        ('4', 'نفسية', 'ضغوط نفسية تؤثر على الأداء الأكاديمي'),
        ('5', 'مالية', 'ظروف مالية تمنع الاستمرار في المقرر'),
        ('6', 'وظيفية', 'الحصول على وظيفة تتعارض مع أوقات الدراسة'),
        ('7', 'أخرى', 'أسباب أخرى مع إمكانية التوضيح'),
    ]
    for i, (num, reason, desc) in enumerate(reasons_data):
        pdf.table_row([(desc, 90), (reason, 45), (num, 15)], alt=i % 2 == 1)

    pdf.subsection_title('مسار إدارة الطلبات (رئيس القسم / المسؤول)')
    admin_steps = [
        'يدخل المسؤول إلى لوحة الإدارة عبر /admin.',
        'يُدخل كلمة المرور للدخول.',
        'تُعرض إحصائيات: إجمالي الطلبات، قيد الانتظار، المقبولة، المرفوضة.',
        'يمكن تصفية الطلبات حسب: الحالة، التخصص، البحث النصي.',
        'عند الضغط على "تفاصيل" تُعرض صفحة تفصيلية كاملة.',
        'يتخذ المسؤول قراره: قبول أو رفض الطلب.',
    ]
    for i, s in enumerate(admin_steps, 1):
        pdf.numbered_item(i, s)

    # ===== Section 6: PDF Parsing =====
    pdf.add_page()
    pdf.section_title('6', 'تحليل السجل الأكاديمي')

    pdf.subsection_title('آلية تحليل ملفات PDF')
    pdf.body_text(
        'يستخدم النظام مكتبة PyMuPDF لاستخراج النصوص من ملفات السجل الأكاديمي. '
        'يدعم النظام كلا النسختين من السجلات الصادرة من جامعة تبوك: النسخة العربية والنسخة الإنجليزية. '
        'تشمل عملية التحليل:'
    )

    pdf.numbered_item('1', 'تطبيع النص: تحويل Unicode Presentation Forms إلى الصيغة القياسية (NFKC).')
    pdf.numbered_item('2', 'استخراج بيانات الطالب: الرقم الجامعي، الاسم، الكلية، التخصص، الدرجة العلمية.')
    pdf.numbered_item('3', 'استخراج المقررات الحالية: تحديد مقررات الفصل الحالي (بدون تقدير) تلقائياً.')
    pdf.numbered_item('4', 'استخراج البيانات الأكاديمية: المعدل التراكمي، عدد الفصول، مرات الاعتذار السابقة.')
    pdf.numbered_item('5', 'التحقق من حالة الطالب: هل هو في السنة الأولى؟ هل هو متوقع تخرجه؟')

    pdf.subsection_title('التحديات والحلول')
    ch_cols = [('الحل', 85), ('التحدي', 65)]
    pdf.table_header(ch_cols)
    challenges = [
        ('النصوص العربية تستخدم Unicode Presentation Forms', 'تطبيق NFKC Normalization قبل المعالجة'),
        ('السجل الإنجليزي: القيمة تسبق التسمية (RTL للأعمدة)', 'دعم النمطين: Value-before-Label وLabel-before-Value'),
        ('السجل الإنجليزي: تقديرات بالحروف الإنجليزية A+ B C W', 'نمط Regex يشمل التقديرات العربية والإنجليزية معاً'),
        ('السجل الإنجليزي: أسماء المقررات بالإنجليزية', 'كشف نصوص اللاتينية في كتلة أسماء المقررات'),
        ('تحديد تقدير الاعتذار "ع" أو "W"', 'البحث عن "ع" أو W كسطر مستقل ضمن التقديرات'),
        ('تنسيقات مختلفة لرأس الصفحة حسب الإصدار', 'استخدام تعبيرات منتظمة (Regex) مرنة متعددة الأنماط'),
    ]
    for i, (ch, sol) in enumerate(challenges):
        pdf.table_row([(sol, 85), (ch, 65)], alt=i % 2 == 1)

    pdf.ln(3)
    pdf.subsection_title('تنسيق السجل الإنجليزي (University of Tabuk)')
    pdf.body_text(
        'تستخدم السجلات الإنجليزية لجامعة تبوك تخطيطاً عمودياً متعدد الفصول، حيث تُستخرج '
        'البيانات عموداً بعمود. يظهر التقدير للمقررات الحالية (غير المكتملة) فارغاً، '
        'وهو ما يستخدمه النظام لتمييز مقررات الفصل الحالي تلقائياً.'
    )

    # ===== Section 7: Security =====
    pdf.section_title('7', 'الأمن والخصوصية')

    pdf.subsection_title('إجراءات الأمان المطبقة')
    security_items = [
        ('حماية لوحة الإدارة: ', 'تسجيل دخول بكلمة مرور مع جلسات مؤمنة (Session-based Authentication).'),
        ('حماية الملفات: ', 'تُحفظ الملفات المرفوعة بأسماء عشوائية (UUID) لمنع التخمين.'),
        ('الوصول المقيد: ', 'ملفات السجلات لا يمكن الوصول إليها إلا عبر لوحة الإدارة.'),
        ('التحقق من نوع الملف: ', 'يُقبل فقط ملفات بصيغة PDF.'),
        ('حجم الملف: ', 'الحد الأقصى 16 ميجابايت لكل ملف.'),
        ('منع التكرار: ', 'قيد تفرد في قاعدة البيانات يمنع تقديم طلب مكرر.'),
        ('متغيرات البيئة: ', 'المفاتيح الحساسة تُخزن كمتغيرات بيئة وليس في الكود.'),
    ]
    for prefix, text in security_items:
        pdf.bullet_item(text, prefix)

    # ===== Section 8: Deployment =====
    pdf.add_page()
    pdf.section_title('8', 'النشر والاستضافة')

    pdf.subsection_title('بيئة الإنتاج')
    pdf.body_text('يُنشر النظام على منصة Railway السحابية باستخدام:')
    pdf.bullet_item('الخادم: Gunicorn WSGI Server', '')
    pdf.bullet_item('قاعدة البيانات: PostgreSQL (إضافة Railway)', '')
    pdf.bullet_item('البناء: Nixpacks Builder (تلقائي)', '')

    pdf.subsection_title('متغيرات البيئة المطلوبة')
    env_cols = [('الوصف', 100), ('المتغير', 50)]
    pdf.table_header(env_cols)
    env_data = [
        ('DATABASE_URL', 'رابط قاعدة بيانات PostgreSQL (يُعين تلقائياً)'),
        ('SECRET_KEY', 'مفتاح تشفير الجلسات'),
        ('ADMIN_PASSWORD', 'كلمة مرور لوحة الإدارة'),
    ]
    for i, (var, desc) in enumerate(env_data):
        pdf.table_row([(desc, 100), (var, 50)], alt=i % 2 == 1)

    # ===== Section 9: Testing =====
    pdf.section_title('9', 'الاختبار والتحقق')

    pdf.body_text(
        'تم اختبار النظام باستخدام سجلات أكاديمية حقيقية من طلاب كلية الحاسبات '
        'وتقنية المعلومات بكلا النسختين العربية والإنجليزية، مع تغطية سيناريوهات متنوعة:'
    )

    test_cols = [('النتيجة', 20), ('المقرر', 25), ('السبب', 22), ('ع سابقة', 15), ('الطالب', 48), ('#', 10)]
    pdf.table_header(test_cols)
    test_data = [
        ('1', 'زياد الرشودي', '1', 'صحية', 'CSC 1201', 'مؤهل'),
        ('2', 'نواف الفقير (عربي)', '0', 'عائلية', 'CEN 1301', 'مؤهل'),
        ('3', 'سيف الحثربي', '1', 'أكاديمية', 'MATH 1204', 'مؤهل'),
        ('4', 'معاذ الرويعيات', '1', 'نفسية', 'PHYS 1251', 'مؤهل'),
        ('5', 'عبدالرحمن المضحوي', '3', 'مالية', 'CSC 1304', 'مؤهل'),
        ('6', 'ALJOHANI M. (إنجليزي)', '0', 'وظيفية', 'CEN 1303', 'مؤهل'),
        ('7', 'فارس الهلباني', '2', 'أخرى', 'MATH 1205', 'مؤهل'),
        ('8', 'فهد الرويثي', '1', 'صحية', 'CSC 1103', 'مؤهل'),
        ('9', 'أبراهيم الغامدي', '0', 'عائلية', 'CEN 1201', 'مؤهل'),
        ('10', 'عبدالله المساوي', '17', 'أكاديمية', 'CEN 1303', 'غير مؤهل'),
    ]
    for i, (num, name, w, reason, course, result) in enumerate(test_data):
        color = LIGHT_GREEN if result == 'مؤهل' else LIGHT_RED
        pdf.table_row(
            [(result, 20), (course, 25), (reason, 22), (w, 15), (name, 48), (num, 10)],
            alt=i % 2 == 1,
            cell_colors={0: color}
        )

    pdf.ln(4)
    pdf.set_font('ar', 'B', 11)
    pdf.set_text_color(*DARK)
    pdf.cell(0, 7, 'نتائج الاختبار:', align='R', new_x='LEFT', new_y='NEXT')
    pdf.set_font('ar', '', 11)
    pdf.bullet_item('9 من 10 طلبات مؤهلة (90%)')
    pdf.bullet_item('طلب واحد غير مؤهل بسبب تجاوز الحد الأقصى للاعتذارات (17 من 6 مسموح)')
    pdf.bullet_item('تمت تغطية جميع أنواع أسباب الاعتذار السبعة')
    pdf.bullet_item('نجح النظام في استخراج البيانات من السجلات العربية والإنجليزية على حد سواء')

    # ===== Section 10: Future Work =====
    pdf.add_page()
    pdf.section_title('10', 'التطوير المستقبلي')

    future_items = [
        ('التكامل مع النظام الأكاديمي: ', 'ربط النظام مع نظام Banner للحصول على البيانات مباشرة بدلاً من رفع PDF.'),
        ('نظام الإشعارات: ', 'إشعارات بريد إلكتروني أو SMS للطالب عند تحديث حالة الطلب.'),
        ('تعدد المستخدمين: ', 'حسابات منفصلة لكل رئيس قسم مع صلاحيات محددة.'),
        ('التقارير الإحصائية: ', 'رسوم بيانية وتقارير دورية عن اتجاهات الاعتذار حسب القسم.'),
        ('تطبيق الجوال: ', 'واجهة متوافقة مع الأجهزة المحمولة أو تطبيق مخصص.'),
        ('التحقق المتقدم: ', 'فحص تلقائي للمتطلبات المتزامنة والمقررات المسجلة في الفصل الحالي.'),
    ]
    for prefix, text in future_items:
        pdf.bullet_item(text, prefix)

    # ===== Section 11: Conclusion =====
    pdf.section_title('11', 'الخلاصة')

    pdf.body_text(
        'يُقدم نظام التحقق من أهلية الاعتذار عن المقررات حلاً تقنياً متكاملاً يُساهم في:'
    )
    for prefix, text in [
        ('توفير وقت ', 'المرشدين الأكاديميين ورؤساء الأقسام.'),
        ('ضمان العدالة ', 'في تطبيق الضوابط على جميع الطلبات.'),
        ('تحسين تجربة ', 'الطالب عبر نتائج فورية وشفافة.'),
        ('بناء قاعدة بيانات ', 'مركزية لتاريخ طلبات الاعتذار.'),
        ('دعم اتخاذ القرار ', 'عبر إحصائيات وتقارير مفصلة.'),
    ]:
        pdf.bullet_item(text, prefix)

    pdf.ln(4)
    pdf.body_text(
        'النظام جاهز للنشر والاستخدام الفعلي، ويمكن تطويره وتوسيعه حسب احتياجات الكلية المستقبلية.'
    )

    # Footer
    pdf.ln(10)
    pdf.set_draw_color(*GOLD)
    pdf.set_line_width(0.6)
    pdf.line(60, pdf.get_y(), 150, pdf.get_y())
    pdf.ln(6)
    pdf.set_font('ar', '', 10)
    pdf.set_text_color(*GRAY)
    pdf.cell(0, 6, 'تم إعداد هذا المستند لكلية الحاسبات وتقنية المعلومات — جامعة تبوك', align='C', new_x='LEFT', new_y='NEXT')
    pdf.cell(0, 6, '19 فبراير 2026م  —  الإصدار 1.1', align='C')

    # Output
    output_path = os.path.join(os.path.dirname(__file__), 'whitepaper.pdf')
    pdf.output(output_path)
    print(f'White paper generated: {output_path}')
    return output_path


if __name__ == '__main__':
    generate()
