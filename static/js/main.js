document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('withdrawalForm');
    const fileInput = document.getElementById('transcript');
    const uploadArea = document.getElementById('uploadArea');
    const fileInfo = document.getElementById('fileInfo');
    const fileName = document.getElementById('fileName');
    const removeFile = document.getElementById('removeFile');
    const submitBtn = document.getElementById('submitBtn');
    const btnText = submitBtn.querySelector('.btn-text');
    const btnLoading = submitBtn.querySelector('.btn-loading');
    const resultModal = document.getElementById('resultModal');
    const modalClose = document.getElementById('modalClose');
    const btnCloseModal = document.getElementById('btnCloseModal');

    // File upload handling
    fileInput.addEventListener('change', function () {
        if (this.files.length > 0) {
            showFileInfo(this.files[0]);
        }
    });

    // Drag and drop
    uploadArea.addEventListener('dragover', function (e) {
        e.preventDefault();
        this.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', function () {
        this.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', function (e) {
        e.preventDefault();
        this.classList.remove('dragover');
        if (e.dataTransfer.files.length > 0) {
            const file = e.dataTransfer.files[0];
            if (file.type === 'application/pdf') {
                fileInput.files = e.dataTransfer.files;
                showFileInfo(file);
            } else {
                alert('يرجى رفع ملف بصيغة PDF فقط');
            }
        }
    });

    function showFileInfo(file) {
        fileName.textContent = file.name + ' (' + formatFileSize(file.size) + ')';
        fileInfo.style.display = 'flex';
        uploadArea.style.display = 'none';
    }

    function formatFileSize(bytes) {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
        return (bytes / 1048576).toFixed(1) + ' MB';
    }

    removeFile.addEventListener('click', function () {
        fileInput.value = '';
        fileInfo.style.display = 'none';
        uploadArea.style.display = 'block';
    });

    // Supporting document upload handling
    const supportingInput = document.getElementById('supporting_doc');
    const supportingUploadArea = document.getElementById('supportingUploadArea');
    const supportingFileInfo = document.getElementById('supportingFileInfo');
    const supportingFileName = document.getElementById('supportingFileName');
    const removeSupportingFile = document.getElementById('removeSupportingFile');

    supportingInput.addEventListener('change', function () {
        if (this.files.length > 0) {
            supportingFileName.textContent = this.files[0].name + ' (' + formatFileSize(this.files[0].size) + ')';
            supportingFileInfo.style.display = 'flex';
            supportingUploadArea.style.display = 'none';
        }
    });

    supportingUploadArea.addEventListener('dragover', function (e) {
        e.preventDefault();
        this.classList.add('dragover');
    });

    supportingUploadArea.addEventListener('dragleave', function () {
        this.classList.remove('dragover');
    });

    supportingUploadArea.addEventListener('drop', function (e) {
        e.preventDefault();
        this.classList.remove('dragover');
        if (e.dataTransfer.files.length > 0) {
            const file = e.dataTransfer.files[0];
            if (file.type === 'application/pdf') {
                supportingInput.files = e.dataTransfer.files;
                supportingFileName.textContent = file.name + ' (' + formatFileSize(file.size) + ')';
                supportingFileInfo.style.display = 'flex';
                supportingUploadArea.style.display = 'none';
            } else {
                alert('يرجى رفع ملف بصيغة PDF فقط');
            }
        }
    });

    removeSupportingFile.addEventListener('click', function () {
        supportingInput.value = '';
        supportingFileInfo.style.display = 'none';
        supportingUploadArea.style.display = 'block';
    });

    // Form submission
    form.addEventListener('submit', async function (e) {
        e.preventDefault();

        if (!document.getElementById('acknowledge').checked) {
            alert('يرجى الموافقة على الإقرار والتعهد');
            return;
        }

        // Show loading
        btnText.style.display = 'none';
        btnLoading.style.display = 'inline';
        submitBtn.disabled = true;

        const formData = new FormData(form);

        try {
            const response = await fetch('/validate', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (response.ok) {
                showResults(result);
            } else if (response.status === 409 && result.duplicate) {
                // Duplicate request
                alert(result.error);
            } else {
                alert(result.error || 'حدث خطأ أثناء المعالجة');
            }
        } catch (error) {
            alert('حدث خطأ في الاتصال بالخادم');
            console.error(error);
        } finally {
            btnText.style.display = 'inline';
            btnLoading.style.display = 'none';
            submitBtn.disabled = false;
        }
    });

    function showResults(result) {
        const modalHeader = document.getElementById('modalHeader');
        const modalTitle = document.getElementById('modalTitle');
        const studentInfo = document.getElementById('resultStudentInfo');
        const rulesResults = document.getElementById('rulesResults');
        const errorsDiv = document.getElementById('resultErrors');
        const warningsDiv = document.getElementById('resultWarnings');
        const requestIdBanner = document.getElementById('requestIdBanner');
        const requestIdValue = document.getElementById('requestIdValue');

        // Set header based on eligibility
        if (result.eligible) {
            modalHeader.className = 'modal-header eligible';
            modalTitle.textContent = 'مؤهل للاعتذار عن المقرر';
        } else {
            modalHeader.className = 'modal-header not-eligible';
            modalTitle.textContent = 'غير مؤهل للاعتذار عن المقرر';
        }

        // Show request ID
        if (result.request_id) {
            requestIdBanner.style.display = 'block';
            requestIdValue.textContent = '#' + result.request_id;
        } else {
            requestIdBanner.style.display = 'none';
        }

        // Student info
        const data = result.transcript_data;
        studentInfo.innerHTML = `
            <div class="info-item">
                <span class="info-label">الاسم:</span>
                <span class="info-value">${data.student_name || document.getElementById('student_name').value}</span>
            </div>
            <div class="info-item">
                <span class="info-label">الرقم الجامعي:</span>
                <span class="info-value">${data.student_id || document.getElementById('student_id').value}</span>
            </div>
            <div class="info-item">
                <span class="info-label">الكلية:</span>
                <span class="info-value">كلية الحاسبات وتقنية المعلومات</span>
            </div>
            <div class="info-item">
                <span class="info-label">التخصص:</span>
                <span class="info-value">${data.major || document.getElementById('major').value}</span>
            </div>
            <div class="info-item">
                <span class="info-label">الدرجة:</span>
                <span class="info-value">${data.degree || document.getElementById('degree').value}</span>
            </div>
            <div class="info-item">
                <span class="info-label">المعدل التراكمي:</span>
                <span class="info-value">${data.gpa || 'غير متوفر'}</span>
            </div>
            <div class="info-item">
                <span class="info-label">عدد مرات الاعتذار السابقة:</span>
                <span class="info-value">${data.withdrawal_count}</span>
            </div>
            <div class="info-item">
                <span class="info-label">الساعات المتبقية:</span>
                <span class="info-value">${data.remaining_credits || 'غير متوفر'}</span>
            </div>
            <div class="info-item">
                <span class="info-label">متوقع التخرج:</span>
                <span class="info-value">${data.expected_graduate ? 'نعم' : 'لا'}</span>
            </div>
        `;

        // Rules check
        rulesResults.innerHTML = '<h3 style="margin-bottom: 15px; color: #1a5632; font-size: 1.1rem;">نتائج فحص الضوابط</h3>';
        result.rules_checked.forEach(function (rule) {
            const icon = rule.status === 'pass' ? '\u2713' : rule.status === 'fail' ? '\u2717' : '\u26A0';
            rulesResults.innerHTML += `
                <div class="rule-item ${rule.status}">
                    <div class="rule-icon">${icon}</div>
                    <div class="rule-content">
                        <div class="rule-name">${rule.rule}</div>
                        <div class="rule-detail">${rule.detail}</div>
                    </div>
                </div>
            `;
        });

        // Errors
        if (result.errors && result.errors.length > 0) {
            errorsDiv.style.display = 'block';
            errorsDiv.innerHTML = '<h3>أسباب عدم الأهلية:</h3><ul>' +
                result.errors.map(function (e) { return '<li>' + e + '</li>'; }).join('') +
                '</ul>';
        } else {
            errorsDiv.style.display = 'none';
        }

        // Warnings
        if (result.warnings && result.warnings.length > 0) {
            warningsDiv.style.display = 'block';
            warningsDiv.innerHTML = '<h3>تنبيهات:</h3><ul>' +
                result.warnings.map(function (w) { return '<li>' + w + '</li>'; }).join('') +
                '</ul>';
        } else {
            warningsDiv.style.display = 'none';
        }

        // Show modal
        resultModal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
    }

    // Close modal
    function closeModal() {
        resultModal.style.display = 'none';
        document.body.style.overflow = '';
    }

    modalClose.addEventListener('click', closeModal);
    btnCloseModal.addEventListener('click', closeModal);

    resultModal.addEventListener('click', function (e) {
        if (e.target === resultModal) {
            closeModal();
        }
    });

    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') {
            closeModal();
        }
    });
});
