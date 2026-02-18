document.addEventListener('DOMContentLoaded', function () {
    // ============ Elements ============
    var step1 = document.getElementById('step1');
    var step2 = document.getElementById('step2');
    var parseBtn = document.getElementById('parseBtn');
    var form = document.getElementById('withdrawalForm');
    var resultModal = document.getElementById('resultModal');
    var modalClose = document.getElementById('modalClose');
    var btnCloseModal = document.getElementById('btnCloseModal');

    // Transcript upload (Step 1)
    var fileInput = document.getElementById('transcript');
    var uploadArea = document.getElementById('uploadArea');
    var fileInfo = document.getElementById('fileInfo');
    var fileName = document.getElementById('fileName');
    var removeFile = document.getElementById('removeFile');

    // Supporting doc upload (Step 2)
    var supportingInput = document.getElementById('supporting_doc');
    var supportingUploadArea = document.getElementById('supportingUploadArea');
    var supportingFileInfo = document.getElementById('supportingFileInfo');
    var supportingFileName = document.getElementById('supportingFileName');
    var removeSupportingFile = document.getElementById('removeSupportingFile');

    // ============ Helpers ============
    function formatFileSize(bytes) {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
        return (bytes / 1048576).toFixed(1) + ' MB';
    }

    function showFileSelected(file, nameEl, infoEl, areaEl) {
        nameEl.textContent = file.name + ' (' + formatFileSize(file.size) + ')';
        infoEl.style.display = 'flex';
        areaEl.style.display = 'none';
    }

    function setupUploadArea(inputEl, areaEl, infoEl, nameEl, removeBtn) {
        inputEl.addEventListener('change', function () {
            if (this.files.length > 0) {
                showFileSelected(this.files[0], nameEl, infoEl, areaEl);
            }
        });

        areaEl.addEventListener('dragover', function (e) {
            e.preventDefault();
            this.classList.add('dragover');
        });

        areaEl.addEventListener('dragleave', function () {
            this.classList.remove('dragover');
        });

        areaEl.addEventListener('drop', function (e) {
            e.preventDefault();
            this.classList.remove('dragover');
            if (e.dataTransfer.files.length > 0) {
                var file = e.dataTransfer.files[0];
                if (file.type === 'application/pdf' || file.name.endsWith('.faces')) {
                    inputEl.files = e.dataTransfer.files;
                    showFileSelected(file, nameEl, infoEl, areaEl);
                } else {
                    alert('يرجى رفع ملف بصيغة PDF فقط');
                }
            }
        });

        removeBtn.addEventListener('click', function () {
            inputEl.value = '';
            infoEl.style.display = 'none';
            areaEl.style.display = 'block';
        });
    }

    // ============ Setup upload areas ============
    setupUploadArea(fileInput, uploadArea, fileInfo, fileName, removeFile);
    setupUploadArea(supportingInput, supportingUploadArea, supportingFileInfo, supportingFileName, removeSupportingFile);

    // Enable parse button when file is selected
    fileInput.addEventListener('change', function () {
        parseBtn.disabled = !this.files.length;
    });

    // Also enable on remove (disable)
    removeFile.addEventListener('click', function () {
        parseBtn.disabled = true;
        // Reset step 2 if visible
        step2.style.display = 'none';
        step1.classList.remove('completed');
    });

    // ============ Phase 1: Parse Transcript ============
    parseBtn.addEventListener('click', async function () {
        if (!fileInput.files.length) {
            alert('يرجى رفع السجل الأكاديمي أولاً');
            return;
        }

        var parseBtnText = parseBtn.querySelector('.btn-text');
        var parseBtnLoading = parseBtn.querySelector('.btn-loading');
        parseBtnText.style.display = 'none';
        parseBtnLoading.style.display = 'inline';
        parseBtn.disabled = true;

        var formData = new FormData();
        formData.append('transcript', fileInput.files[0]);

        try {
            var response = await fetch('/parse-transcript', {
                method: 'POST',
                body: formData
            });

            var result = await response.json();

            if (response.ok) {
                populateStep2(result);
                step1.classList.add('completed');
                step2.style.display = 'block';
                step2.scrollIntoView({ behavior: 'smooth' });
            } else {
                alert(result.error || 'حدث خطأ أثناء تحليل السجل');
            }
        } catch (error) {
            alert('حدث خطأ في الاتصال بالخادم');
            console.error(error);
        } finally {
            parseBtnText.style.display = 'inline';
            parseBtnLoading.style.display = 'none';
            parseBtn.disabled = false;
        }
    });

    function populateStep2(data) {
        // Student info card
        var infoGrid = document.getElementById('studentInfoGrid');
        infoGrid.innerHTML =
            '<div class="info-item"><span class="info-label">الاسم:</span><span class="info-value">' + (data.student.name || 'غير متوفر') + '</span></div>' +
            '<div class="info-item"><span class="info-label">الرقم الجامعي:</span><span class="info-value">' + (data.student.id || 'غير متوفر') + '</span></div>' +
            '<div class="info-item"><span class="info-label">الكلية:</span><span class="info-value">' + (data.student.college || 'غير متوفر') + '</span></div>' +
            '<div class="info-item"><span class="info-label">التخصص:</span><span class="info-value">' + (data.student.department || 'غير متوفر') + '</span></div>' +
            '<div class="info-item"><span class="info-label">الدرجة:</span><span class="info-value">' + (data.student.degree || 'غير متوفر') + '</span></div>' +
            '<div class="info-item"><span class="info-label">المعدل التراكمي:</span><span class="info-value">' + (data.student.gpa || 'غير متوفر') + '</span></div>';

        // Semester info
        var semesterInfo = document.getElementById('semesterInfo');
        if (data.current_semester && data.current_year) {
            semesterInfo.textContent = 'الفصل الدراسي الحالي: الفصل ' + data.current_semester + ' - هـ' + data.current_year;
            semesterInfo.style.display = 'block';
        } else {
            semesterInfo.style.display = 'none';
        }

        // Course table
        var tableBody = document.getElementById('courseTableBody');
        tableBody.innerHTML = '';

        data.courses.forEach(function (course) {
            var row = document.createElement('tr');

            row.innerHTML =
                '<td class="radio-cell"><label class="radio-container"><input type="radio" name="selected_course" value="' + course.code + '" required><span class="radio-checkmark"></span></label></td>' +
                '<td class="code-cell">' + course.code + '</td>' +
                '<td class="name-cell">' + course.name + '</td>';

            tableBody.appendChild(row);
        });
    }

    // ============ Phase 2: Form Submit ============
    form.addEventListener('submit', async function (e) {
        e.preventDefault();

        if (!document.getElementById('acknowledge').checked) {
            alert('يرجى الموافقة على الإقرار والتعهد');
            return;
        }

        if (!document.querySelector('input[name="selected_course"]:checked')) {
            alert('يرجى اختيار المقرر المراد الاعتذار عنه');
            return;
        }

        var submitBtn = document.getElementById('submitBtn');
        var btnText = submitBtn.querySelector('.btn-text');
        var btnLoading = submitBtn.querySelector('.btn-loading');

        btnText.style.display = 'none';
        btnLoading.style.display = 'inline';
        submitBtn.disabled = true;

        var formData = new FormData(form);

        try {
            var response = await fetch('/validate', {
                method: 'POST',
                body: formData
            });

            var result = await response.json();

            if (response.ok) {
                showResults(result);
            } else if (response.status === 409 && result.duplicate) {
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

    // ============ Results Modal ============
    function showResults(result) {
        var modalHeader = document.getElementById('modalHeader');
        var modalTitle = document.getElementById('modalTitle');
        var studentInfo = document.getElementById('resultStudentInfo');
        var rulesResults = document.getElementById('rulesResults');
        var errorsDiv = document.getElementById('resultErrors');
        var warningsDiv = document.getElementById('resultWarnings');
        var requestIdBanner = document.getElementById('requestIdBanner');
        var requestIdValue = document.getElementById('requestIdValue');

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

        // Student info summary
        var data = result.transcript_data;
        studentInfo.innerHTML =
            '<div class="info-item"><span class="info-label">الاسم:</span><span class="info-value">' + (data.student_name || 'غير متوفر') + '</span></div>' +
            '<div class="info-item"><span class="info-label">الرقم الجامعي:</span><span class="info-value">' + (data.student_id || 'غير متوفر') + '</span></div>' +
            '<div class="info-item"><span class="info-label">الكلية:</span><span class="info-value">كلية الحاسبات وتقنية المعلومات</span></div>' +
            '<div class="info-item"><span class="info-label">التخصص:</span><span class="info-value">' + (data.department || data.major || 'غير متوفر') + '</span></div>' +
            '<div class="info-item"><span class="info-label">الدرجة:</span><span class="info-value">' + (data.degree || 'غير متوفر') + '</span></div>' +
            '<div class="info-item"><span class="info-label">المعدل التراكمي:</span><span class="info-value">' + (data.gpa || 'غير متوفر') + '</span></div>' +
            '<div class="info-item"><span class="info-label">عدد مرات الاعتذار السابقة:</span><span class="info-value">' + data.withdrawal_count + '</span></div>' +
            '<div class="info-item"><span class="info-label">الساعات المتبقية:</span><span class="info-value">' + (data.remaining_credits || 'غير متوفر') + '</span></div>' +
            '<div class="info-item"><span class="info-label">متوقع التخرج:</span><span class="info-value">' + (data.expected_graduate ? 'نعم' : 'لا') + '</span></div>';

        // Rules check
        rulesResults.innerHTML = '<h3 style="margin-bottom: 15px; color: #1a5632; font-size: 1.1rem;">نتائج فحص الضوابط</h3>';
        result.rules_checked.forEach(function (rule) {
            var icon = rule.status === 'pass' ? '\u2713' : rule.status === 'fail' ? '\u2717' : '\u26A0';
            rulesResults.innerHTML +=
                '<div class="rule-item ' + rule.status + '">' +
                    '<div class="rule-icon">' + icon + '</div>' +
                    '<div class="rule-content">' +
                        '<div class="rule-name">' + rule.rule + '</div>' +
                        '<div class="rule-detail">' + rule.detail + '</div>' +
                    '</div>' +
                '</div>';
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
